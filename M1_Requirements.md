# M1 Requirements — PRD-06 Clinical Staff Scheduling & Duty Roster Management

## 5. Phase-1 Functional Requirements (S-Tier scope)

| # | Requirement | S-Tier |
|---|---|:---:|
| FR-1 | Staff registry: role, department, skills/competencies (ICU-trained, dialysis, scrub), employment type (permanent/contract/locum) | ● |
| FR-2 | Credential registry: NMC/State Nursing Council reg., pharmacist licence, BLS/ACLS expiry — with expiry alerts and roster-block on lapse | ● |
| FR-3 | Shift templates & patterns (morning/evening/night, 12-hr, on-call) per department | ● |
| FR-6 | Leave management: types (EL/CL/SL/ML per policy), balances, approval chains, roster impact preview | ● |
| FR-14 | Roster publication & notifications (app/WhatsApp/SMS), change alerts | ● |

> All five requirements are marked ● (fully in scope) for S-tier hospitals — no partial/optional markers apply at this tier for Phase 1. Rules engine (FR-4), swap marketplace (FR-7), on-call trees (FR-8), attendance (FR-9), auto-solver (FR-5), acuity-linking (FR-11), resident-hours (FR-12) and the NABH evidence pack (FR-15) are Phase 2/3 — out of scope for M1/M2.

## 6. User Stories & Acceptance Criteria

| FR | User Story | Acceptance Criteria |
|---|---|---|
| FR-1 | As a **nursing superintendent**, I want a searchable staff registry with role, department and skill tags so I know who's available before I start building a roster. | Registry lists staff filterable by department/role/active status; each record captures role, department, employment type, and tagged skills; new staff can be added in under 60 seconds with employee code and department mandatory. |
| FR-2 | As an **HR manager**, I want credential expiry alerts and an automatic roster-block on lapsed registrations so we're never non-compliant during an inspection. | System flags credentials as valid / expiring-soon / expired based on `expiry_date`; a staff member with an expired mandatory credential cannot be assigned to a new roster entry; expiring-soon threshold is configurable (default 60 days). |
| FR-3 | As a **department head**, I want reusable shift templates per department so roster-building doesn't start from scratch every week. | Templates define name, shift type, start/end time and duration per department; duration auto-calculates from start/end; existing templates for a department are listed before a new one is created. |
| FR-6 | As a **staff nurse**, I want to apply for leave and see my balance with a roster-impact preview so approvals are fast and informed. | Leave request captures type, date range and reason; current-year balance for that leave type is shown before submission; if the requested dates overlap a published roster entry, the approver sees a coverage-gap warning before deciding. |
| FR-14 | As a **staff nurse**, I want to see my published roster and get notified of changes so I'm never caught off guard by a shift swap. | Publishing a roster version locks it (audit-immutable) and triggers a notification per affected staff member; roster is viewable per staff member for the published week; unpublished/draft entries are never shown to staff. |

---
*Scope note: this mirrors the FR-1–FR-15 numbering from PRD-06 §6 — numbers are not sequential here because only the Phase-1 (S-tier ●) subset is listed, per §12 Phased Rollout.*
