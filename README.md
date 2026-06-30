# Compliance Obligations Tracker

Accountability and compliance software for founders. Tracks a company's compliance
obligations: what must be filed, when it is due, what state it is in, and what
documentation backs it.

See [AGENTS.md](./AGENTS.md) for the full specification and domain rules.

## Stack

- **Backend** — FastAPI + Pydantic + SQLAlchemy + PostgreSQL (`/backend`)
- **Frontend** — Next.js (App Router) + React + TypeScript + Tailwind (`/frontend`)

## Run with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000 (health check: http://localhost:8000/health)
- Postgres: localhost:5432 (user/pass/db: `compliance`)

## Backend — local development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests (domain layer needs no database)
pytest

# Run the API against a local Postgres
export DATABASE_URL="postgresql+psycopg://compliance:compliance@localhost:5432/compliance"
uvicorn app.main:app --reload
```

### Document storage (Supabase)

Uploaded documents are stored as real files in a private Supabase Storage
bucket; downloads are served via short-lived signed URLs. Copy
`backend/.env.example` to `backend/.env` and set:

- `SUPABASE_URL` — project URL
- `SUPABASE_SERVICE_KEY` — service-role key (server-side only; never commit or log)
- `SUPABASE_BUCKET` — private bucket name (default `obligation-documents`)

### Database migrations (Alembic)

The schema is managed by Alembic. The app runs `alembic upgrade head`
automatically on startup, so a fresh database is migrated to the latest schema
with no manual step. After changing the SQLAlchemy models, generate a migration:

```bash
cd backend
alembic revision --autogenerate -m "describe the change"
alembic upgrade head   # apply locally (also applied on app startup)
```

## Frontend — local development

```bash
cd frontend
npm install

# Point at a running backend (defaults to http://localhost:8000)
export API_BASE_URL="http://localhost:8000"
npm run dev          # http://localhost:3000

npm test             # Vitest + Testing Library
npm run build        # production build / typecheck
```

The frontend renders only what the API allows: state transitions, the document
gate, and the masked tax ID all come from the backend. UI language toggles
between English and Spanish.
