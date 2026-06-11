"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  BadgeCheck,
  BarChart3,
  Brain,
  LayoutGrid,
  Palette,
  Users,
} from "lucide-react";
import { type AnalysisDetail } from "@/lib/api";
import { useI18n } from "@/components/LanguageProvider";
import { ExecutiveOverview } from "./ExecutiveOverview";
import { ContentAnalytics } from "./ContentAnalytics";
import { VisualIdentity } from "./VisualIdentity";
import { Recommendations } from "./Recommendations";
import { TopPosts } from "./TopPosts";

const TABS = [
  { id: "overview", key: "tab.overview", icon: LayoutGrid },
  { id: "content", key: "tab.content", icon: BarChart3 },
  { id: "visual", key: "tab.visual", icon: Palette },
  { id: "ai", key: "tab.ai", icon: Brain },
];

export function Dashboard({ data }: { data: AnalysisDetail }) {
  const { t } = useI18n();
  const [tab, setTab] = useState("overview");
  const profileMetrics = data.report?.profile?.metrics ?? {};

  return (
    <div>
      {/* Account header */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass mb-6 flex flex-wrap items-center justify-between gap-4 p-5"
      >
        <div className="flex items-center gap-4">
          <div className="grid h-14 w-14 place-items-center rounded-2xl bg-accent-gradient text-xl font-bold text-white shadow-glow">
            {data.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-semibold text-white" dir="ltr">
                @{data.username}
              </h1>
              {profileMetrics.is_verified && (
                <BadgeCheck className="h-5 w-5 text-accent-cyan" />
              )}
            </div>
            <div className="mt-0.5 flex flex-wrap items-center gap-3 text-sm text-slate-400">
              <span className="inline-flex items-center gap-1">
                <Users className="h-3.5 w-3.5" />
                {fmt(profileMetrics.followers)} {t("acc.followers")}
              </span>
              {profileMetrics.niche && (
                <span className="chip">{profileMetrics.niche}</span>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {TABS.map((item) => {
            const active = tab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id)}
                className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition ${
                  active
                    ? "bg-accent-gradient text-white shadow-glow"
                    : "border border-white/[0.08] bg-white/[0.02] text-slate-300 hover:bg-white/[0.05]"
                }`}
              >
                <item.icon className="h-4 w-4" /> {t(item.key)}
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Panels */}
      {tab === "overview" && <ExecutiveOverview data={data} />}
      {tab === "content" && (
        <>
          <ContentAnalytics data={data} />
          <TopPosts data={data} />
        </>
      )}
      {tab === "visual" && <VisualIdentity data={data} />}
      {tab === "ai" && <Recommendations data={data} />}
    </div>
  );
}

function fmt(n?: number): string {
  if (n == null) return "—";
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}
