# PRD-06: Clinical Staff Scheduling & Duty Roster Management

> **Product**: Hospital Operations Suite — Sub-project 6 of 8
> **Author**: Healthcare Solution Architect
> **Version**: 1.0 | July 2026 | Status: Draft for review
> **Tiers**: S (<50 beds, ~30–120 staff) | M (50–200 beds, ~150–600 staff) | L (200+ beds, 800–5,000+ staff incl. residents) — legend per PRD-01 §3

---

## 1. Problem Statement

Hospital rosters in India are built in Excel by a nursing superintendent or department head, weeks in advance, then corrected daily by phone. The result: shifts that silently violate nurse:patient ratios, doctors scheduled against their OT lists, night-shift clustering that breaches working-hour norms, expired professional registrations going unnoticed, and zero data linking staffing levels to patient load. Compliance stakes are real — NABH 6th Edition ties staffing to patient acuity, Clinical Establishments (Central Government) Rules prescribe minimum staffing where adopted, state Shops & Establishments Acts govern hours/overtime for private hospitals, and NMC has pushed resident duty-hour reform.

## 2. Goals & Success Metrics

| Goal | Metric | Target |
|---|---|---|
| Ratio compliance | Shifts meeting configured nurse:patient ratios | ≥95% |
| Legal hours | Working-hour/rest-period violations per month | 0 (hard rule) |
| Roster stability | Same-day roster changes | <10% of shifts |
| Credential hygiene | Staff on duty with expired registration/BLS | 0 |
| Fairness | Night/weekend distribution variance across comparable staff | Gini <0.15 |
| Effort | Roster-preparation hours per ward per month | −70% vs Excel baseline |

## 3. Stakeholders & Personas

| Persona | Role |
|---|---|
| Nursing superintendent / dept head | Builds & approves rosters |
| Staff nurse / resident / technician / consultant | Views shifts, requests leave/swaps |
| HR manager | Leave balances, overtime, contract terms, statutory compliance |
| Medical superintendent | On-call trees, cross-department escalation |
| Quality/NABH coordinator | Ratio evidence for audits |
| Finance | Overtime cost, locum spend |

## 4. Scope

**In scope**: Shift-pattern & roster builder, rules engine (ratios, hours, skills, credentials), leave/swap workflows, on-call scheduling, attendance integration, float pool & locum management, acuity-linked staffing (via PRD-02/04 census), fatigue rules, roster analytics, credential registry (licences, certifications).
**Out of scope**: Payroll computation (exports attendance/overtime data), recruitment, performance appraisal, biometric hardware supply (integrates with existing).

## 5. User Stories

1. As a **nursing superintendent**, I want to generate a rule-compliant monthly roster from shift templates in minutes, then hand-adjust, so I stop spending 2 days/month on Excel.
2. As a **staff nurse**, I want to see my roster on my phone, apply for leave, and propose shift swaps that auto-check rule compliance so approvals are fast and fair.
3. As a **department head**, I want hard blocks on rostering a doctor into two places at once (ward + OT list from PRD-03) so conflicts surface at planning time.
4. As an **HR manager**, I want the system to hard-stop rosters that violate working-hour law (max hours/week, rest between shifts, night-shift limits per state rules) so we're never exposed in an inspection.
5. As a **charge nurse**, I want a same-day gap board (sick calls) with one-tap float-pool/locum call-out so coverage is minutes, not hours of phoning.
6. As a **quality coordinator**, I want shift-wise ratio-vs-census evidence exportable for NABH assessment so audits are painless.
7. As a **resident**, I want my duty hours tracked against policy caps so chronic overwork is visible to the DME office.

## 6. Functional Requirements

| # | Requirement | S | M | L |
|---|---|---|---|---|
| FR-1 | Staff registry: role, department, skills/competencies (ICU-trained, dialysis, scrub), employment type (permanent/contract/locum) | ● | ● | ● |
| FR-2 | Credential registry: NMC/State Medical Council reg., Nursing Council reg., pharmacist licence, BLS/ACLS expiry — with expiry alerts & roster-block on lapse | ● | ● | ● |
| FR-3 | Shift templates & patterns (morning/evening/night, 12-hr, on-call) per department | ● | ● | ● |
| FR-4 | Rules engine: nurse:patient ratios by unit type, max consecutive nights, min rest between shifts, weekly-hour caps, skill-mix minimums (≥1 ACLS per ICU shift) — all configurable, violations classed hard/soft | ◐ | ● | ● |
| FR-5 | Auto-roster generation (constraint solver) + manual override with reason | ○ | ● | ● |
| FR-6 | Leave management: types (EL/CL/SL/ML per policy), balances, approval chains, roster impact preview | ● | ● | ● |
| FR-7 | Shift-swap marketplace with auto rule-check and approver sign-off | ◐ | ● | ● |
| FR-8 | On-call trees: primary/secondary/consultant escalation per specialty, with contact reachability | ◐ | ● | ● |
| FR-9 | Attendance integration (biometric/mobile geo-fenced punch) → variance vs roster | ◐ | ● | ● |
| FR-10 | Gap board & call-out: sick-call marking, float pool broadcast, locum engagement log | ○ | ● | ● |
| FR-11 | Acuity-linked staffing: live census/acuity from PRD-02/04 drives recommended staffing per shift | ○ | ◐ | ● |
| FR-12 | Resident duty-hour tracking with policy caps & DME reports (L/teaching) | — | ○ | ● |
| FR-13 | Fairness analytics: night/weekend/holiday distribution, overtime by person | ◐ | ● | ● |
| FR-14 | Roster publication & notifications (app/WhatsApp/SMS), change alerts | ● | ● | ● |
| FR-15 | NABH evidence pack: shift-wise ratio vs census export | ◐ | ● | ● |

