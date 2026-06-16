"use client";

import { motion } from "framer-motion";
import { Brain, CheckCircle2, AlertCircle, Sparkles } from "lucide-react";
import {
  Card,
  ScoreBar,
  ScoreRing,
  SectionTitle,
  scoreLabelKey,
} from "@/components/primitives";
import { useI18n } from "@/components/LanguageProvider";
import { type AnalysisDetail } from "@/lib/api";
import { type RawInsight } from "@/lib/insights";

export function ExecutiveOverview({ data }: { data: AnalysisDetail }) {
  const { t, ti } = useI18n();
  const aiEnabled = data.report?.ai?.available;

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Growth score hero */}
      <Card className="flex flex-col items-center justify-center text-center lg:col-span-1">
        <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">
          {t("ov.growth")}
        </div>
        <div className="my-4">
          <ScoreRing
            score={data.growth_score}
            label={t(`lbl.${scoreLabelKey(data.growth_score)}`)}
          />
        </div>
        <p className="text-sm text-slate-400">{t("ov.growth.sub")}</p>
      </Card>

      {/* Sub scores */}
      <Card delay={0.05} className="lg:col-span-2">
        <SectionTitle
          eyebrow={t("ov.breakdown")}
          title={t("ov.composition")}
          icon={<Sparkles className="h-4 w-4" />}
        />
        <div className="grid gap-5 sm:grid-cols-2">
          <ScoreBar label={t("score.profile")} score={data.profile_score} />
          <ScoreBar label={t("score.brand")} score={data.brand_score} />
          <ScoreBar label={t("score.engagement")} score={data.engagement_score} />
          <ScoreBar label={t("score.visual")} score={data.visual_score} />
        </div>

        <div className="mt-6 grid grid-cols-3 gap-3">
          {keyMetrics(data, t).map((m) => (
            <div
              key={m.label}
              className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 text-center"
            >
              <div className="text-lg font-bold text-white tabular-nums">
                {m.value}
              </div>
              <div className="text-[11px] uppercase tracking-wider text-slate-500">
                {m.label}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* AI summary */}
      <Card delay={0.1} className="lg:col-span-3">
        <SectionTitle
          eyebrow={t("ai.strategist")}
          title={t("ai.summary")}
          icon={<Brain className="h-4 w-4" />}
        />
        {aiEnabled ? (
          <p className="text-pretty text-[15px] leading-relaxed text-slate-200">
            {data.ai_summary}
          </p>
        ) : (
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/[0.06] p-4 text-sm text-amber-200/90">
            {t("ai.disabled")}
          </div>
        )}
      </Card>

      {/* Strengths & weaknesses */}
      <SignalList
        title={t("ov.strengths")}
        icon={<CheckCircle2 className="h-4 w-4 text-accent-lime" />}
        items={strengths(data).map((s) => (typeof s === "string" ? s : ti(s)))}
        tone="lime"
        delay={0.12}
        empty={t("list.empty")}
      />
      <SignalList
        title={t("ov.weaknesses")}
        icon={<AlertCircle className="h-4 w-4 text-accent-rose" />}
        items={weaknesses(data).map((s) => (typeof s === "string" ? s : ti(s)))}
        tone="rose"
        delay={0.16}
        className="lg:col-span-2"
        empty={t("list.empty")}
      />
    </div>
  );
}

function SignalList({
  title,
  icon,
  items,
  tone,
  delay,
  empty,
  className = "",
}: {
  title: string;
  icon: React.ReactNode;
  items: string[];
  tone: "lime" | "rose";
  delay: number;
  empty: string;
  className?: string;
}) {
  const dot = tone === "lime" ? "bg-accent-lime" : "bg-accent-rose";
  return (
    <Card delay={delay} className={className}>
      <SectionTitle title={title} icon={icon} />
      <ul className="space-y-2.5">
        {items.length === 0 && (
          <li className="text-sm text-slate-500">{empty}</li>
        )}
        {items.map((s, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: delay + i * 0.05 }}
            className="flex items-start gap-2.5 text-sm leading-relaxed text-slate-300"
          >
            <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${dot}`} />
            {s}
          </motion.li>
        ))}
      </ul>
    </Card>
  );
}

// --- data helpers: prefer AI output, fall back to deterministic insights ---
// The fallback splits insights by polarity (tone) so strengths and weaknesses
// are genuinely different lists — never the same items shown twice.
function strengths(d: AnalysisDetail): (string | RawInsight)[] {
  if (d.strengths?.length) return d.strengths;
  return collectInsights(d)
    .filter((i) => i.tone === "good")
    .slice(0, 5);
}
function weaknesses(d: AnalysisDetail): (string | RawInsight)[] {
  if (d.weaknesses?.length) return d.weaknesses;
  return collectInsights(d)
    .filter((i) => i.tone !== "good")
    .slice(0, 5);
}
function collectInsights(d: AnalysisDetail): RawInsight[] {
  const r = d.report ?? {};
  return ["profile", "content", "engagement", "visual"].flatMap(
    (k) => r[k]?.insights ?? []
  );
}

function keyMetrics(d: AnalysisDetail, t: (k: string) => string) {
  const e = d.report?.engagement?.metrics ?? {};
  const c = d.report?.content?.metrics ?? {};
  const trend = e.trend_direction
    ? t(`trend.${e.trend_direction}`)
    : t("trend.unknown");
  return [
    { label: t("metric.avgER"), value: e.avg_engagement_rate != null ? `${e.avg_engagement_rate}%` : "—" },
    { label: t("metric.postsWk"), value: c.avg_gap_days ? (7 / c.avg_gap_days).toFixed(1) : "—" },
    { label: t("metric.trend"), value: trend },
  ];
}
