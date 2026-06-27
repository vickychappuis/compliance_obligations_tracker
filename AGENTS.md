# AGENTS.md

Guidance for working in this repository. Read this before making changes.

## Overview

Compliance Obligations Tracker — accountability and compliance software for founders. It tracks a company's compliance obligations: what must be filed, when it is due, what state it is in, and what documentation backs it.

This is a high-care domain. A miscalculated due date, a leaked sensitive field, or an unrecorded state change are expensive errors. Treat the domain rules below as non-negotiable.

## Repository structure

Monorepo with two deployables:

```
/backend     FastAPI service (domain, services, data access, routes)
/frontend    Next.js App Router app (features, UI primitives)
docker-compose.yml
```

Backend and frontend are independent: the frontend consumes the API and never re-implements domain logic.

## Tech stack

**Backend** — FastAPI + Pydantic + PostgreSQL. Layered: `routes/` → `services/` → `data access/` → `domain/`. (SQLite is an acceptable fallback for local persistence.)

**Frontend** — Next.js (App Router) + React + TypeScript in `strict` mode (no `any`) + Tailwind, no heavy UI library. Server Components by default; Server Actions for mutations.

## Domain model — Obligation

- `id`
- `type` — one of `annual_report | franchise_tax | boi_report | registered_agent_renewal`
- `title`, `description`
- `status` — one of `pending | in_progress | submitted | done`
- `dueDate`
- `owner` — required
- `requiresDocument` (bool) and an attached document when set
- `companyTaxId` — sensitive

## Domain rules (critical — these are the core of the system)

These live in the backend domain layer, isolated from HTTP and persistence. Rules never go in route handlers.

### State machine (backend is the source of truth)

Allowed transitions only:

- `pending → in_progress`
- `in_progress → submitted | pending`
- `submitted → done | in_progress` (rejection / rework)
- `done → in_progress` (reopen)

Any transition not listed is invalid. The API rejects invalid transitions and they must not be persisted through any path.

### Document-gated invariant

If `requiresDocument` is true, the obligation cannot move to `submitted` without an attached document. This is enforced in the backend domain, not in the form.

### Overdue is derived, never stored

An obligation is overdue when `dueDate` has passed and its status is not `submitted` or `done`. Compute it; do not add it as a persisted status. The derivation lives in the domain layer.

### Sensitive data: `companyTaxId`

- Stored in full.
- Returned masked in all reads (e.g. `••••6789`).
- Never written to logs, error messages, or traces.

### Audit trail

Every state change is recorded with from-state, to-state, and timestamp. The detail view exposes this history.

### Concurrency

State changes must be safe under simultaneous requests. The chosen mechanism (version / optimistic lock / transaction) must be applied consistently to state-changing operations.

## Backend conventions

- Keep the domain layer free of FastAPI, Pydantic-request, and database concerns. Domain logic should be testable without HTTP or a database.
- Routes are thin: validate input, call a service, map results/errors to HTTP.
- Validation is server-side. Do not rely on the client to enforce any rule.
- Consistent error model: meaningful HTTP status codes, `404` for missing resources, structured error bodies.
- Pydantic models should reflect reality — no permissive `Any` to paper over shape mismatches.
- Provide a state-change endpoint distinct from generic update; it runs the transition rules.

## Frontend conventions

- Organize by layers/features with reusable UI primitives. Keep server/client boundaries explicit.
- Do not duplicate domain logic. Valid transitions and the document-gated block come from the backend; render what the API allows.
- TypeScript `strict`, no `any`.
- Surface loading and error states from the API in the UI.
- i18n for `es` and `en`.
- Basic accessibility on interactive elements.

Expected views:

- **Dashboard** — KPIs (total, by status, overdue, upcoming), filtering, list sorted by `dueDate` with overdue items highlighted.
- **Detail** — all fields, masked `taxId`, audit history, and the valid transitions available for the current state. The submitted action is disabled when a required document is missing.
- **Create / edit** — with validation.

## Testing

Behavior-focused tests on both layers:

- Backend: state transitions, the document-gated invariant, and at least one endpoint end to end.
- Frontend: at least one user flow.

## Non-negotiables

- Domain rules never live in route handlers or React components.
- Invalid state transitions are never persisted.
- `companyTaxId` is never logged and never returned unmasked.
- `overdue` is never stored as a status.
- The frontend never re-derives transition validity or the document gate locally.
- Keep commits small and focused.