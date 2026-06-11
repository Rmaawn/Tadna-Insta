"use client";

import { Heart, MessageCircle, TrendingDown, TrendingUp } from "lucide-react";
import { Card, SectionTitle } from "@/components/primitives";
import { useI18n } from "@/components/LanguageProvider";
import { type AnalysisDetail } from "@/lib/api";

export function TopPosts({ data }: { data: AnalysisDetail }) {
  const { t } = useI18n();
  const eng = data.report?.engagement?.details ?? {};
  const top = eng.top_posts ?? [];
  const weak = eng.weak_posts ?? [];

  if (top.length === 0) return null;

  return (
    <div className="mt-6 grid gap-6 lg:grid-cols-2">
      <Card>
        <SectionTitle
          eyebrow={t("posts.eyebrow")}
          title={t("posts.top")}
          icon={<TrendingUp className="h-4 w-4 text-accent-lime" />}
        />
        <div className="grid grid-cols-3 gap-3">
          {top.map((p: any) => (
            <PostTile key={p.shortcode} post={p} accent="#a3e635" noimg={t("posts.noimg")} />
          ))}
        </div>
      </Card>

      <Card delay={0.05}>
        <SectionTitle
          eyebrow={t("posts.eyebrow")}
          title={t("posts.weak")}
          icon={<TrendingDown className="h-4 w-4 text-accent-rose" />}
        />
        <div className="grid grid-cols-3 gap-3">
          {weak.map((p: any) => (
            <PostTile key={p.shortcode} post={p} accent="#fb7185" noimg={t("posts.noimg")} />
          ))}
        </div>
      </Card>
    </div>
  );
}

function PostTile({ post, accent, noimg }: { post: any; accent: string; noimg: string }) {
  return (
    <a
      href={post.permalink}
      target="_blank"
      rel="noreferrer"
      className="group relative block overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.02]"
    >
      <div className="aspect-square w-full overflow-hidden bg-ink-800">
        {post.thumbnail_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={post.thumbnail_url}
            alt={post.shortcode}
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
            referrerPolicy="no-referrer"
          />
        ) : (
          <div className="grid h-full place-items-center text-xs text-slate-600">
            {noimg}
          </div>
        )}
      </div>
      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/85 to-transparent p-2">
        <div
          className="text-xs font-bold tabular-nums"
          style={{ color: accent }}
        >
          {post.engagement_rate}% ER
        </div>
        <div className="mt-0.5 flex items-center gap-2 text-[10px] text-slate-300">
          <span className="flex items-center gap-0.5">
            <Heart className="h-3 w-3" /> {fmt(post.likes)}
          </span>
          <span className="flex items-center gap-0.5">
            <MessageCircle className="h-3 w-3" /> {fmt(post.comments)}
          </span>
        </div>
      </div>
    </a>
  );
}

function fmt(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}