## 7. Non-Functional Requirements

| Area | Requirement |
|---|---|
| Availability | 99.5%; published rosters cached offline on mobile |
| Solver performance | Monthly roster for 100-nurse unit generated <60 s |
| Privacy | Staff personal data under DPDP (employees are data principals); health-related leave reasons masked from non-HR roles |
| Audit | Roster versions immutable; who-changed-what for labour disputes |
| Interop | Staff availability API consumed by PRD-03 (OT teams), PRD-04 (ratio checks), PRD-08 |

## 8. Regulatory & Compliance Requirements

| Instrument | Obligation |
|---|---|
| **State Shops & Establishments Acts** (private hospitals) | Working hours, overtime, weekly off, night-shift conditions for women (incl. transport/consent provisions in several states) — encoded per deployment state |
| **Clinical Establishments (Central Govt) Rules / state minimum standards** | Minimum staffing by facility category where notified |
| **NABH 6th Ed — HRM chapter** | Credential verification records, staffing plan linked to patient load/acuity, duty rosters as objective evidence |
| **Indian Nursing Council norms / ISCCM** | Nurse:patient ratio benchmarks (configurable defaults) |
| **NMC regulations** | Doctor registration validity; resident duty-hour policies (teaching hospitals) |
| **Maternity Benefit Act 1961 (amended 2017)** | ML entitlements; no night rostering during protected periods per policy |
| **Rights of Persons with Disabilities Act 2016** | Reasonable-accommodation flags in scheduling |
| **DPDP Act 2023 + Rules 2025** | Staff biometric/attendance data = personal data; purpose limitation; notice to employees; retention schedule |
| **Labour Codes (OSH Code 2020)** — as and when brought into force | Rules engine must be re-parameterisable to Code limits without re-engineering |

## 9. Data & Integration Architecture

- **FHIR R4**: `Practitioner`, `PractitionerRole`, `Schedule`, `Slot` — aligns with ABDM HPR (Healthcare Professionals Registry) IDs where available.
- **Integrations**: biometric devices (existing), HRMS/payroll export (CSV/API), PRD-02/03/04 (census & conflict checks), PRD-08 (staffing tiles), ABDM HPR lookup (M4 optional milestone).
- **Solver**: constraint-programming engine (hard rules inviolable; soft rules weighted, weights visible to admins).

## 10. 🤖 GenAI Features (Advisory-Only)

| # | Feature | Description | Guardrails |
|---|---|---|---|
| AI-1 | Roster-quality narrator | Explains a generated roster's trade-offs ("Nurse A has 3 nights because...") | Explanations from solver logs; no fabricated rationale |
| AI-2 | Absence forecaster | Predicts high-absence days (festivals, exam seasons, monsoon) for buffer planning | Advisory overlay on planning view |
| AI-3 | Policy Q&A assistant | Staff ask "How many CLs can I combine with a weekly off?" — answers from the hospital's own HR policy docs | RAG over approved policy corpus only; cites clause; "not HR advice" label |
| AI-4 | Swap matchmaker | Suggests viable swap partners (skills + rules compatible) | Suggestions only; standard approval flow unchanged |

## 11. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Solver roster rejected as "unfair" by staff | Publish fairness metrics; grievance-reviewable override log; phased trust-building (assist mode before auto mode) |
| Union/staff resistance to biometric-roster variance tracking | Transparent policy, DPDP notice, variance used for coverage not punishment (policy commitment) |
| State-law parameter errors | Per-state rule packs maintained centrally, versioned, legal-reviewed |
| Credential registry stale | Self-service upload + auto-verification against NMC/NUID registries where APIs exist; hard block only after grace workflow |
| Ghost/duplicate staff entries (contract churn) | Aadhaar-less dedup via mobile+bank-hash; HR audit views |

## 12. Phased Rollout

1. **Phase 1**: FR-1,2,3,6,14 — registry, credentials, templates, leave, publication.
2. **Phase 2**: Rules engine, swaps, on-call, attendance, gap board, fairness analytics.
3. **Phase 3**: Auto-solver, acuity-linked staffing, resident hours, NABH pack, AI features.

## 13. Prerequisites & External System Dependencies

> **Legend**: 🔴 Required · 🟡 Integrates if present (degraded mode defined) · ⚪ Optional

| Dependency | Type | If absent |
|---|---|---|
| Existing EHR/EMR/HIS | ⚪ None | Fully self-contained: staff registry, credentials, rosters all live in-module |
| PRD-01…05 modules | ⚪ | No patient-side dependency; suite integration only enriches (conflict checks, ratios) |
| HRMS/payroll system | 🟡 | Attendance/overtime exported as CSV; leave balances maintained in-module if no HRMS master |
| Biometric attendance hardware | 🟡 (FR-9) | Mobile geo-fenced punch or manual attendance marking; variance analytics degrade |
| PRD-02/04 census feeds | ⚪ (FR-11) | Acuity-linked staffing uses manually entered census; static ratios still enforced |
| PRD-03 OT schedule | ⚪ | Doctor double-booking checks limited to roster-internal conflicts |
| NMC/Nursing Council registries | ⚪ (FR-2) | Credential verification by document upload + manual check; auto-verification where APIs exist |
| ABDM HPR | ⚪ | HPR ID stored if available; never a precondition |

**Bottom line**: the most standalone module in the suite — can even be sold/deployed first in hospitals wanting quick wins, though its full value (ratio checks vs live census) arrives with PRD-02/04.

## 14. Open Questions

- Deployment state(s) → which Shops & Establishments parameters and women-night-shift provisions apply.
- Existing biometric hardware inventory & protocols (affects integration effort).
- Whether consultants (visiting) are rostered or only credential-tracked.
