# Odoo Plantation Management Add-Ons (PLT Suite) — Development Plan

> **For Hermes:** Use subagent-driven-development skill to implement each sprint module-by-module.
> **SDLC:** This plan follows a modified waterfall-within-sprints approach: Requirements → Design → Build → Test → Deploy for each module, with integration testing between sprints.

**Goal:** Build the custom PLT add-on suite on Odoo 19 Enterprise to run a 100–500 ha oil palm estate end-to-end (nursery → harvest → transport → sales).

**Architecture:** 13 custom Odoo modules (PLT-01 through PLT-13) layered on Odoo 19 Enterprise native modules. Each block = one Odoo analytic account; every field document is a first-class Odoo record with chatter, state machine, and audit trail. Mobile app (PLT-11) is a separate Android project.

**Tech Stack:** Python 3.11, Odoo 19 Enterprise, PostgreSQL 16, XML/JS OWL framework (Odoo frontend), React Native or Flutter (mobile app TBD).

**Source:** `/root/workspace/kebun/odoo-19.0+e.20260709/`
**Custom addons path:** `/root/workspace/kebun/odoo-data/addons/19.0/`
**Database:** `odoo` on PostgreSQL (user: odoo)
**Config:** `/root/workspace/kebun/odoo.conf`

---

## SDLC Phases & Timeline

```
Phase 0: Foundations       (Weeks 1–8)
Phase 1: Harvest-to-Cash   (Weeks 9–20)
Phase 2: Upkeep, Planning & Plasma (Weeks 21–34)
Phase 3: Compliance        (Weeks 35–46)
Phase 4: Extended          (Weeks 47+)
```

---

## Phase 0 — Foundations (Weeks 1–8)

**Goal:** Set up the development environment, build the master data backbone (PLT-01), and the GCG control layer skeleton (PLT-12). Everything else depends on these.

### Sprint 0.1: Dev Environment & Conventions (Week 1)

**Goal:** Establish the development workflow, coding standards, and Odoo module scaffolding.

#### Task 0.1.1: Create custom addons directory structure
- **Path:** `/root/workspace/kebun/odoo-data/addons/19.0/`
- **Content:** Create the directory and add it to `addons_path` in `odoo.conf`
- **Verify:** Run `odoo server -c odoo.conf --init=base --stop-after-init` and confirm the custom path appears in logs

#### Task 0.1.2: Scaffold module template
- **Path:** `odoo-data/addons/19.0/plt_template/`
- **Content:** Create `__init__.py`, `__manifest__.py`, `/models/`, `/views/`, `/security/`, `/data/`, `/static/`, `/tests/` with standard Odoo 19 conventions
- **Verify:** Module appears in Apps list

#### Task 0.1.3: Establish development conventions
- Python 3.11+, Odoo 19 ORM, OWL 2 for frontend
- PEP 8, Odoo coding guidelines
- TDD: tests before models (see `test-driven-development` skill)
- Commits: `feat(PLT-XX):`, `fix(PLT-XX):`, `test(PLT-XX):`
- All user-facing labels in Bahasa Indonesia (primary) + English (secondary)
- Commit after every logical unit

#### Task 0.1.4: Set up test database
- Create a separate `odoo_test` database for test runs
- Configure `--test-enable` and `--test-tags` for module-level testing
- **Verify:** `odoo server -c odoo.conf -d odoo_test --init=base --stop-after-init --test-enable`

---

### Sprint 0.2: PLT-01 — Estate Master Data & Land Registry (Weeks 2–5)

**Purpose:** Single source of truth for the physical estate and its legality. Every other module references this.
**Priority:** P0 | **Size:** M (4–8 dev-weeks, compressed with experienced team)
**Dependencies:** None (base Odoo only)

