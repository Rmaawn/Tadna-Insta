"use client";

import {
  Area,
  AreaChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { BarChart3, CalendarClock, Images } from "lucide-react";
import { Card, SectionTitle } from "@/components/primitives";
import { useI18n } from "@/components/LanguageProvider";
import { type AnalysisDetail } from "@/lib/api";
import { Heatmap } from "./Heatmap";

const TYPE_COLORS = ["#7c5cff", "#22d3ee", "#fb7185"];

export function ContentAnalytics({ data }: { data: AnalysisDetail }) {
  const { t } = useI18n();
  const content = data.report?.content ?? {};
  const eng = data.report?.engagement ?? {};
  const dist = content.details?.type_distribution ?? {};
  const cadence = content.details?.cadence ?? {};
  const heatmap = content.details?.heatmap ?? [];
  const weekdays = content.details?.weekdays ?? [];
  const trend = (eng.details?.trend ?? []).map((t: any, i: number) => ({
    i: i + 1,
    er: t.engagement_rate,
    date: t.date ? new Date(t.date).toLocaleDateString() : `#${i + 1}`,
  }));

  const typeData = [
    { name: t("type.images"), value: dist.image ?? 0 },
    { name: t("type.carousels"), value: dist.carousel ?? 0 },
    { name: t("type.reels"), value: dist.video ?? 0 },
  ].filter((d) => d.value > 0);

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Engagement trend */}
      <Card className="lg:col-span-2">
        <SectionTitle
          eyebrow={t("content.eyebrow.eng")}
          title={t("content.engTitle")}
          icon={<BarChart3 className="h-4 w-4" />}
        />
        {trend.length > 1 ? (
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={trend} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <defs>
                <linearGradient id="erFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7c5cff" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#7c5cff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="i" stroke="#475569" fontSize={11} tickLine={false} />
              <YAxis stroke="#475569" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={(_, p: any) => p?.[0]?.payload?.date ?? ""}
                formatter={(v: any) => [`${v}%`, "ER"]}
              />
              <Area
                type="monotone"
                dataKey="er"
                stroke="#9d7bff"
                strokeWidth={2.5}
                fill="url(#erFill)"
                dot={{ r: 3, fill: "#9d7bff" }}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <Empty />
        )}
      </Card>

      {/* Content mix donut */}
      <Card delay={0.05}>
        <SectionTitle
          eyebrow={t("content.eyebrow.mix")}
          title={t("content.types")}
          icon={<Images className="h-4 w-4" />}
        />
        {typeData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie
                  data={typeData}
                  dataKey="value"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  stroke="none"
                >
                  {typeData.map((_, i) => (
                    <Cell key={i} fill={TYPE_COLORS[i % TYPE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 flex justify-center gap-4 text-xs">
              {typeData.map((d, i) => (
                <span key={d.name} className="flex items-center gap-1.5 text-slate-400">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ background: TYPE_COLORS[i % TYPE_COLORS.length] }}
                  />
                  {d.name} {d.value}
                </span>
              ))}
            </div>
          </>
        ) : (
          <Empty />
        )}
      </Card>

      {/* Cadence stats */}
      <Card delay={0.1} className="lg:col-span-3">
        <SectionTitle
          eyebrow={t("content.eyebrow.consistency")}
          title={t("content.cadence")}
          icon={<CalendarClock className="h-4 w-4" />}
        />
        <div className="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label={t("stat.avgGap")} value={cadence.avg_gap_days != null ? `${cadence.avg_gap_days}d` : "—"} />
          <Stat label={t("stat.postsWeek")} value={cadence.posts_per_week ?? "—"} />
          <Stat label={t("stat.regularity")} value={t(`cons.${cadence.consistency_label ?? "unknown"}`)} />
          <Stat label={t("stat.bestWindow")} value={content.metrics?.best_slot ?? "—"} />
        </div>
        {heatmap.length > 0 ? (
          <Heatmap matrix={heatmap} weekdays={weekdays} />
        ) : (
          <Empty />
        )}
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: any }) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
      <div className="text-base font-semibold text-white">{value}</div>
      <div className="text-[11px] uppercase tracking-wider text-slate-500">
        {label}
      </div>
    </div>
  );
}

function Empty() {
  const { t } = useI18n();
  return (
    <div className="grid h-32 place-items-center text-sm text-slate-600">
      {t("chart.empty")}
    </div>
  );
}

const tooltipStyle = {
  background: "#0e111b",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 12,
  fontSize: 12,
  color: "#e2e8f0",
};

function cap(s?: string) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : "—";
}
