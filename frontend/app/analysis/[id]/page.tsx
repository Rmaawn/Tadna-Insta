"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { AlertTriangle, ArrowLeft, Loader2 } from "lucide-react";
import { Logo } from "@/components/primitives";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useI18n } from "@/components/LanguageProvider";
import { api, type AnalysisDetail } from "@/lib/api";
import { Dashboard } from "@/components/dashboard/Dashboard";

const STAGE_COUNT = 6;

export default function AnalysisPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const { t } = useI18n();
  const [data, setData] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stage, setStage] = useState(0);

  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const d = await api.getAnalysis(id);
        if (!active) return;
        setData(d);
        if (d.status === "pending" || d.status === "running") {
          timer = setTimeout(poll, 1800);
        }
      } catch (e: any) {
        if (active) setError(e?.message ?? t("error.load"));
      }
    }
    poll();
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [id, t]);

  useEffect(() => {
    if (data && (data.status === "pending" || data.status === "running")) {
      const timer = setInterval(
        () => setStage((s) => Math.min(s + 1, STAGE_COUNT - 1)),
        2600
      );
      return () => clearInterval(timer);
    }
  }, [data]);

  const status = data?.status;

  return (
    <main className="mx-auto max-w-6xl px-6 pb-24">
      <header className="flex items-center justify-between py-6">
        <Logo />
        <div className="flex items-center gap-3">
          <LanguageToggle />
          <Link
            href="/"
            className="chip glass-hover inline-flex items-center gap-1.5"
          >
            <ArrowLeft className="h-3.5 w-3.5 rtl:rotate-180" /> {t("nav.new")}
          </Link>
        </div>
      </header>

      {error && <ErrorCard message={error} />}

      {!error && (!data || status === "pending" || status === "running") && (
        <Analyzing username={data?.username} stage={stage} />
      )}

      {status === "failed" && data && (
        <ErrorCard message={data.error ?? ""} username={data.username} />
      )}

      {status === "completed" && data && <Dashboard data={data} />}
    </main>
  );
}

function Analyzing({ username, stage }: { username?: string; stage: number }) {
  const { t } = useI18n();
  const name = username ? `@${username}` : t("analyzing.profile");
  return (
    <div className="grid place-items-center py-32 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative"
      >
        <div className="absolute -inset-10 rounded-full bg-accent/20 blur-3xl" />
        <div className="relative grid h-24 w-24 place-items-center rounded-3xl border border-white/[0.08] bg-white/[0.03] shadow-glow">
          <Loader2 className="h-10 w-10 animate-spin text-accent-glow" />
        </div>
      </motion.div>
      <h1 className="mt-8 text-2xl font-semibold text-white">
        {t("analyzing.title", { name })}
      </h1>
      <motion.p
        key={stage}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-2 text-slate-400"
      >
        {t(`stage.${stage}`)}
      </motion.p>
      <div className="mt-6 flex gap-1.5">
        {Array.from({ length: STAGE_COUNT }).map((_, i) => (
          <span
            key={i}
            className={`h-1.5 w-8 rounded-full transition-colors ${
              i <= stage ? "bg-accent" : "bg-white/10"
            }`}
          />
        ))}
      </div>
    </div>
  );
}

function ErrorCard({
  message,
  username,
}: {
  message: string;
  username?: string;
}) {
  const { t } = useI18n();
  const name = username ? `@${username}` : t("analyzing.profile");
  return (
    <div className="grid place-items-center py-32 text-center">
      <div className="grid h-16 w-16 place-items-center rounded-2xl border border-accent-rose/30 bg-accent-rose/10 text-accent-rose">
        <AlertTriangle className="h-8 w-8" />
      </div>
      <h1 className="mt-6 text-2xl font-semibold text-white">
        {t("error.title", { name })}
      </h1>
      {message && <p className="mt-2 max-w-md text-slate-400">{message}</p>}
      <Link
        href="/"
        className="mt-6 rounded-xl bg-accent-gradient px-5 py-2.5 text-sm font-semibold text-white shadow-glow"
      >
        {t("error.retry")}
      </Link>
    </div>
  );
}