#### Task 0.2.1: Build `plt_estate` module skeleton
- **Create:** `plt_estate/__manifest__.py` — depends on `base`, `mail`
- **Models needed:**
  - `estate.estate` — single-estate record (name, code, address, phone)
  - `estate.afdeling` — division (name, code, estate_id, manager_id → hr.employee)
  - `estate.block` — block (code, name, afdeling_id, area_ha_planted, area_ha_total, tahun_tanam, seed_source, SPH, soil_class, topography_class, status TBM/TM with dated history, polygon_geojson, analytic_account_id auto-created)
  - `estate.ancak` — optional sub-division (code, block_id, area)
  - `estate.tph` — collection point (code, block_id, gps_lat, gps_lon)
  - `estate.land_document` — legal parcel docs (SHM/HGU/STDB/IUP number, holder_name, area, expiry_date, attachment, expiry_alerts)
- **Views:** Form/List/Kanban for each model; map view for blocks with GeoJSON; dashboard for blocks by afdeling
- **Tests:** Block → analytic account creation; TM flip re-routes costs; expiry alerts fire

#### Task 0.2.2: Block → Analytic Account Integration
- On `estate.block` creation, auto-create an `account.analytic.account` named `BLK-{code}`
- Block posting rules: TBM status → costs to asset WIP; TM status → costs to P&L
- Status history: `estate.block.status.history` model with `date_from`, `date_to`, `status`, `approved_by`, `effective`
- **Verify:** Create block → check analytic account exists in Accounting → change status to TM → confirm effective date logic

#### Task 0.2.3: Palm Census (Sensus Pokok)
- **Model:** `estate.census` — periodic per-block census (date, block_id, productive_count, unproductive_count, dead_count, vacant_points, sisipan_count, notes)
- Computed: variance vs prior census period
- **Views:** Census form with before/after comparison; trend chart per block
- **Tests:** Variance calculation correct; census with zero pokok rejected

#### Task 0.2.4: GIS & Land Legality
- GeoJSON polygon field on block; auto area calculation vs declared area; variance flag > 3%
- Land document expiry alerts at 12/6/3 months → auto-post to chatter
- Document type registry with name-consistency validation (holder names match across linked docs)
- **Verify:** Upload a test polygon, compare computed area vs declared; set document expiry to +60 days → alert appears

#### Task 0.2.5: Master Data Approval Workflows
- All master data changes (block, afdeling, census, land docs) go through `Draft → Submitted → Approved` workflow
- Maker: admin/assistant; Approver: Estate Manager
- Change history via `mail.thread` tracking; approved records locked (no edit without reversal)
- **Tests:** Unapproved block edit rejected; reversal document creates correct contra-entry

---

### Sprint 0.3: PLT-12 — GCG Control Layer Skeleton (Weeks 6–8)

**Purpose:** The governance spine — Authority Matrix, SoD engine, audit trail, exception dashboard.
**Priority:** P0 (skeleton with MVP) | **Size:** M
**Dependencies:** PLT-01 (estate master for role scoping)

#### Task 0.3.1: Build `plt_gcg` module skeleton
- **Create:** `plt_gcg/__manifest__.py` — depends on `base`, `mail`, `hr`, `plt_estate`
- **Models:**
  - `gcg.authority.matrix` — configurable approval routes (document_type, min_value, max_value, approver_role_1, approver_role_2, is_active)
  - `gcg.sod.rule` — segregation-of-duties rules (role_a, role_b, conflict_description, document_types, is_blocking)
  - `gcg.audit.log` — append-only critical field changes (model_name, record_id, field_name, old_value, new_value, changed_by, changed_at)
  - `gcg.exception` — red-flag log (exception_type, document_reference, severity, assigned_to, status)
  - `gcg.whistleblowing` — grievance case (channel, reporter, description, status, resolution, is_anonymous)

#### Task 0.3.2: Authority Matrix Engine
- Configurable per document type + value band (e.g., BPB ≤ Rp X: asisten; > Rp X: EM)
- Matrix itself is version-controlled and requires Direksi approval to change
- API: `gcg.check_approval(document_model, document_id, amount) → required_approvers`
- **Views:** Matrix grid editor; approval route tester
- **Tests:** BPB of Rp 5M routes to EM; BPB of Rp 500K routes to Asisten; price master always routes to Direksi

#### Task 0.3.3: Segregation of Duties (SoD) Engine
- Violation check at user-role assignment time (not at transaction time — preventative)
- Conflict matrix:
  - Gudang ⛔ approve BPB
  - Weighbridge operator ⛔ edit SPB
  - Payroll admin ⛔ approve payroll
  - Kerani panen ⛔ approve harvest (maker ≠ approver)
