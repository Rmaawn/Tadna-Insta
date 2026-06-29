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

## Quick start with Docker (recommended)

The whole stack — frontend + backend — runs with a single command. No need to
start the two services by hand or in a particular order; Docker Compose brings
them up together.

```bash
# 1. Fill in your config (OpenAI key, Instagram auth, etc.)
cp backend/.env.example backend/.env   # then edit backend/.env

# 2. Development — hot reload on both services (edits on the host apply live):
docker compose up --build

# 3. Production — optimized build, no reload:
docker compose -f docker-compose.yml up -d --build
```

- Frontend: <http://localhost:3000> · Backend API docs: <http://localhost:8000/docs>
- `docker compose up` automatically layers `docker-compose.override.yml` (the dev
  config). Passing `-f docker-compose.yml` alone skips it for a production run.
- The SQLite database and cached Instagram sessions are persisted in the
  `tadna-data` volume (production) or your local `backend/` folder (dev), so they
  survive rebuilds.
- Instagram/OpenAI settings are read from `backend/.env`. If `instagram.com` is
  blocked on your network, keep your system-wide tunnel on; on an unrestricted
  server (e.g. production) no proxy is needed.

> Prefer running the services natively instead? The manual setup is below.

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
| `IG_PROXY`        | Set when `instagram.com` is network-blocked (common in Iran), e.g. `http://127.0.0.1:10809` or `socks5h://127.0.0.1:1080`. |
| `IG_POST_LIMIT`   | Number of recent posts to analyze (default 20).                |
| `DATABASE_URL`    | Defaults to local SQLite. Swap for Postgres later, no code changes. |

### Instagram authentication

Anonymous Instagram requests get blocked, so the fetcher authenticates. Pick
the path that fits your environment:

**Local development (recommended) — Chrome `sessionid` cookie.** No password, no
checkpoint, works behind a VPN:

1. In Chrome, open `instagram.com` and log in (use a secondary account).
2. `F12` → **Application** → **Cookies** → `https://www.instagram.com` → copy
   the **`sessionid`** value.
3. Paste it into `backend/.env` as `IG_SESSIONID=...`.
4. Verify: `python verify_login.py` → expect `Instagram access works!`

Keep your VPN on while using the app, and set `IG_PROXY` if `instagram.com` is
filtered on your network.

**Production / unrestricted server.** Just set `IG_USERNAME` and `IG_PASSWORD`
(or run `python login_instagram.py` once); no proxy or sessionid needed.

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

### Languages

The UI ships in **Persian (default), Arabic and English** with a live toggle in
the header and full RTL support. The selected language is also sent to the
backend so the AI growth report is written in that language. Static UI strings
and the analyzer insights switch instantly; the AI narrative is generated in the
language chosen when the analysis was started.

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
