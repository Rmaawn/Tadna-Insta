"use client";

import { motion } from "framer-motion";
import { Brain, Zap } from "lucide-react";
import { Card, SectionTitle } from "@/components/primitives";
import { useI18n } from "@/components/LanguageProvider";
import { type AnalysisDetail, type Recommendation } from "@/lib/api";

const PRIORITY_STYLE = {
  high: { color: "#fb7185", bg: "rgba(251,113,133,0.12)" },
  medium: { color: "#22d3ee", bg: "rgba(34,211,238,0.1)" },
  low: { color: "#94a3b8", bg: "rgba(148,163,184,0.1)" },
} as const;

const CATS = ["Profile", "Content", "Engagement", "Visual", "Strategy"];

export function Recommendations({ data }: { data: AnalysisDetail }) {
  const { t } = useI18n();
  const recs: Recommendation[] = data.recommendations ?? [];
  const aiEnabled = data.report?.ai?.available;

  if (!aiEnabled || recs.length === 0) {
    return (
      <Card>
        <SectionTitle
          eyebrow={t("ai.strategist")}
          title={t("rec.title")}
          icon={<Brain className="h-4 w-4" />}
        />
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/[0.06] p-5 text-sm text-amber-200/90">
          {t("rec.disabled")}
        </div>
      </Card>
    );
  }

  return (
    <div>
      <Card className="mb-6">
        <SectionTitle
          eyebrow={t("ai.strategist")}
          title={t("rec.summary")}
          icon={<Brain className="h-4 w-4" />}
        />
        <p className="text-pretty text-[15px] leading-relaxed text-slate-200">
          {data.ai_summary}
        </p>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        {recs.map((r, i) => {
          const p = PRIORITY_STYLE[r.priority] ?? PRIORITY_STYLE.medium;
          const cat = CATS.includes(r.category) ? t(`cat.${r.category}`) : r.category;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06, duration: 0.5 }}
              className="glass glass-hover relative overflow-hidden p-5"
            >
              <div
                className="absolute top-0 h-full w-1 ltr:left-0 rtl:right-0"
                style={{ background: p.color }}
              />
              <div className="mb-3 flex items-center justify-between gap-3">
                <span className="chip">{cat}</span>
                <span
                  className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold"
                  style={{ color: p.color, background: p.bg }}
                >
                  <Zap className="h-3 w-3" /> {t(`prio.${r.priority}`)}
                </span>
              </div>
              <h3 className="text-base font-semibold text-white">{r.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-300">
                {r.detail}
              </p>
              {r.impact && (
                <p className="mt-3 border-t border-white/[0.06] pt-3 text-xs text-slate-400">
                  <span className="font-medium text-accent-glow">{t("rec.impact")} · </span>
                  {r.impact}
                </p>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