- **Tests:** Assign gudang + BPB approver → rejected; assign asisten + payroll approver → accepted

#### Task 0.3.4: Immutable Audit Trail
- Override `mail.thread.message_post` to add critical field change logging
- All PLT models inherit `gcg.audit.mixin` which auto-logs field changes on write
- Posted/locked documents blocked from edit (override write/create to check state)
- Correction mechanism: reversal documents only — original stays immutable
- **Tests:** Edit a posted BKM → rejected; reversal creates correct contra-document

#### Task 0.3.5: Exception Dashboard (SPI View)
- Aggregated red-flag view for internal audit:
  - Weighbridge variance > tolerance
  - Restan > 24h
  - Rotation > target
  - HK anomalies (output > norm × 150%)
  - Chemical variance
  - SPB gaps (missing sequence numbers)
  - Premi outliers
  - Master-data changes (last 7 days)
  - Override log (any user overrides in the period)
- SPI role: read-all, no transaction rights — enforced via record rules
- **Verify:** Run as SPI user → can view all dashboards, cannot create/approve any document

#### Task 0.3.6: Period Close & Locking Checklist
- Monthly close checklist model with configurable items
- Each checklist item linked to a system check (e.g., "All BKM posted for period" → queries BKM state)
- Only when all items pass can the accounting period be locked
- **Tests:** Unlocked period prevents posting; checklist item auto-detects unposted BKM

---

### Phase 0 Exit Criteria (All must pass before Phase 1)
- [ ] `plt_estate` module: blocks, afdelings, TBM/TM status, analytic accounts, census, GIS, legality docs with expiry alerts — all CRUD + workflows tested
- [ ] `plt_gcg` module: Authority Matrix, SoD rules, audit log, exception dashboard, period close checklist — all tested
- [ ] PSAK 69 cost routing: TBM costs → capitalized to asset WIP; TM costs → P&L expense, verified with sample transactions
- [ ] Role matrix: Estate Manager, Asisten, Mandor, Kerani, KTU, SPI roles defined and tested
- [ ] Test coverage ≥ 80% on both modules
- [ ] Database migration scripts run clean
- [ ] UAT sign-off on master data entry screen for a sample estate (1 afdeling, 10 blocks)

---

## Phase 1 — Harvest-to-Cash MVP (Weeks 9–20)

**Goal:** The core value chain: taksasi → harvest capture → premi → SPB → weighbridge → mill reconciliation → invoicing → payroll. This is where the estate generates revenue and pays workers.

### Sprint 1.1: PLT-05 — Harvest Management (Weeks 9–14)
**Priority:** P0 | **Size:** L | **Dependencies:** PLT-01, PLT-12

#### Models
- `harvest.taksasi` — D-1 crop estimate (date, block_id, section, pokok_sampled, bunches_counted, AKP, estimated_janjang, estimated_tonnage, required_harvesters, required_trucks)
- `harvest.rotation` — harvest sections (name, blocks[], rotation_interval_days, last_harvest_date, next_harvest_date)
- `harvest.ancak` — daily harvester-to-ancak allocation (date, mandor_id, harvester_id, block_id, ancak_type tetap/giring)
- `harvest.tph_record` — harvest capture at TPH (date, tph_id, harvester_id, kerani_id, janjang_count, brondolan_kg, brondolan_karung, gps_lat, gps_lon, timestamp, photo)
- `harvest.quality_event` — quality grading & denda (tph_record_id, event_type mentah/tangkai/brondolan_tidak_dikutip/buah_tinggal/pelepah, quantity, rate, denda_amount, photo)
- `harvest.inspection` — mutu ancak/buah inspection (date, type, mandor_id, block_id, checklist_items[], scores, result)
- `harvest.premi.config` — effective-dated rate tables (basis_kg_per_hk per block_class, premi_tier_1_rate, premi_tier_2_rate, brondolan_rate, mandor_multiplier, kerani_multiplier)
- `harvest.denda.config` — effective-dated penalty tables (event_type, rate_per_unit)

