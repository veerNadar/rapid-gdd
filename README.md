# Rapid GDD

**Design the game. Let AI handle the document.**

Rapid GDD turns a short intake form into a structured, editable Game Design
Document, and reviews GDDs you've already written — sorting them into
sections and generating section-by-section critique with suggested
rewrites. The goal is to spend your time on the design decisions that make
a game good, not on formatting a document nobody reads.

## How it works

1. **Answer a few questions** — genre, perspective, scope, reference games,
   and the one hook that makes the game worth playing.
2. **Get a structured GDD** — Gemini drafts all seven sections (Overview,
   Gameplay & Mechanics, Story & Narrative, Characters, World-Building,
   Progression, Additional Design Specifications), each aware of the others
   for consistency.
3. **Review, edit, iterate** — regenerate any section, edit inline, or
   upload a GDD you already wrote for AI critique against a design-review
   checklist (vague core loop, scope mismatch, mechanics vs. target
   feeling, weak progression, narrative inconsistency, shallow sections),
   with suggested rewrites you accept, edit, or reject — and optionally
   promote the accepted ones into a new project.

## Stack

- **Backend** — FastAPI, SQLAlchemy + Alembic, LangChain + Gemini
  (`langchain-google-genai`), Postgres (Supabase-hosted)
- **Frontend** — React + TypeScript, Vite, Tailwind, react-router-dom

## Prerequisites

- Python 3.11+
- Node 18+
- A free [Supabase](https://supabase.com) account (hosts the Postgres database)
- A free [Google AI Studio](https://aistudio.google.com) API key (Gemini)

## Setup

### 1. Create a Supabase project

1. Create a new project at [supabase.com](https://supabase.com) (the free tier is enough).
2. In **Project Settings → Database → Connection string**, copy the
   **Session pooler** URI — not the direct connection. The direct host is
   IPv6-only and won't resolve on most networks; the pooler host works
   everywhere.
3. If your database password contains special characters (e.g. `@`), URL-encode
   them in the connection string (`@` → `%40`, etc.).

### 2. Get a Gemini API key

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and
   create a free API key.
2. The free tier is rate-limited per model (observed: ~20 `generateContent`
   requests/day per model) — plenty for development, but expect `429`s if
   you generate a lot in one day. The app surfaces these as a clear
   rate-limit message rather than a generic error.

### 3. Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/activate   # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env      # fill in DATABASE_URL (Supabase pooler URI) and GOOGLE_API_KEY
alembic upgrade head      # apply migrations
uvicorn main:app --reload
```

Verify it's running: `curl http://localhost:8000/health` should return `{"status":"ok"}`.

### 4. Frontend

```bash
cd frontend
npm install
cp .env.example .env      # only needed if the backend isn't on localhost:8000
npm run dev
```

Visit `http://localhost:5173`.

## Project structure

```
backend/
  ai/           # LangChain + Gemini: prompts, generation, critique, review parsing
  alembic/      # Database migrations
  models/       # SQLAlchemy models
  routers/      # FastAPI routes (projects, sections, reviews, metrics)
  schemas/      # Pydantic request/response schemas
  services/     # Shared DB helpers used by multiple routers
frontend/
  src/api/      # Typed API client
  src/components/
  src/pages/
```

## Deployment

This project is deploy-ready but **not deployed** — nothing here should be
run unless you choose to run it.

- **Backend** — any Python/ASGI host works (Render, Railway, Fly.io, etc.).
  A `Procfile` is included (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`).
  Set `DATABASE_URL`, `GOOGLE_API_KEY`, and `CORS_ORIGINS` (comma-separated
  list of your deployed frontend's origin(s), e.g.
  `https://your-app.vercel.app`) as environment variables on the host. Run
  `alembic upgrade head` against the production database before or during
  the first deploy.
- **Frontend** — any static host works (Vercel, Netlify, Cloudflare Pages).
  Build command `npm run build`, output directory `dist`. Set
  `VITE_API_BASE_URL` to your deployed backend's URL.
- **Database** — Supabase is already cloud-hosted, so there's no separate
  database deployment step; just make sure the deployed backend can reach
  it (Supabase allows connections from any IP by default unless you've
  restricted it).

## Status

Functional end-to-end: intake → AI generation → editing/regeneration →
review upload → AI critique → accept/edit/reject → promote to a new
project, plus a lightweight metrics view. Not deployed.
