"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Brain,
  Palette,
  TrendingUp,
  UserCheck,
  Clock,
  ChevronRight,
} from "lucide-react";
import { Logo, scoreColor } from "@/components/primitives";
import { AnalyzeForm } from "@/components/AnalyzeForm";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useI18n } from "@/components/LanguageProvider";
import { api, type AnalysisSummary } from "@/lib/api";

const FEATURES = [
  { icon: UserCheck, key: "profile" },
  { icon: TrendingUp, key: "engagement" },
  { icon: Palette, key: "visual" },
  { icon: Brain, key: "ai" },
];

export default function Home() {
  const { t } = useI18n();
  const [recent, setRecent] = useState<AnalysisSummary[]>([]);

  useEffect(() => {
    api.listAnalyses().then(setRecent).catch(() => {});
  }, []);

  return (
    <main className="relative mx-auto max-w-6xl px-6 pb-24">
      <header className="flex items-center justify-between py-6">
        <Logo />
        <div className="flex items-center gap-3">
          <LanguageToggle />
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            className="chip glass-hover hidden sm:inline-flex"
          >
            {t("nav.api")}
          </a>
        </div>
      </header>

      {/* Hero */}
      <section className="relative pt-16 text-center sm:pt-24">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.03] px-4 py-1.5 text-xs text-slate-300"
        >
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent-lime" />
          {t("hero.badge")}
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.05 }}
          className="mx-auto max-w-3xl text-balance text-4xl font-bold leading-[1.15] tracking-tight text-white sm:text-6xl sm:leading-[1.05]"
        >
          {t("hero.title1")} <span className="gradient-text">{t("hero.titleHi")}</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mx-auto mt-5 max-w-xl text-pretty text-base text-slate-400 sm:text-lg"
        >
          {t("hero.subtitle")}
        </motion.p>

        <div className="mt-10">
          <AnalyzeForm />
        </div>
      </section>

      {/* Features */}
      <section className="mt-24 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.key}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 + i * 0.08 }}
            className="glass glass-hover p-5"
          >
            <div className="mb-4 grid h-10 w-10 place-items-center rounded-xl border border-white/[0.08] bg-white/[0.03] text-accent-glow">
              <f.icon className="h-5 w-5" />
            </div>
            <h3 className="text-sm font-semibold text-white">{t(`feat.${f.key}.t`)}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-slate-400">
              {t(`feat.${f.key}.d`)}
            </p>
          </motion.div>
        ))}
      </section>

      {/* Recent analyses */}
      {recent.length > 0 && (
        <section className="mt-20">
          <div className="mb-4 flex items-center gap-2 text-sm text-slate-400">
            <Clock className="h-4 w-4" /> {t("recent.title")}
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {recent.slice(0, 6).map((a) => (
              <Link
                key={a.id}
                href={`/analysis/${a.id}`}
                className="glass glass-hover flex items-center justify-between p-4"
              >
                <div>
                  <div className="font-medium text-white" dir="ltr">@{a.username}</div>
                  <div className="text-xs text-slate-500">
                    {t(`status.${a.status}`)}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {a.growth_score != null && (
                    <span
                      className="text-lg font-bold tabular-nums"
                      style={{ color: scoreColor(a.growth_score) }}
                    >
                      {Math.round(a.growth_score)}
                    </span>
                  )}
                  <ChevronRight className="h-4 w-4 text-slate-600 rtl:rotate-180" />
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