#### Key Features
1. Taksasi → auto-compute harvester/truck requirements → generate RKH
2. TPH capture with duplicate detection (same harvester/TPH/time → rejected)
3. Quality grading with photo evidence
4. Premi engine: formula-driven from config tables, daily statement per harvester
5. Denda offset against premi (with statutory floor protection → PLT-08)
6. BJR auto-derived from weighbridge (kg ÷ janjang at block level)

#### Tests
- Given basis 1,100 kg + premi tiers, harvester with 1,450 kg + 1 unripe penalty → premi calculated to the rupiah
- Duplicate TPH record → rejected
- Permi config change mid-period → only applies from effective date

---

### Sprint 1.2: PLT-06 — FFB Transport & Weighbridge (Weeks 12–15)
**Priority:** P0 | **Size:** M–L | **Dependencies:** PLT-01, PLT-05, PLT-12

#### Models
- `transport.spb` — Surat Pengantar Buah (number, date, truck_id [fleet.vehicle], driver_id, blocks[], tphs[], janjang_count, estimated_kg, seal_number, destination_mill_id, state: Issued→Weighed→Delivered→MillConfirmed→Closed)
- `transport.weighbridge_ticket` — weighbridge record (spb_id, gross_kg, tare_kg, net_kg, timestamp, operator_id, photo_fr, photo_rr, mode auto/manual)
- `transport.restan` — uncollected FFB (date, block_id, tph_id, janjang_count, estimated_kg, age_hours, escalated)

#### Key Features
1. SPB numbering: gap-controlled, auto-sequenced per period
2. Weighbridge integration: abstract service layer for indicator hardware (RS-232/TCP); manual mode requires EM approval + flagged
3. Restan daily report; > 24h escalates
4. Three-way reconciliation: SPB janjang/est-kg ↔ weighbridge net ↔ mill net (variance > 2–3% → SPI exception)

#### Tests
- SPB created without previous SPB closure → gap detected
- Manual weight input without EM approval → rejected
- Bridge net vs mill net variance 5% → exception logged

---

### Sprint 1.3: PLT-07 — TBS Sales & Mill Reconciliation (Weeks 14–17)
**Priority:** P0 | **Size:** M | **Dependencies:** PLT-06

#### Models
- `sales.mill` — customer master (name, pricing_basis, payment_terms, sortasi_rules)
- `sales.tbs_price` — effective-dated price table (market_price, disbun_price_by_age_band for plasma)
- `sales.mill_reception` — mill intake per SPB (spb_id, gross_kg, sortasi_deduction_kg, sortasi_deduction_pct, deduction_reasons, accepted_net_kg, mill_doc_ref)
- `sales.invoice_line` — auto-generated from accepted_net × price

#### Key Features
1. Mill reception capture from mill documents
2. Auto-match SPB → estate net → mill net
3. Revenue auto-distributed to block analytic (pro-rata by block weights)
4. Sortasi deduction trend analysis (feedback into PLT-05 quality)

#### Tests
- SPB with 5,000 kg × price Rp 2,500 → invoice Rp 12,500,000
- Deduction > 5% from same mandor 3 periods → exception flagged

---

### Sprint 1.4: PLT-08 — Plantation Payroll Indonesia (Weeks 15–20)
**Priority:** P0 | **Size:** L | **Dependencies:** PLT-04 (HK from BKM), PLT-05 (premi/denda), Odoo native `hr_payroll`

#### Models
- `payroll.worker_contract` — extends `hr.contract` with worker class (BHL/SKU/KHT/staff), PKWT/PKWTT type, wage_master_id
- `payroll.wage_master` — effective-dated minimum wage + piece rates
- `payroll.bpjs_config` — effective-dated BPJS rates (Kesehatan 5%/4+1, JHT 5.7%/3.7+2, JP 3%/2+1, JKK by class, JKM 0.3%)
- `payroll.pph21_config` — TER method tables, PTKP table, NPWP surcharge
- `payroll.salary_rule` — extends `hr.salary.rule` with plantation-specific rules (daily base × HK, premi additive, denda deductive, THR, natura)
- `payroll.payslip` — extends `hr.payslip` with premi formula breakdown

