"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  DEFAULT_LANG,
  type Lang,
  dirOf,
  translate,
} from "@/lib/i18n";
import { insightText, type RawInsight } from "@/lib/insights";

interface LangCtx {
  lang: Lang;
  dir: "rtl" | "ltr";
  setLang: (l: Lang) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
  ti: (item: RawInsight | string) => string;
}

const Ctx = createContext<LangCtx | null>(null);
const STORAGE_KEY = "tadna_lang";

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(DEFAULT_LANG);

  // Hydrate from localStorage on mount (default stays Persian).
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as Lang | null;
    if (saved === "fa" || saved === "ar" || saved === "en") {
      setLangState(saved);
    }
  }, []);

  // Keep <html dir/lang> in sync so RTL/LTR and fonts switch globally.
  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = dirOf(lang);
  }, [lang]);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    localStorage.setItem(STORAGE_KEY, l);
  }, []);

  const value = useMemo<LangCtx>(
    () => ({
      lang,
      dir: dirOf(lang),
      setLang,
      t: (key, params) => translate(lang, key, params),
      ti: (item) => insightText(lang, item),
    }),
    [lang, setLang]
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useI18n(): LangCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useI18n must be used within LanguageProvider");
  return ctx;
}
