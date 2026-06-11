"use client";

import { motion } from "framer-motion";
import { LANGS } from "@/lib/i18n";
import { useI18n } from "./LanguageProvider";

/** Segmented three-way language switch: فارسی · العربية · English. */
export function LanguageToggle() {
  const { lang, setLang } = useI18n();

  return (
    <div className="relative flex items-center gap-0.5 rounded-full border border-white/[0.08] bg-white/[0.03] p-1">
      {LANGS.map((l) => {
        const active = lang === l.code;
        return (
          <button
            key={l.code}
            onClick={() => setLang(l.code)}
            className="relative rounded-full px-3 py-1 text-xs font-medium transition-colors"
            aria-pressed={active}
          >
            {active && (
              <motion.span
                layoutId="lang-pill"
                className="absolute inset-0 rounded-full bg-accent-gradient shadow-glow"
                transition={{ type: "spring", stiffness: 380, damping: 30 }}
              />
            )}
            <span
              className={`relative z-10 ${
                active ? "text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {l.native}
            </span>
          </button>
        );
      })}
    </div>
  );
}