#### Key Features
1. Auto-feed HK from PLT-04 BKM, premi/denda from PLT-05
2. BPJS auto-calculation (employer + employee portions)
3. PPh 21 TER method + December annual true-up
4. Payroll journal auto-distributed to block analytic accounts
5. Payslips show premi formula components (Fairness/Transparansi)

#### Tests
- Worker with 25 HK × Rp 100,000 base + premi Rp 450,000 − denda Rp 25,000 − BPJS − PPh21 → net pay matches manual calc
- Ghost worker check: BKM-sourced HK only; worker bank account uniqueness

---

### Sprint 1.5: PLT-13 Core Reports (Weeks 18–20)
**Priority:** P0 core set | **Size:** M | **Dependencies:** PLT-05, PLT-06, PLT-07

#### Reports (MVP)
1. Daily production per block/mandor/harvester (janjang, kg, BJR)
2. Daily dispatch & weighbridge log
3. Daily restan report
4. Daily HK summary
5. LHM (Laporan Harian Mandor) auto-generated from BKM
6. Monthly yield/ha per block vs RKAP
7. Monthly cost per block & per kg TBS
8. Monthly premi & denda summary
9. Monthly mill reconciliation & sortasi analysis
10. Monthly budget vs actual (basic: actual costs vs budget)

---

### Phase 1 Exit Criteria
- [ ] ≥ 90% harvest data captured correctly with duplicate detection
- [ ] Premi payroll paid from system for 2 consecutive cycles, verified against manual
- [ ] Weighbridge/mill variance tracked and < 3% discrepancy flagged
- [ ] All P0 modules have test coverage ≥ 80%
- [ ] Integration test: taksasi → TPH capture → SPB → weighbridge → mill reception → invoice → payroll (end-to-end)

---

## Phase 2 — Upkeep, Planning & Plasma (Weeks 21–34)

**Goal:** Digital BKM for all non-harvest field work, planning cascade (RKH→RKB→RKAP), plasma farmer management. This is where the estate transitions from harvest-only digital to full digital operations.

### Sprint 2.1: PLT-04 — Upkeep/Agronomy Operations (Digital BKM) (Weeks 21–27)
**Priority:** P0 | **Size:** L | **Dependencies:** PLT-01, PLT-02 (partial — RKH needed), PLT-12

#### Key Models
- `upkeep.bkm` — Buku Kerja Mandor (date, mandor_id, rkh_id, block_id, activity_code, workers[], output_per_worker, materials_consumed[], gps_start, gps_end, photos[], state: Draft→Submitted→Verified→Approved→Posted)
- `upkeep.bpb` — Bon Permintaan Barang (number, date, requestor_id, items[], approved_by, issued_by, issued_qty, return_qty)
- `upkeep.activity_code` — standard activity catalog (pemupukan, semprot, tunasan, kastrasi, rawat_jalan, p&d_treatment)
- `upkeep.fertilizer_program` — recommendation per block (type, dose_per_pokok, round, realization vs recommendation)
- `upkeep.pd_census` — pest & disease monitoring (block_id, pest_type ganoderma/tikus/oryctes/ulat_api, severity, sample_count, photos)
- `upkeep.tyto_alba` — barn-owl box registry

#### Key Features
1. BKM state machine + maker–checker (mandor–asisten)
2. Material flow: BPB → store issue → BKM consumption → return (two-way match; variance → exception)
3. Fertilizer: program vs realization with 5T compliance tracking
4. P&D: monitoring + treatment work orders + IPM history
5. Piece-rate (borongan) output feeds worker pay lines → PLT-08
6. Validations: duplicate HK block, output > norm × 150%, dose outside tolerance

---

### Sprint 2.2: PLT-02 — Planning & Budgeting (Weeks 25–30)
**Priority:** P0 for RKH+RKB, P1 for RKAP | **Size:** M | **Dependencies:** PLT-01, PLT-04

