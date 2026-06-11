"use client";

import { motion } from "framer-motion";
import { Palette, Sparkles, Type, Smile } from "lucide-react";
import {
  Card,
  ScoreRing,
  SectionTitle,
  scoreLabelKey,
} from "@/components/primitives";
import { useI18n } from "@/components/LanguageProvider";
import { type AnalysisDetail } from "@/lib/api";

export function VisualIdentity({ data }: { data: AnalysisDetail }) {
  const { t, ti } = useI18n();
  const visual = data.report?.visual ?? {};
  const metrics = visual.metrics ?? {};
  const palette: { hex: string; weight: number }[] = visual.details?.palette ?? [];
  const analyzed = metrics.thumbnails_analyzed ?? 0;

  if (!analyzed) {
    return (
      <Card>
        <SectionTitle title={t("score.visual")} icon={<Palette className="h-4 w-4" />} />
        <p className="text-sm text-slate-400">{t("vis.none")}</p>
      </Card>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card className="flex flex-col items-center justify-center text-center">
        <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">
          {t("vis.score")}
        </div>
        <div className="my-4">
          <ScoreRing
            score={data.visual_score}
            label={t(`lbl.${scoreLabelKey(data.visual_score)}`)}
            size={160}
          />
        </div>
        <p className="text-sm text-slate-400">{t("vis.basedOn", { n: analyzed })}</p>
      </Card>

      <Card delay={0.05} className="lg:col-span-2">
        <SectionTitle
          eyebrow={t("vis.eyebrow.palette")}
          title={t("vis.palette")}
          icon={<Palette className="h-4 w-4" />}
        />
        <div className="flex h-28 overflow-hidden rounded-xl border border-white/[0.06]">
          {palette.map((c, i) => (
            <motion.div
              key={c.hex + i}
              initial={{ flexGrow: 0 }}
              animate={{ flexGrow: c.weight }}
              transition={{ duration: 0.8, delay: i * 0.06 }}
              style={{ background: c.hex, flexBasis: 0 }}
              className="group relative"
            >
              <span className="absolute inset-x-0 bottom-1 text-center text-[9px] font-medium uppercase text-white/70 opacity-0 transition group-hover:opacity-100">
                {c.hex}
              </span>
            </motion.div>
          ))}
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Metric
            icon={<Sparkles className="h-4 w-4" />}
            label={t("vis.consistency")}
            value={metrics.consistency_score != null ? Math.round(metrics.consistency_score) : "—"}
          />
          <Metric
            icon={<Palette className="h-4 w-4" />}
            label={t("vis.brightness")}
            value={metrics.avg_brightness != null ? Math.round(metrics.avg_brightness) : "—"}
          />
          <Metric
            icon={<Type className="h-4 w-4" />}
            label={t("vis.textHeavy")}
            value={metrics.text_heavy_ratio != null ? `${Math.round(metrics.text_heavy_ratio * 100)}%` : "—"}
          />
          <Metric
            icon={<Smile className="h-4 w-4" />}
            label={t("vis.faces")}
            value={
              metrics.face_ratio != null
                ? `${Math.round(metrics.face_ratio * 100)}%`
                : metrics.face_detection === "unavailable"
                ? "n/a"
                : "0%"
            }
          />
        </div>
      </Card>

      <Card delay={0.1} className="lg:col-span-3">
        <SectionTitle eyebrow={t("vis.eyebrow.findings")} title={t("vis.insights")} />
        <ul className="space-y-2.5">
          {(visual.insights ?? []).map((s: any, i: number) => (
            <li
              key={i}
              className="flex items-start gap-2.5 text-sm leading-relaxed text-slate-300"
            >
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent-cyan" />
              {ti(s)}
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: any;
}) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
      <div className="mb-1 text-accent-glow">{icon}</div>
      <div className="text-lg font-bold text-white tabular-nums">{value}</div>
      <div className="text-[11px] uppercase tracking-wider text-slate-500">
        {label}
      </div>
    </div>
  );
}
