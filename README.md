 PRD-06 — Clinical Staff Scheduling (Phase-1 MVP)

M2 deliverable (design freeze, per team sprint calendar): ERD, SQLite DDL, API/route list,
5 low-fi wireframes, deterministic seeded dataset, walking-skeleton Flask repo.

**Scope**: Phase-1 (●) requirements only, per PRD-06 §12 Phased Rollout:
FR-1 (staff registry), FR-2 (credential registry), FR-3 (shift templates),
FR-6 (leave management), FR-14 (roster publication). No solver, no rules engine,
no swap marketplace, no acuity-linking, no resident-hours, no NABH export — those are
Phase 2/3 (M3+).

**Stack**: Python 3.9+ / Flask / SQLite / Chart.js (Chart.js is for the M3 analytics
views — not yet wired, no frontend exists in M2).

**AI features**: none in M2. Per PRD-06 §10, any GenAI feature (roster narrator, absence
forecaster, policy Q&A, swap matchmaker) is advisory-only — no AI output writes to
records without human confirmation. Not built in this milestone.

## Repo layout

```
schema.sql               SQLite DDL (source of truth for the ERD)
docs/ERD.md               Mermaid ERD + design notes
docs/API_ROUTES.md         Full Phase-1 route contract (LIVE vs STUB)
seed.py                   Deterministic sample data (10 staff, 4 depts, 6 credentials incl.
                           1 expired + 1 expiring-soon, 6 shift templates, leave data, 1 roster week)
app.py                     Flask app — Staff Registry (FR-1) is the one LIVE end-to-end
                           flow required for M2; everything else in the route contract
                           is registered as a 501 stub so M3 has a fixed API to build against
wireframes/                5 SVG low-fi wireframes (registry, credentials, shift templates,
                           leave form, roster publish/calendar)
requirements.txt
```

## Run it

```bash
pip install -r requirements.txt
python3 seed.py          # (re)builds prd06.db from schema.sql + fixed sample data
python3 -m flask --app app run --port 5000
```

Then:

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/api/v1/staff
curl -X POST http://127.0.0.1:5000/api/v1/staff \
  -H "Content-Type: application/json" \
  -d '{"employee_code":"EMP011","full_name":"Test Nurse","role":"nurse","department_id":1}'
curl http://127.0.0.1:5000/api/v1/staff/11
```

## M2 exit criteria (met)

- [x] App boots (`flask run` starts clean, `/health` returns 200)
- [x] One end-to-end flow works against seeded data: create staff → list staff → staff detail
- [x] Final ERD + DDL (`schema.sql`, `docs/ERD.md`)
- [x] Full API/route list for Phase-1 scope (`docs/API_ROUTES.md`)
- [x] 5 wireframes covering all Phase-1 FRs (`wireframes/`)
- [x] Seeded sample dataset, deterministic (`seed.py`)

## Carried forward to M3 (build checkpoint)

- Implement the remaining STUB routes: credentials, shift templates, roster entries/publish
  (incl. version-lock enforcement), leave requests/balances, notifications.
- Enforce roster-version immutability at the write layer (schema supports it via
  `roster_versions.is_locked`; not yet checked in `app.py`).
- DPDP masking of leave `reason` field from non-HR roles — needs an auth/role layer,
  out of scope until M3.
- Credential `status` recompute job (currently static at seed time).