#### Key Models
- `plan.norma_kerja` — standard norms (activity_code, output_per_hk, cost_per_unit, effective_from, effective_to)
- `plan.rkap` — annual plan per block × activity × month (physical_qty, hk, material_cost, total_cost, version, state: Proposed→Approved)
- `plan.rkb` — monthly plan (derived from RKAP; deviation > x% requires justification)
- `plan.rkh` — daily work order (parent of BKM; block, activity, target, workers[], planned_materials)

---

### Sprint 2.3: Fleet & Maintenance Rollout (Weeks 28–32)
**Objective:** Configure native Odoo `fleet` and `maintenance` for plantation context — not custom modules, but configuration + data load + integration with PLT-06 (transport) and PLT-01 (road/bridge assets).

### Sprint 2.4: PLT-09 — Plasma / Kemitraan Management (Weeks 28–34)
**Priority:** P2 → pulled to Phase 2 (active program) | **Size:** M | **Dependencies:** PLT-01, PLT-06, PLT-07

#### Models
- `plasma.farmer` — farmer registry (name, NIK, STDB, land_docs, plot_polygons, bank_account, koperasi_id)
- `plasma.koperasi` — cooperative registry
- `plasma.ffb_intake` — plasma FFB at weighbridge with supplier ID, priced from Disbun table
- `plasma.loan_ledger` — saprodi/advance loan entries with agreed deduction %
- `plasma.farmer_statement` — monthly statement (delivery, gross, deductions, net)
- `plasma.disbun_price` — effective-dated government price table by age band

#### Key Features
1. Farmer & koperasi registry with plot polygons (EUDR-ready)
2. Plasma FFB intake auto-priced from Disbun table by age band
3. Loan/deduction ledgers with configurable deduction %
4. Monthly farmer statement (printable, transparent — Fairness principle)
5. SIPERIBUN 6-monthly reporting pack

#### Tests
- Farmer with 3 deliveries × Disbun price Rp 2,200 = Rp X, minus 20% loan deduction → statement matches calculator
- Farmer statement immutable after posted; price applied = published Disbun table

---

### Phase 2 Exit Criteria
- [ ] 100% field work captured via BKM; BPB-controlled store issues
- [ ] Budget-vs-actual live per block
- [ ] Fleet costs allocated per trip to block
- [ ] Plasma farmer statements generated and matched against manual for 2 cycles

---

## Phase 3 — Compliance (Weeks 33–44)

### Sprint 3.1: PLT-10 — Compliance & Traceability (Weeks 33–38)
**Priority:** P1 | **Size:** M | **Dependencies:** PLT-01 (GIS), PLT-06 (SPB chain)

#### Key Models
- `compliance.ispo_evidence` — structured by 7 ISPO principles, each criterion → system record links + uploaded docs
- `compliance.eudr_export` — per-block polygon + production-period linkage → DDS-ready GeoJSON/CSV export
- `compliance.k3_incident` — incident/accident log with APD issue records
- `compliance.environmental` — HCV areas, riparian buffers, fire watch, chemical usage summary

---

### Sprint 3.2: PLT-12 Hardening (Weeks 36–40)
**Objective:** Harden all GCG controls from Phase 0 skeleton — full exception rules, period close enforcement, comprehensive role matrix.

---

### Phase 3 Exit Criteria
- [ ] ISPO readiness gap list produced from evidence register
- [ ] EUDR data pack exportable per block
- [ ] All P1 GCG controls active

---

## Phase 4 — Extended (Weeks 45+)

| Module | Priority | Description |
|--------|----------|-------------|
| PLT-03 | P2 | Nursery Management (seedling batches, culling, transfer to field) |
| PLT-11 | P0 (deferred) | Android offline-first mobile app (field capture for mandor/kerani) |
| PSAK 69 full | P2 | Fair-value models for biological asset standing valuation (cost routing built in Phase 0) |
| Weighbridge bridge | P1 (deferred) | Hardware bridge service for weighbridge indicator (estate-estimate mode in MVP) |

---

## Mobile App (PLT-11) — Deferred to Phase 4+

**Decision:** Mobile app deferred. All field data capture initially via Odoo web UI on tablets, with paper fallback + next-day office entry.

