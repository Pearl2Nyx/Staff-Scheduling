# PRD-06 — Phase-1 API / Route List

Base URL: `/api/v1`. All responses JSON. No auth layer in the M2 skeleton (flagged for M3).

Status column: `LIVE` = implemented and working in the walking-skeleton repo (M2 requires exactly
one end-to-end flow — Staff Registry was chosen). `STUB` = route registered, returns
`501 Not Implemented` placeholder. Everything else is documented but not yet wired.

## Staff registry (FR-1) — end-to-end flow for M2

| Method | Route | Description | Status |
|---|---|---|---|
| GET | `/staff` | List staff, filter by `department_id`, `role`, `active` | **LIVE** |
| POST | `/staff` | Create staff record | **LIVE** |
| GET | `/staff/<id>` | Staff detail incl. skills | **LIVE** |
| PATCH | `/staff/<id>` | Update staff fields | **LIVE** |
| DELETE | `/staff/<id>` | Soft-delete (sets `active=0`) | **LIVE** |
| GET | `/departments` | List departments | **LIVE** |
| POST | `/departments` | Create department | **LIVE** |
| GET | `/skills` | List skill tags | **LIVE** |
| POST | `/staff/<id>/skills` | Attach skill to staff | **LIVE** |

## Credential registry (FR-2)

| Method | Route | Description | Status |
|---|---|---|---|
| GET | `/staff/<id>/credentials` | List a staff member's credentials | STUB |
| POST | `/staff/<id>/credentials` | Add credential | STUB |
| PATCH | `/credentials/<id>` | Update / re-verify credential | STUB |
| GET | `/credentials/expiring` | Credentials expiring within N days (query `days=`) | STUB |

## Shift templates (FR-3)

| Method | Route | Description | Status |
|---|---|---|---|
| GET | `/shift-templates` | List templates, filter by `department_id` | STUB |
| POST | `/shift-templates` | Create shift template | STUB |
| PATCH | `/shift-templates/<id>` | Update template | STUB |
| DELETE | `/shift-templates/<id>` | Remove template | STUB |

## Roster & publication (FR-14)

| Method | Route | Description | Status |
|---|---|---|---|
| GET | `/roster` | Roster entries for a date range + department | STUB |
| POST | `/roster/entries` | Create a roster entry (blocked if version locked) | STUB |
| DELETE | `/roster/entries/<id>` | Remove entry (blocked if version locked) | STUB |
| POST | `/roster/versions` | Open a new draft roster version for a dept/week | STUB |
| POST | `/roster/versions/<id>/publish` | Lock version, set `published_at`, trigger notifications | STUB |
| GET | `/roster/versions/<id>` | Version detail with entries | STUB |

## Leave management (FR-6)

| Method | Route | Description | Status |
|---|---|---|---|
| GET | `/leave-types` | List leave types | STUB |
| GET | `/staff/<id>/leave-balances` | Balances by year | STUB |
| POST | `/leave-requests` | File a leave request | STUB |
| PATCH | `/leave-requests/<id>` | Approve / reject (updates balance on approve) | STUB |
| GET | `/leave-requests` | List requests, filter by `staff_id`, `status` | STUB |

## Notifications (FR-14 support)

| Method | Route | Description | Status |
|---|---|---|---|
| GET | `/staff/<id>/notifications` | Notification history for a staff member | STUB |

## Ops

| Method | Route | Description | Status |
|---|---|---|---|
| GET | `/health` | Liveness check | **LIVE** |

**M2 exit criteria met**: app boots, `/health` responds, and the Staff Registry flow
(`POST /staff` → `GET /staff` → `GET /staff/<id>`) runs end-to-end against seeded SQLite data.
All Phase-1 routes are enumerated above so M3 (build checkpoint) has a fixed contract to build against.
