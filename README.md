# Compliance Obligations Tracker

Accountability and compliance software for founders. Tracks a company's
compliance obligations: what must be filed, when it is due, what state it is
in, and what documentation backs it. See [AGENTS.md](./AGENTS.md) for the full
specification and domain rules.

- **Backend** — FastAPI + Pydantic + SQLAlchemy + PostgreSQL (`/backend`)
- **Frontend** — Next.js (App Router) + React + TypeScript + Tailwind (`/frontend`)

## Run

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000 (health check: `/health`)
- Postgres: localhost:5432 (user/pass/db: `compliance`)

No configuration needed. The only feature that requires setup is document
upload/download (see below); everything else works out of the box.

## Document storage (optional)

Documents live in a private Supabase Storage bucket, downloaded via
short-lived signed URLs. Set `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, and
`SUPABASE_BUCKET` (default `obligation-documents`) — in `backend/.env` for
local dev (see `backend/.env.example`), or exported in your shell for Docker.
Works against a cloud project or a local `supabase start` stack (from inside
Docker, use `http://host.docker.internal:54321`).

## Backend development

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                                 # domain tests need no database
export DATABASE_URL="postgresql+psycopg://compliance:compliance@localhost:5432/compliance"
uvicorn app.main:app --reload
```

The schema is managed by Alembic and applied automatically on startup. After
changing models: `alembic revision --autogenerate -m "describe the change"`.

## Frontend development

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000, expects the API at http://localhost:8000 (API_BASE_URL)
npm test         # Vitest + Testing Library
npm run build    # production build / typecheck
```