**When resumed (Phase 4+):** Architecture TBD (React Native recommended). Forms: TPH harvest capture, BKM entry, taksasi, inspections, SPB creation/scan. Offline-first: local queue, background sync, idempotent server writes. GPS + timestamp + photo auto-attach. ≤ 3 taps per common record, Bahasa Indonesia labels, Android 8+ / 2GB RAM.

---

## Cross-Cutting Requirements (All Phases)

### Testing Strategy (SDLC)
- **Unit tests:** Every model method, every computed field, every constraint → TDD (see `test-driven-development` skill)
- **Integration tests:** Module-to-module data flow (e.g., BKM → analytic posting → payroll → GL)
- **UAT per sprint:** Realistic datasets (1 afdeling, real block shapes, real worker list, real premi rates)
- **Regression:** Full suite runs on every PR merge

### Code Quality Gates
- Pre-commit: lint (ruff), Odoo module structure check via `requesting-code-review` skill
- PR review: mandatory spec compliance check + code quality review
- No Odoo core patching — all customizations via inheritance and `_inherit`

### Localization
- UI: Bahasa Indonesia (primary) + English toggle
- Currency: Rupiah (IDR)
- Tax: PPN 11%, PPh 23, Indonesian Chart of Accounts
- Date format: DD/MM/YYYY
- Number format: 1.234.567,89

### Security
- Role-based access (Odoo record rules) per afdeling
- SoD engine enforcement (PLT-12)
- TLS for all communication
- Daily off-site backups
- Audit log retention ≥ 10 years

---

## Resolved Decisions (9 July 2026)

| # | Question | Decision | Impact |
|---|----------|----------|--------|
| 1 | Weighbridge hardware | **Estate-estimate mode** for MVP. SPB carries estimated weight; reconciled at mill. Bridge integration deferred to later sprint. | PLT-06 simplified — no hardware bridge service needed for Phase 1. Manual weight entry with EM approval + flagging. |
| 2 | Mobile app framework | **Deferred.** Odoo backend modules first. Field data captured via Odoo web UI on tablets as interim; paper fallback with next-day office entry. | PLT-11 not in Phase 1 scope. Offline-first app becomes Phase 4+ workstream. |
| 3 | Buy vs build | **Build custom.** Fresh start with no legacy data, full control, and unique SOP requirements. Custom PLT suite built on Odoo 19 Enterprise. | Full build of all 13 modules. Evaluate existing modules as reference only. |
| 4 | PSAK 69 | **Build now in Phase 0.** Needed for TBM/TM cost capitalization logic in PLT-01. Fair-value templates integrated into block cost routing from day one. | Added PSAK 69 templates to Sprint 0.2 (PLT-01). Accountant/PSAK SME input needed during design. |
| 5 | Data migration | **Fresh start.** No existing data to migrate. Master data entered manually through Odoo UI. | Phase 0 timeline holds — no ETL workstream. Data stewardship role ensures quality at entry. |
| 6 | Plasma obligation | **Active.** Full plasma/kemitraan program. PLT-09 pulled from Phase 4 to Phase 2. | PLT-09 (farmer registry, Disbun pricing, loan ledgers, SIPERIBUN reports) now in Phase 2 alongside Upkeep & Planning. |

---

## Success Metrics

| Metric | Target | Measured When |
|--------|--------|---------------|
| FFB dispatches on numbered SPB with 3-way reconciliation | 100% | Phase 1 exit |
| Unexplained estate-vs-mill variance | < 2% | Phase 1+ |
| Field activities recorded digitally D+0 | ≥ 95% | Phase 2 exit |
| Payroll cycle time reduction | ≥ 50% vs manual | Phase 1+ 2 cycles |
| Premi disputes escalated beyond afdeling | Zero in last quarter | Phase 1+ |
| Cost per kg TBS & yield/ha per block | Available by D+3 | Phase 2 exit |
| ISPO evidence completeness | ≥ 90% on dashboard | Phase 3 exit |
| EUDR polygon coverage | 100% of producing blocks | Phase 3 exit |

---

*Plan last updated: 2026-07-09. Next: Confirm open questions above, then kick off Sprint 0.1.*
