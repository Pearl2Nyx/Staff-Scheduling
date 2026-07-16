# P6 — Clinical Staff Scheduling (PRD-06) — Phase 1 MVP

Flask + SQLite implementation of Phase-1 scope: **FR-1, FR-2, FR-3, FR-6, FR-14**, plus the
two Phase-1 rule checks (ratio rule + rest-hour rule) from the M2 design doc.

## Setup

```bash
pip install flask
python app.py
```

Then open **http://127.0.0.1:5000** in a browser.

The database (`roster.db`) is created and seeded automatically the first time you run the app.
Delete `roster.db` and re-run to reset to fresh demo data.

## What's implemented

| Screen | FR | Route |
|---|---|---|
| Staff Registry | FR-1 | `/staff`, `/staff/add` |
| Credential Registry | FR-2 | `/staff/<id>` (Credentials tab) |
| Shift Templates | FR-3 | `/shift-templates` |
| Leave Management | FR-6 | `/leave`, `/leave/add` |
| Roster Grid + Publish | FR-14 | `/roster` |

## Rule checks implemented

1. **Credential hard block** — a staff member with any `expired` credential cannot be
   assigned to a new roster entry. Shown as a red banner on their profile and blocks the
   assignment attempt with an error message.
2. **Rest-hour rule (hard block)** — a new shift is rejected immediately if it gives the
   staff member less than **8 hours** rest from an adjacent shift (day before/after),
   including correct handling of overnight shifts.
3. **Ratio rule (warn → block)** — each shift template has a `min_staff_required`. Assigning
   fewer than that shows a **warning** while the roster is still a draft. Trying to
   **publish** a roster with any shift still below minimum is **blocked** — the publish
   button lists exactly which shift/date combinations are short.



## Known gaps (Phase 1 scope — by design)

- No authentication/login — role-based UI is described in the design doc but not enforced
  at the request level in this build (this is out of Phase-1 scope; FR-4 rules engine and
  role-based auth arrive in Phase 2/3 of the full PRD).
- Notifications (FR-14) are logged to the `notifications` table but not actually sent via
  app/WhatsApp/SMS (stubbed — real dispatch is out of scope for a local demo).
- Credential status (valid/expiring_soon/expired) is computed once at creation time based
  on the expiry date typed in; it does not re-evaluate daily on a schedule (would need a
  cron/scheduler, out of scope for Phase 1).
- Only one ratio rule and one hour-rule are implemented, per the milestone brief
  ("one ratio rule + one hour-rule chosen") — the full FR-4 rules engine (skill-mix,
  weekly-hour caps, etc.) is Phase 2/3.

## File structure

```
app.py               Flask application, all routes, both rule-check functions
schema.sql            SQLite DDL (12 tables)
seed.sql              Demo seed data (includes 1 deliberately expired credential and
                       1 deliberately understaffed shift template, for the demo script)
templates/            Jinja2 HTML templates (server-rendered, no JS framework needed)
static/style.css      Styling
```
