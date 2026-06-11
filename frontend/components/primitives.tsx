"use client";

import { motion } from "framer-motion";
import { useI18n } from "./LanguageProvider";

/**
 * Minimal brand mark: three ascending rounded bars (growth analytics) topped
 * with a spark dot (the AI signal). Clean, geometric, on-theme.
 */
export function BrandMark({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" fill="none" className={className} aria-hidden>
      <rect x="5" y="18" width="4.4" height="9" rx="2.2" fill="white" fillOpacity="0.85" />
      <rect x="13.8" y="12.5" width="4.4" height="14.5" rx="2.2" fill="white" fillOpacity="0.95" />
      <rect x="22.6" y="7" width="4.4" height="20" rx="2.2" fill="white" />
      <circle cx="24.8" cy="3.7" r="2.4" fill="white" />
    </svg>
  );
}

export function Logo({ className = "" }: { className?: string }) {
  const { t } = useI18n();
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <div className="relative grid h-9 w-9 place-items-center rounded-xl bg-accent-gradient shadow-glow">
        <BrandMark />
      </div>
      <div className="leading-tight">
        <div
          className="text-sm font-semibold tracking-tight text-white rtl:text-right"
          dir="ltr"
        >
          Tadna<span className="gradient-text"> Insta</span>
        </div>
        <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500 rtl:text-right">
          {t("brand.tag")}
        </div>
      </div>
    </div>
  );
}

export function scoreColor(score: number | null | undefined): string {
  if (score == null) return "#64748b";
  if (score >= 75) return "#a3e635";
  if (score >= 55) return "#22d3ee";
  if (score >= 40) return "#7c5cff";
  return "#fb7185";
}

/** Returns the i18n label key suffix for a score (translate via `lbl.<key>`). */
export function scoreLabelKey(score: number | null | undefined): string {
  if (score == null) return "NA";
  if (score >= 80) return "Elite";
  if (score >= 65) return "Strong";
  if (score >= 50) return "Average";
  if (score >= 35) return "Weak";
  return "Critical";
}

/** Animated circular score gauge. */
export function ScoreRing({
  score,
  size = 180,
  stroke = 12,
  label,
}: {
  score: number | null;
  size?: number;
  stroke?: number;
  label?: string;
}) {
  const value = score ?? 0;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const color = scoreColor(score);
  const id = `grad-${Math.round(value)}-${size}`;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <defs>
          <linearGradient id={id} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={color} />
            <stop offset="100%" stopColor="#7c5cff" />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={stroke}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={`url(#${id})`}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - (circ * value) / 100 }}
          transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
          style={{ filter: `drop-shadow(0 0 8px ${color}66)` }}
        />
      </svg>
      <div className="absolute inset-0 grid place-items-center text-center">
        <div>
          <div className="text-4xl font-bold text-white tabular-nums">
            {score == null ? "—" : Math.round(value)}
          </div>
          {label && (
            <div className="mt-0.5 text-[11px] uppercase tracking-widest text-slate-400">
              {label}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/** Small horizontal score meter for sub-scores. */
export function ScoreBar({
  label,
  score,
}: {
  label: string;
  score: number | null;
}) {
  const color = scoreColor(score);
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="font-semibold tabular-nums text-white">
          {score == null ? "—" : Math.round(score)}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
        <motion.div
          className="h-full rounded-full"
          style={{ background: color, boxShadow: `0 0 12px ${color}88` }}
          initial={{ width: 0 }}
          animate={{ width: `${score ?? 0}%` }}
          transition={{ duration: 1.1, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

export function Card({
  children,
  className = "",
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      className={`glass glass-hover p-5 ${className}`}
    >
      {children}
    </motion.div>
  );
}

export function SectionTitle({
  eyebrow,
  title,
  icon,
}: {
  eyebrow?: string;
  title: string;
  icon?: React.ReactNode;
}) {
  return (
    <div className="mb-4 flex items-center gap-3">
      {icon && (
        <div className="grid h-9 w-9 place-items-center rounded-lg border border-white/[0.08] bg-white/[0.03] text-accent-glow">
          {icon}
        </div>
      )}
      <div>
        {eyebrow && (
          <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">
            {eyebrow}
          </div>
        )}
        <h2 className="text-lg font-semibold text-white">{title}</h2>
      </div>
    </div>
  );
}
