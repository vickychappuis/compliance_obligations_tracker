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
