# Rapid GDD

AI-powered Game Design Document generator and reviewer for indie/solo game developers.

## Structure

- `backend/` — Python FastAPI service (see `backend/requirements.txt`; uses a local `venv`)
- `frontend/` — React app scaffolded with Vite

## Getting started

### Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/activate   # Windows
pip install -r requirements.txt
cp .env.example .env      # fill in DATABASE_URL and GOOGLE_API_KEY
alembic upgrade head       # apply migrations
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Status

Scaffolding only — no feature code yet.
