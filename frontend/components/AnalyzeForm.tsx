"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Loader2, AtSign } from "lucide-react";
import { api } from "@/lib/api";
import { useI18n } from "./LanguageProvider";

export function AnalyzeForm() {
  const router = useRouter();
  const { t, lang } = useI18n();
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const clean = username.trim().replace(/^@/, "");
    if (!clean) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.analyze(clean, lang);
      router.push(`/analysis/${res.id}`);
    } catch (err: any) {
      setError(err?.message ?? t("form.error"));
      setLoading(false);
    }
  }

  return (
    <motion.form
      onSubmit={submit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="mx-auto w-full max-w-xl"
    >
      <div className="group relative flex items-center gap-2 rounded-2xl border border-white/[0.08] bg-white/[0.03] p-2 shadow-glow backdrop-blur-xl transition focus-within:border-accent/50">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-white/[0.04] text-slate-400">
          <AtSign className="h-5 w-5" />
        </div>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder={t("form.placeholder")}
          className="flex-1 bg-transparent text-base text-white placeholder:text-slate-500 focus:outline-none rtl:text-right"
          autoFocus
          spellCheck={false}
          dir="auto"
        />
        <button
          type="submit"
          disabled={loading || !username.trim()}
          className="inline-flex items-center gap-2 rounded-xl bg-accent-gradient px-5 py-3 text-sm font-semibold text-white shadow-glow transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> {t("form.analyzing")}
            </>
          ) : (
            <>
              {t("form.analyze")} <ArrowRight className="h-4 w-4 rtl:rotate-180" />
            </>
          )}
        </button>
      </div>
      {error && (
        <p className="mt-3 text-center text-sm text-accent-rose">{error}</p>
      )}
      <p className="mt-3 text-center text-xs text-slate-500">{t("form.hint")}</p>
    </motion.form>
  );
}
