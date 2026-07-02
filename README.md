# Compliance Obligations Tracker

Accountability and compliance software for founders. Tracks a company's
compliance obligations: what must be filed, when it is due, what state it is
in, and what documentation backs it. See [AGENTS.md](./AGENTS.md) for the full
specification and domain rules.

- **Backend** - FastAPI + Pydantic + SQLAlchemy + PostgreSQL (`/backend`)
- **Frontend** - Next.js (App Router) + React + TypeScript + Tailwind (`/frontend`)

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

Documents live in a private Supabase Storage bucket. Without this setup the
rest of the app works fine; uploads and downloads will fail gracefully.

### Option A - Local Supabase stack

```bash
supabase start                    # starts Supabase in Docker
supabase status                   # prints the service_role key and API URL
supabase storage create-bucket obligation-documents --private
```

Copy the output into `backend/.env` (see `backend/.env.example`):

```env
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_KEY=<service_role key from supabase status>
```

> When running the full stack via `docker compose`, use
> `http://host.docker.internal:54321` as the URL instead.

### Option B - Supabase cloud project

Create a private bucket named `obligation-documents` in the Storage tab, then
set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` (Settings → API → service_role)
in `backend/.env`.

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
