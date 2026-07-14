# PRD-06 — Phase-1 ERD

Scope: FR-1, FR-2, FR-3, FR-6, FR-14 only. Rules engine, solver, swap marketplace,
on-call trees, attendance, acuity-linking, resident-hours, NABH pack are Phase 2/3 — not modeled here.

```mermaid
erDiagram
    DEPARTMENTS ||--o{ STAFF : employs
    DEPARTMENTS ||--o{ SHIFT_TEMPLATES : defines
    DEPARTMENTS ||--o{ ROSTER_VERSIONS : owns

    STAFF ||--o{ STAFF_SKILLS : has
    SKILLS ||--o{ STAFF_SKILLS : tagged_on

    STAFF ||--o{ CREDENTIALS : holds
    STAFF ||--o{ ROSTER_ENTRIES : assigned_to
    STAFF ||--o{ LEAVE_BALANCES : has
    STAFF ||--o{ LEAVE_REQUESTS : files
    STAFF ||--o{ NOTIFICATIONS : receives

    SHIFT_TEMPLATES ||--o{ ROSTER_ENTRIES : instantiated_as
    ROSTER_VERSIONS ||--o{ ROSTER_ENTRIES : groups

    LEAVE_TYPES ||--o{ LEAVE_BALANCES : tracked_by
    LEAVE_TYPES ||--o{ LEAVE_REQUESTS : categorizes

    ROSTER_ENTRIES ||--o{ NOTIFICATIONS : triggers

    DEPARTMENTS {
        int id PK
        text name
        text unit_type
    }
    STAFF {
        int id PK
        text employee_code
        text full_name
        text role
        int department_id FK
        text employment_type
        int active
    }
    SKILLS {
        int id PK
        text name
    }
    STAFF_SKILLS {
        int staff_id FK
        int skill_id FK
    }
    CREDENTIALS {
        int id PK
        int staff_id FK
        text credential_type
        text credential_no
        text expiry_date
        text status
        int verified
    }
    SHIFT_TEMPLATES {
        int id PK
        int department_id FK
        text name
        text shift_type
        text start_time
        text end_time
        real duration_hours
    }
    ROSTER_VERSIONS {
        int id PK
        int department_id FK
        text week_start_date
        int version_number
        text published_at
        int is_locked
    }
    ROSTER_ENTRIES {
        int id PK
        int staff_id FK
        int shift_template_id FK
        int roster_version_id FK
        text shift_date
        text status
    }
    LEAVE_TYPES {
        int id PK
        text code
        text name
        int max_days_per_year
    }
    LEAVE_BALANCES {
        int id PK
        int staff_id FK
        int leave_type_id FK
        int year
        real allocated_days
        real used_days
    }
    LEAVE_REQUESTS {
        int id PK
        int staff_id FK
        int leave_type_id FK
        text start_date
        text end_date
        text status
    }
    NOTIFICATIONS {
        int id PK
        int staff_id FK
        int roster_entry_id FK
        text channel
        text status
    }
```

## Design notes
- `roster_versions.is_locked = 1` after publish enforces the audit/immutability NFR — app-layer must reject writes to `roster_entries` once the parent version is locked (M2 stub: enforced in `POST /roster/versions/<id>/publish`, not yet enforced on entry edits — flag for M3).
- `credentials.status` is denormalized (computed nightly against `expiry_date` in production; for the MVP it's set at seed time and left static — no scheduler in the walking skeleton).
- Health-related `leave_requests.reason` masking from non-HR roles (DPDP requirement, §7 NFR) is an API-layer concern, not a schema concern — not implemented in M2, flagged for M3 auth work.
