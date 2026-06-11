# Tadna Insta — AI Instagram Growth Intelligence

A premium, AI-native platform that analyzes any **public** Instagram profile and
returns a strategic growth report: branding, content, engagement and visual
identity scores plus an AI growth strategy that reads like a senior consultant
wrote it.

> Not another analytics dashboard — an **AI Instagram Growth Strategist**.

---

## Architecture

```
Tadna Insta/
├── backend/                 FastAPI + SQLAlchemy (async, SQLite) + OpenAI
│   └── app/
│       ├── fetchers/        Instagram data collection (instaloader, pluggable)
│       ├── analyzers/       Modular, isolated analyzers + AI recommendation engine
│       │   ├── profile_analyzer.py
│       │   ├── content_analyzer.py
│       │   ├── engagement_analyzer.py
│       │   ├── visual_analyzer.py
│       │   └── recommendation_engine.py
│       ├── ai/              LLM provider abstraction (OpenAI today, pluggable)
│       ├── services/        Pipeline orchestration
│       ├── models/          ORM entities (accounts, posts, analyses)
│       └── api/             REST routes
└── frontend/                Next.js 14 + Tailwind + Framer Motion + Recharts
```

**Design principles:** modular analyzers (each independent & pluggable),
async-first backend, AI-provider abstraction, clean separation of fetching →
analysis → AI → persistence. New analyzers register in
`app/analyzers/__init__.py::ANALYZER_PIPELINE` with zero changes elsewhere.

---

## Prerequisites

- Python 3.11+ (tested on 3.13)
- Node.js 18+ (tested on 22)
- An **OpenAI API key** (for AI recommendations)
- Optional: a **secondary** Instagram account for reliable data fetching

> **Package mirrors:** to avoid unstable connections, npm and pip are
> pre-configured to install from Liara's Iranian mirrors via the committed
> `frontend/.npmrc` and `backend/pip.ini`. Both are verified working. See
> [`docs/MIRRORS.md`](docs/MIRRORS.md) for Docker/Debian mirrors too.

---

## 1) Backend setup

```powershell
cd backend
$env:PIP_CONFIG_FILE = "$PWD\pip.ini"   # use the Liara PyPI mirror
python -m pip install -r requirements.txt
copy .env.example .env        # then edit .env
uvicorn app.main:app --reload --port 8000
```

Edit `backend/.env`:

| Variable          | Purpose                                                        |
| ----------------- | -------------------------------------------------------------- |
| `OPENAI_API_KEY`  | **Required** for AI recommendations.                           |
| `OPENAI_MODEL`    | Defaults to `gpt-4o-mini`.                                      |
| `IG_USERNAME` / `IG_PASSWORD` | Optional. Log in **once** for reliable fetching — a session is cached to `.ig_sessions/`, so the password is only used the first time. Use a throwaway account. |
| `IG_POST_LIMIT`   | Number of recent posts to analyze (default 20).                |
| `DATABASE_URL`    | Defaults to local SQLite. Swap for Postgres later, no code changes. |

> **On Instagram reliability:** anonymous requests are aggressively rate-limited
> and often blocked. Configuring `IG_USERNAME`/`IG_PASSWORD` once makes fetching
> dependable. The login is cached as a session file and reused thereafter.

API docs: <http://localhost:8000/docs>

### Optional: face detection in the visual analyzer

The visual analyzer auto-enables face detection **if** OpenCV is present:

```powershell
python -m pip install opencv-python-headless
```

Without it, every other visual metric still works; face ratio reports `n/a`.

---

## 2) Frontend setup

```powershell
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Open <http://localhost:3000>, enter a public Instagram username, and watch the
analysis stream into the dashboard.

---

## How it works

1. `POST /api/analyze` creates an analysis row and runs the pipeline in a
   background task (an infra-free stand-in for Celery).
2. The fetcher pulls the profile + latest N posts (and thumbnails).
3. Each analyzer runs in isolation, writing a structured section into the report
   and sharing signals via a mutable `context`.
4. Headline scores are computed; the **Growth Score** is a weighted blend.
5. The AI recommendation engine turns the structured analysis into an executive
   summary, strengths/weaknesses and prioritized recommendations.
6. The frontend polls `GET /api/analyses/{id}` and renders the dashboard.

---

## Roadmap (architected for, not built in MVP)

- Competitor intelligence & trend detection
- Reel understanding, speech-to-text, OCR
- Comment sentiment analysis
- AI caption / reel-script generation
- Autonomous AI growth agent

Each is a new fetcher/analyzer module — the pipeline is built to absorb them.
