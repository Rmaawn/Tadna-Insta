"""Visual identity analyzer.

Operates on post **thumbnails only** (no video processing). For each image it
extracts the dominant colors, brightness and a "busy/text-heavy" estimate via
edge density, then aggregates these into a Visual Identity Score and an
Aesthetic Consistency Score.

Face presence is detected opportunistically: if OpenCV is installed it runs a
Haar-cascade pass, otherwise the field is reported as ``null`` and the rest of
the analysis proceeds unaffected. This keeps the base install light while
leaving a clean hook for the (future) deeper visual analyzer.
"""

from __future__ import annotations

import io
import logging
from collections import Counter
from typing import Any

import numpy as np
from PIL import Image

from app.analyzers.base import AnalyzerResult, BaseAnalyzer, clamp, ins, scale
from app.schemas.schemas import FetchedProfile

logger = logging.getLogger(__name__)

try:  # optional, only used if available
    import cv2  # type: ignore

    _FACE_CASCADE = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    _CV2_OK = not _FACE_CASCADE.empty()
except Exception:  # noqa: BLE001
    _CV2_OK = False


class VisualAnalyzer(BaseAnalyzer):
    key = "visual"
    title = "Visual Identity"

    def analyze(
        self, profile: FetchedProfile, context: dict[str, Any]
    ) -> AnalyzerResult:
        signals: dict[str, dict] = context.setdefault("post_signals", {})
        analyzed = []

        for p in profile.posts:
            if not p.image_bytes:
                continue
            data = self._analyze_image(p.image_bytes)
            if data is None:
                continue
            analyzed.append(data)
            sig = signals.setdefault(p.shortcode, {})
            sig.update(
                {
                    "dominant_color": data["dominant_hex"],
                    "brightness": data["brightness"],
                    "text_heavy": data["text_heavy"],
                    "has_face": data["has_face"],
                }
            )

        if not analyzed:
            return AnalyzerResult(
                key=self.key, title=self.title, score=None,
                insights=[ins("visual.no_thumbnails", "No thumbnails could be downloaded for visual analysis.")],
                metrics={"thumbnails_analyzed": 0},
            )

        palette = self._aggregate_palette(analyzed)
        consistency = self._color_consistency(analyzed)
        brightness = float(np.mean([a["brightness"] for a in analyzed]))
        text_heavy_ratio = np.mean([a["text_heavy"] for a in analyzed])
        face_vals = [a["has_face"] for a in analyzed if a["has_face"] is not None]
        face_ratio = (sum(face_vals) / len(face_vals)) if face_vals else None

        # Visual identity rewards consistency and balanced (not blown-out) light.
        brightness_balance = 100 - abs(brightness - 128) / 128 * 100
        visual_score = clamp(0.60 * consistency + 0.25 * brightness_balance + 0.15 * (100 - text_heavy_ratio * 100))
        context["visual_score"] = visual_score

        insights: list[dict] = []
        if consistency < 45:
            insights.append(ins("visual.scattered", "Thumbnails lack a consistent color identity — the grid looks scattered."))
        elif consistency > 75:
            insights.append(ins("visual.strong_palette", "Strong, consistent color palette — your grid has a recognizable identity."))
        if text_heavy_ratio > 0.5:
            insights.append(ins("visual.text_heavy", "Most thumbnails are text-heavy; cleaner visuals usually read better in-feed."))
        if face_ratio is not None and face_ratio >= 0.4:
            insights.append(ins("visual.faces_common", "Posts featuring faces are common — these tend to outperform on engagement."))
        elif face_ratio == 0:
            insights.append(ins("visual.no_faces", "No faces detected in thumbnails; human faces typically lift engagement."))
        if brightness < 60:
            insights.append(ins("visual.dark", "Imagery skews dark — consider brighter, higher-contrast visuals."))
        if not insights:
            insights.append(ins("visual.coherent", "Visual identity is coherent; keep the palette and composition consistent."))

        return AnalyzerResult(
            key=self.key,
            title=self.title,
            score=visual_score,
            metrics={
                "thumbnails_analyzed": len(analyzed),
                "consistency_score": round(consistency, 1),
                "avg_brightness": round(brightness, 1),
                "text_heavy_ratio": round(float(text_heavy_ratio), 2),
                "face_ratio": round(face_ratio, 2) if face_ratio is not None else None,
                "face_detection": "enabled" if _CV2_OK else "unavailable",
            },
            insights=insights,
            details={"palette": palette},
        )

    # ------------------------------------------------------------------ #
    def _analyze_image(self, raw: bytes) -> dict[str, Any] | None:
        try:
            img = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception as exc:  # noqa: BLE001
            logger.debug("Unreadable thumbnail: %s", exc)
            return None

        small = img.resize((128, 128))
        arr = np.asarray(small, dtype=np.float32)

        # Dominant color via palette quantization.
        quant = small.quantize(colors=5, method=Image.Quantize.FASTOCTREE)
        pal = quant.getpalette()
        counts = Counter(quant.getdata())
        dominant_idx = counts.most_common(1)[0][0]
        r, g, b = pal[dominant_idx * 3 : dominant_idx * 3 + 3]
        top_colors = [
            self._rgb_hex(pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2])
            for i, _ in counts.most_common(3)
        ]

        brightness = float(arr.mean())

        # Edge density as a proxy for "busy / text-heavy".
        gray = arr.mean(axis=2)
        gx = np.abs(np.diff(gray, axis=1)).mean()
        gy = np.abs(np.diff(gray, axis=0)).mean()
        edge_density = (gx + gy) / 2.0
        text_heavy = edge_density > 18.0  # empirical threshold

        has_face = self._detect_face(np.asarray(img.resize((256, 256)))) if _CV2_OK else None

        return {
            "dominant_rgb": (r, g, b),
            "dominant_hex": self._rgb_hex(r, g, b),
            "top_colors": top_colors,
            "brightness": round(brightness, 1),
            "edge_density": round(float(edge_density), 2),
            "text_heavy": bool(text_heavy),
            "has_face": has_face,
        }

    @staticmethod
    def _detect_face(arr: np.ndarray) -> bool:
        try:
            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
            faces = _FACE_CASCADE.detectMultiScale(gray, 1.1, 5)
            return len(faces) > 0
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def _aggregate_palette(analyzed: list[dict]) -> list[dict[str, Any]]:
        counter: Counter = Counter()
        for a in analyzed:
            for hex_color in a["top_colors"]:
                counter[hex_color] += 1
        total = sum(counter.values()) or 1
        return [
            {"hex": hex_color, "weight": round(count / total, 3)}
            for hex_color, count in counter.most_common(6)
        ]

    @staticmethod
    def _color_consistency(analyzed: list[dict]) -> float:
        colors = np.array([a["dominant_rgb"] for a in analyzed], dtype=np.float32)
        if len(colors) < 2:
            return 60.0
        # Mean distance of each dominant color to the palette centroid.
        centroid = colors.mean(axis=0)
        dists = np.linalg.norm(colors - centroid, axis=1)
        avg_dist = float(dists.mean())  # 0 (identical) .. ~220 (very varied)
        return clamp(100 - scale(min(avg_dist, 160), 0, 160))

    @staticmethod
    def _rgb_hex(r: int, g: int, b: int) -> str:
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
