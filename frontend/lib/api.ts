// Thin client for the Tadna Insta backend.
// Requests go through Next's rewrite (/api/* -> backend) so there are no CORS
// or base-URL concerns in the browser.

export type AnalysisStatus = "pending" | "running" | "completed" | "failed";

export interface AnalysisSummary {
  id: string;
  username: string;
  status: AnalysisStatus;
  growth_score: number | null;
  brand_score: number | null;
  engagement_score: number | null;
  visual_score: number | null;
  profile_score: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface Recommendation {
  title: string;
  category: string;
  priority: "high" | "medium" | "low";
  impact: string;
  detail: string;
}

export interface PostOut {
  id: string;
  shortcode: string;
  caption: string | null;
  media_type: string;
  thumbnail_url: string | null;
  permalink: string | null;
  likes: number;
  comments: number;
  video_views: number;
  engagement_rate: number;
  posted_at: string | null;
  signals: Record<string, any>;
}

export interface AnalysisDetail extends AnalysisSummary {
  error: string | null;
  ai_summary: string | null;
  strengths: string[];
  weaknesses: string[];
  recommendations: Recommendation[];
  report: Record<string, any>;
  posts: PostOut[];
}

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${body}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => http<{ ai_enabled: boolean; ig_login_enabled: boolean }>("/api/health"),
  analyze: (username: string, language: string = "fa") =>
    http<AnalysisSummary>("/api/analyze", {
      method: "POST",
      body: JSON.stringify({ username, language }),
    }),
  getAnalysis: (id: string) => http<AnalysisDetail>(`/api/analyses/${id}`),
  listAnalyses: () => http<AnalysisSummary[]>("/api/analyses"),
};
