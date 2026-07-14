# Product Requirements Document (PRD)
# Odoo Plantation Management Add-Ons — Kebun Kelapa Sawit (100–500 ha)

| Field | Value |
|---|---|
| Document | PRD — Custom Odoo Add-on Suite for Oil Palm Estate Management |
| Version | 1.0 (Draft for review) |
| Date | 02 July 2026 |
| Owner | Windalfin (Product Owner) |
| Platform | Odoo 17/18 Enterprise (recommended) + custom addons + offline-first mobile app |
| Scope | Single estate, 100–500 ha, full cycle: nursery → planting → upkeep → harvest → transport → sales to PKS |
| Governing frameworks | Standard estate SOP flow (RKT/RKB/RKH, BKM, taksasi–panen–TPH–SPB–weighbridge–mill) and GCG principles (TARIF per Pedoman Umum GCG / Permen BUMN PER-01/MBU/2011) |

---

## 1. Purpose & Background

This PRD defines the custom add-on modules ("PLT suite") to be built on top of Odoo to run a 100–500 ha oil palm estate end-to-end. Odoo natively provides Accounting/Analytic, Inventory, Purchasing, HR/Payroll engine, Fleet, Maintenance, and Project. It does **not** provide plantation concepts (blok, afdeling, tahun tanam, ancak, taksasi/AKP, premi panen, fraksi, SPB/weighbridge, TBS pricing, ISPO/EUDR traceability). Those gaps are the subject of this document.

Two non-negotiable design mandates apply to every module:

1. **The system enforces the standard/ideal plantation operating flow** — the widely used estate administration model: annual plan (RKT/RKAP) → monthly plan (RKB) → daily plan (RKH) → execution recorded by mandor in the Buku Kerja Mandor (BKM) → verified by asisten afdeling → consolidated into division daily/monthly reports (LHM/LKM, Laporan Bulanan Divisi). Materials only move against an approved Bon Permintaan Barang (BPB); harvested FFB only moves against a numbered Surat Pengantar Buah (SPB); every kilogram is reconciled estate-weighbridge-vs-mill.

2. **The system embeds GCG (Good Corporate Governance)** — the five TARIF principles: **T**ransparansi, **A**kuntabilitas, **R**esponsibilitas, **I**ndependensi, **F**airness. In system terms this translates to: single source of truth with immutable audit trail (Transparansi); every transaction has a named maker, checker, and approver per an Authority Matrix (Akuntabilitas); statutory compliance is built in — BPJS, PPh 21, ISPO, environmental & K3 records (Responsibilitas); segregation of duties so no role can create, approve, and pay the same transaction (Independensi); and rule-based, formula-driven premi/wages and plasma pricing so workers and partners are paid by transparent published rules (Fairness).

### 1.1 Objectives
- Digitize 100% of daily field administration (BKM, harvest records, weighbridge tickets) with offline-capable mobile capture.
- Enforce maker–checker–approver on all cost, payroll, and dispatch transactions.
- Produce cost-per-block, cost-per-kg-TBS, yield/ha, and budget-vs-actual (RKAP) automatically.
- Make the estate audit-ready: ISPO principle evidence, EUDR geolocation, SPI/internal-audit trails.
- Close the classic leakage points: unverified harvest counts, phantom workers (HK fiktif), unauthorized FFB movement (theft/penadah), weighbridge manipulation, and unreconciled mill sortasi deductions.

### 1.2 Out of Scope (v1)
- Palm oil mill (PKS) processing — the estate sells FFB to third-party mills.
- Multi-estate consolidation, replanting program management, drone/satellite analytics (future).
- Full PSAK 69 fair-value automation (policy configuration only; valuation entries remain manual journal with template).

---

## 2. Reference Frameworks (What "We Will Follow")

### 2.1 Standard / Ideal Estate Operating Flow (SOP baseline)
The suite implements the canonical Indonesian estate administration cycle:

**Planning cascade**
- **RKT / RKAP** (Rencana Kerja Tahunan / Rencana Kerja & Anggaran Perusahaan): annual work plan and budget per block and activity, drafted by Asisten + Askep + Estate Manager, approved by Direksi.
- **RKB** (Rencana Kerja Bulanan): monthly breakdown, approved by Estate Manager.
- **RKH** (Rencana Kerja Harian): daily work orders per mandor team, drafted by Asisten Afdeling.

**Execution & recording**
- **BKM** (Buku Kerja Mandor): the mandor's daily record — workers present, block, activity, output (ha, patok, tanks, kg), materials used. Signed (digitally) by mandor and countersigned by asisten. This is the single source for HK (hari kerja), piece-rate output, and material consumption.
- **BPB** (Bon Permintaan Barang): material requisition raised by asisten, approved by Estate Manager, issued by Kepala Gudang against the approved BPB only.

**Harvest chain**
- **Taksasi / AKP** (Angka Kerapatan Panen): D-1 crop estimate per block section → determines tomorrow's harvester count, ancak allocation, and truck requirement.
- **Panen**: harvest by ancak (tetap or giring), rotation target 6/7–9/10 days; ripeness by fraksi standard (minimum brondolan criterion); harvester number written on the stalk.
- **TPH**: bunches lined and counted at Tempat Pengumpulan Hasil by kerani panen/KCS per harvester; quality graded (fraksi, unripe, empty bunch, long stalk, brondolan collected); penalties (denda) recorded.
- **Mutu ancak & mutu buah checks**: mandor inspects ancak completeness; mandor I / asisten performs sampling checks — recorded as inspections.
- **SPB / Surat Pengantar Buah (TBS)**: numbered dispatch note per truck — vehicle, driver, blocks, janjang count, estimated tonnage. No FFB leaves the estate without an SPB.
- **Weighbridge**: gross/tare/net weight per ticket, tied to the SPB.
- **Mill reception**: mill weight + sortasi/grading deductions captured and reconciled against estate figures ticket-by-ticket.

**Reporting**
- **LHM** (Laporan Harian Mandor) auto-generated from BKM; **Laporan Harian/Bulanan Divisi** auto-consolidated; production, HK, materials, and cost roll up to block analytic accounts daily.

### 2.2 GCG Framework (TARIF) → System Control Requirements
Following the Pedoman Umum GCG Indonesia (KNKG) and Permen BUMN PER-01/MBU/2011 as adopted by plantation companies (PTPN-style governance instruments: Code of Corporate Governance, Board Manual, Code of Conduct, Internal Audit/SPI Charter):

| GCG Principle | System Requirement |
|---|---|
| **Transparansi** | Immutable audit log on all plantation transactions; published premi/wage formulas visible to payroll and workers' slips; dashboards accessible per role; document register for legality/compliance docs. |
| **Akuntabilitas** | Authority Matrix (Delegation of Authority) configurable by transaction type and value; named maker–checker–approver on BKM, BPB, SPB, weighbridge tickets, premi runs, price masters; e-signature/timestamp on approvals. |
| **Responsibilitas** | Statutory engines: BPJS Kesehatan & Ketenagakerjaan, PPh 21 (TER), THR; ISPO evidence register (7 principles); K3 incident log; environmental/HCV records; EUDR geolocation per block. |
| **Independensi** | Segregation of duties enforced by role: the recorder of harvest (kerani) ≠ approver (asisten) ≠ payer (KTU/payroll); weighbridge operator cannot edit SPB; gudang cannot approve its own BPB; SPI (internal audit) role has read-all + exception reports but no transaction rights. |
| **Fairness** | Formula-driven premi/denda applied identically to all harvesters; TBS purchase from plasma at the government-set Disbun price table; grievance/whistleblowing intake channel logged. |

**Key anti-fraud controls the system must implement** (responding to the sector's known leakage patterns — FFB theft/penadah networks, phantom HK, weighbridge games):
- No un-numbered SPB; SPB quantity vs weighbridge net vs mill accepted weight three-way reconciliation with tolerance thresholds and automatic exception flags.
- Geo/time-stamped mobile capture of harvest records at TPH.
- Duplicate-worker and impossible-productivity detection on BKM (e.g., output > physical norm ×150%).
- Locked master data (block areas, premi rates, TBS price tables) — changes only via approval workflow with effective-dating and history.
- Daily restan (uncollected FFB) report; FFB older than 24h at TPH escalates.

---

## 3. Solution Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                     Odoo (Enterprise)                       │
│  Native: Accounting/Analytic • Inventory • Purchase •      │
│  HR/Payroll engine • Fleet • Maintenance • Documents       │
├────────────────────────────────────────────────────────────┤
│  PLT Custom Add-on Suite                                    │
│  PLT-01 Estate Master  PLT-02 Plan/Budget  PLT-03 Nursery  │
│  PLT-04 Upkeep Ops     PLT-05 Harvest      PLT-06 Transport│
│  PLT-07 TBS Sales      PLT-08 Payroll-ID   PLT-09 Plasma   │
│  PLT-10 Compliance     PLT-12 GCG Control  PLT-13 Reports  │
├────────────────────────────────────────────────────────────┤
│  PLT-11 Mobile Field App (offline-first, Android)          │
│  Weighbridge bridge service (indicator → Odoo API)         │
└────────────────────────────────────────────────────────────┘
```

**Backbone design decisions**
- Every **block = one Odoo analytic account**; every PLT transaction posts analytic lines automatically (labor HK cost, materials, transport) → cost per block / per kg TBS with zero re-keying.
- Every field document (RKH, BKM, SPB, weighbridge ticket, inspection) is a first-class Odoo record with chatter, state machine (Draft → Submitted → Verified → Approved → Posted/Locked), and full mail.thread audit trail.
- TBM/TM status on the block drives account routing: TBM activity costs → capitalized to biological asset WIP; TM costs → P&L harvesting/upkeep expense (PSAK 69-ready).
- Mobile app is capture-only (no approvals in the field app v1); sync is idempotent, conflict-safe, and queued offline.

---

## 4. Module PRDs

Priorities: **P0** = MVP (go-live blocker), **P1** = fast-follow, **P2** = later phase.
Sizing: S ≈ 2–4 dev-weeks, M ≈ 4–8, L ≈ 8–16 (single experienced Odoo dev equivalent, excl. QA/UAT).

---

### PLT-01 — Estate Master Data & Land Registry  *(P0, size M)*

**Purpose.** Single source of truth for the physical estate and its legality. Everything else references it.

**Users.** Estate Manager, Askep, Asisten, Admin/KTU, SPI (read), Compliance officer.

**Functional requirements**
1. Hierarchy: Estate → Afdeling/Divisi → Blok → Ancak (optional sub-division). Block auto-creates a linked analytic account.
2. Block attributes: area statement (ha planted / ha total), tahun tanam, seed source (kecambah origin & batch), SPH, planting density, soil/topography class, **status TBM/TM with dated status history** (status change requires Estate Manager approval — drives cost capitalization).
3. Palm census (sensus pokok): periodic census records per block — productive, unproductive, dead, vacant points, sisipan; census variance vs prior period highlighted.
4. GIS: GeoJSON polygon per block (≥6-decimal coordinates), map view, auto area calculation vs declared area (variance flag > 3%) — this is the EUDR/ISPO geolocation backbone.
5. Land legality register: parcel records (SHM/HGU number, holder name, area, location) linked to blocks; document types STDB/IUP/HGU/SHM/izin lingkungan with number, issue date, expiry, scanned file (Odoo Documents); expiry alerts at 12/6/3 months. **Name-consistency validation**: holder names must match across linked documents; mismatches (e.g., spelling variants of the same person) are flagged for legal review rather than silently accepted.
6. TPH registry per block with GPS point; gudang/warehouse registry; road/bridge asset registry (feeds Maintenance).

**GCG controls.** Master data changes are workflow-approved (maker: admin; approver: Estate Manager) and effective-dated; full change history; block area and analytic mapping locked after activation.

**Acceptance criteria (sample).** Creating a block generates its analytic account; a TM flip on 01/mm reroutes that block's costs from asset WIP to P&L from that date; legality doc expiring in <90 days appears on the compliance dashboard.

---

### PLT-02 — Planning & Budgeting (RKAP / RKB / RKH)  *(P0 for RKH+RKB, P1 for full RKAP, size M)*

**Purpose.** Digitize the planning cascade and lock execution to plan.

**Functional requirements**
1. **Norma kerja master**: standard output & cost norms per activity (e.g., pemupukan kg/HK, semprot ha/HK, panen basis kg/HK by tahun tanam), effective-dated, approval-controlled.
2. **RKT/RKAP**: annual plan per block × activity × month: physical quantity, HK, materials, cost; versioning (proposed → approved by Direksi); becomes the Odoo budget on the block analytic accounts.
3. **RKB**: monthly derivation from RKAP with adjustment workflow (asisten proposes, Estate Manager approves; deviation > x% from RKAP requires justification note).
4. **RKH**: daily work orders per mandor team: block(s), activity, target output, assigned workers, planned materials (pre-fills BPB), planned HK. RKH is the parent of tomorrow's BKM.
5. Budget vs actual: physical (ha, kg, janjang) and financial, per block/afdeling/estate, monthly and YTD; overspend beyond tolerance blocks further BPB for that activity-block unless Estate Manager overrides (logged).

**GCG controls.** Plan approval hierarchy per Authority Matrix; overrides always logged with reason; RKAP versions immutable.

---

### PLT-03 — Nursery Management (Pembibitan)  *(P2, size S–M)*

**Purpose.** Manage seedling production from kecambah receipt to field planting (needed only if estate raises its own seedlings; otherwise procurement of seedlings via native Purchase).

**Functional requirements**
1. Kecambah receipt as inventory lots (source, variety, certificate doc, quantity).
2. Pre-nursery → main-nursery transplant transactions; batch cards (kartu bibit) tracking age, treatments (watering, fertilizing, spraying via PLT-04 activities on nursery "blocks").
3. Seleksi/culling records with reason codes; mortality %; apkir destruction record (two-person sign-off — GCG: prevents culled-seedling leakage).
4. Bibit siap tanam release: transfer order to destination block, updating block census (sisipan/new planting).
5. Cost accumulation per batch → unit cost per seedling → carried into TBM capitalization of the receiving block.

---

### PLT-04 — Upkeep / Agronomy Operations (Digital BKM)  *(P0, size L)*

**Purpose.** The digital Buku Kerja Mandor: all non-harvest field work — pemupukan, semprot/weeding, pruning/tunasan, kastrasi, rawat jalan/piringan, pest & disease.

**Functional requirements**
1. **BKM record** (mobile-first): date, mandor, RKH reference, block, activity code, workers (from HR, with attendance status), output per worker (ha/patok/tanks/kg/pokok), materials consumed (auto-drawn from the approved BPB issue), start/end geo-timestamps, photos.
2. **State machine**: Draft (mandor) → Submitted → Verified (asisten checks in the field/office) → Approved (askep/EM for exceptions) → Posted (creates analytic cost lines: labor HK × wage rate + materials + equipment hours).
3. **Material flow**: RKH pre-generates BPB (asisten submits → Estate Manager approves → gudang issues against BPB only; issue quantity cannot exceed approved BPB; returns (retur) recorded). Chemical/fertilizer usage per block is reconciled: issued vs applied vs returned; variance > tolerance flags exception.
4. **Fertilizing specifics**: program per block (rekomendasi pemupukan: type, dose/pokok, round); realization vs recommendation (5T compliance: tepat jenis/dosis/waktu/cara/tempat); untilan/ecer tracking to TPP.
5. **Pest & disease (P&D)**: census/monitoring records per block (Ganoderma, tikus, Oryctes, ulat api) with severity, sample counts, photos; treatment work orders; barn-owl (Tyto alba) box registry; IPM history per block (ISPO Principle 2/3 evidence).
6. **Piece-rate (borongan) support**: activity output feeds worker piece-rate pay lines into PLT-08.
7. Validations: worker cannot appear in two BKM on the same day (duplicate-HK block); output beyond norma × configurable ceiling requires asisten override with reason; material dose outside recommendation ± tolerance flags.

**GCG controls.** Maker–checker (mandor–asisten) on every BKM; phantom-worker analytics; chemical issue/return two-way match; posted BKM immutable (corrections via reversal document only).

---

### PLT-05 — Harvest Management (Panen, Premi & Denda)  *(P0, size L — the heart of the system)*

**Purpose.** Run the full harvest chain: taksasi → ancak assignment → harvest capture at TPH → quality inspection → premi/denda calculation.

**Functional requirements**
1. **Taksasi/AKP (D-1)**: sample-based crop estimate per block section (pokok sampled, bunches counted → AKP → estimated janjang & tonnage); auto-computes required harvesters (vs basis) and trucks; output becomes tomorrow's harvest RKH.
2. **Seksi & rotation management**: blocks grouped into harvest sections (typically 6 for 6/7 rotation); rotation calendar auto-tracks interval per block; dashboard flags rotation > target (e.g., >9 days) — over-rotation is a fruit-quality and theft risk signal.
3. **Ancak assignment**: ancak tetap or giring per mandor policy; daily harvester-to-ancak allocation stored (accountability for ancak completeness).
4. **Harvest capture at TPH (mobile, offline)**: per harvester per TPH: janjang count, brondolan (kg or karung), timestamp+GPS; kerani panen is the maker. BJR auto-derived later from weighbridge actuals (block-level BJR = net kg ÷ janjang).
5. **Quality grading & denda**: per-harvester quality events per company denda table: buah mentah (unripe), tangkai panjang (long stalk), brondolan tidak dikutip, buah tinggal/tidak dipanen, pelepah sengkleh; each with photo evidence option and rate.
6. **Mutu ancak / mutu buah inspections**: structured sampling inspections by mandor panen, mandor I, asisten with scored checklists; results linked to harvester/mandor scorecards.
7. **Premi engine (configurable formula tables, effective-dated, approved)**:
   - Basis borong per block class/tahun tanam (kg or janjang per HK).
   - Premi siap borong + premi lebih borong tiers (Rp/kg or Rp/janjang above basis); proportional pay below basis for justified cases.
   - Premi brondolan (Rp/kg); premi mandor & kerani (multiplier of team average / % of collection).
   - Denda offsets from (5); daily premi statement per harvester visible on supervisor app (Fairness: transparent calculation).
8. **Outputs**: daily harvest report per block/mandor/harvester; premi batch → PLT-08 payroll input lines; production quantity → block analytic & inventory (FFB stock at TPH).

**GCG controls.** Kerani records, mandor confirms, asisten approves (3 distinct users enforced); janjang at TPH vs janjang on SPB vs weighbridge tonnage cross-checks; premi rate tables locked & versioned; per-harvester statements auditable line-by-line.

**Acceptance criteria (sample).** Given basis 1,100 kg and premi tiers configured, a harvester delivering 1,450 kg with one unripe-bunch penalty produces a premi line equal to the published formula to the rupiah, traceable to TPH records; a second identical TPH record for the same harvester/TPH/time is rejected as duplicate.

---

### PLT-06 — FFB Transport & Weighbridge (SPB / Timbangan)  *(P0, size M–L)*

**Purpose.** Control FFB movement from TPH to mill: no fruit moves without papers; every kg reconciled.

**Functional requirements**
1. **SPB (Surat Pengantar Buah)** — numbered, gap-controlled document series: date, truck (Fleet vehicle), driver, block(s)/TPH(s) loaded, janjang count, estimated kg, seal number (optional), destination mill; printed/QR version travels with the truck; states: Issued → Weighed (estate) → Delivered → Mill-confirmed → Closed.
2. **Weighbridge integration** (if estate owns a bridge; else estate-estimate mode): bridge service reads the indicator (RS-232/TCP) and posts gross/tare/net to the SPB ticket — operator cannot type weights manually except in approved offline-failure mode (flagged, requires EM approval). Photos/ANPR optional.
3. **Restan management**: FFB at TPH not loaded same day = restan; daily restan report by block with age; >24h restan escalates (ALB/quality risk).
4. **Trip & fleet economics**: trips per truck, tonnage, km, fuel (native Fleet) → transport cost per kg allocated to blocks.
5. **Internal-move mode** for estates delivering via agents/collection points: chain of custody preserved (EUDR requirement).

**GCG controls.** SPB numbering with gap audit; weight fields system-written; three-way reconciliation SPB janjang/est-kg ↔ estate weighbridge net ↔ mill accepted net with tolerance thresholds (e.g., >2–3% variance auto-exception to SPI dashboard); driver/vehicle master locked; unauthorized-exit report (gate log vs SPB).

---

### PLT-07 — TBS Sales, Pricing & Mill Reconciliation  *(P0, size M)*

**Purpose.** Turn dispatched FFB into correct, reconciled revenue.

**Functional requirements**
1. **Mill/customer master** with contract terms (pricing basis, payment terms, sortasi rules).
2. **TBS price master**: effective-dated price tables — market/negotiated price and, for plasma-partnered volumes, the Disbun government-set table by tahun-tanam age band (Permentan 01/2018 mechanism: CPO/kernel reference × rendemen × Indeks-K); price changes are approval-controlled.
3. **Mill reception capture**: mill weight, sortasi/grading deduction (%, kg, reason: mentah, busuk, tangkai panjang, sampah), accepted net, per SPB ticket — entered from mill documents or mill portal import.
4. **Reconciliation & invoicing**: auto match SPB ↔ estate net ↔ mill net; generate sales invoice per period per mill from accepted quantities × applicable price; deduction analytics by reason and by block/mandor (feedback loop into PLT-05 quality).
5. Revenue posts to estate/block analytic (pro-rata by dispatched block weights).

**GCG controls.** Price master approval + history; invoice quantities system-derived (no free-typed tonnage); sortasi deduction trend report (abnormal mill deductions are a negotiation/fraud signal); credit-limit & receivable aging on mills.

---

### PLT-08 — Plantation Payroll Indonesia  *(P0, size L)*

**Purpose.** Pay every worker class correctly and lawfully: BHL, SKU/KHT, staff, borongan — with premi panen integrated from field data.

**Functional requirements**
1. **Worker classes & contracts**: BHL (daily casual), SKU/KHT (permanent daily), monthly staff; PKWT/PKWTT contract records; wage masters effective-dated (regional minimum wage compliance check).
2. **Inputs auto-fed**: HK & attendance from BKM (PLT-04), premi/denda batches from harvest (PLT-05), piece-rate lines from upkeep borongan; manual inputs (leave, overtime for workshop/drivers) via HR.
3. **Salary rules**: daily base pay × verified HK; premi additive; denda deductive (with statutory floor protections); THR; natura/catu beras if applicable.
4. **Statutory engines** (configurable rates, effective-dated):
   - BPJS Kesehatan 5% (4% employer / 1% employee, ceiling per regulation).
   - BPJS Ketenagakerjaan: JHT 5.7% (3.7/2), JP 3% (2/1, ceiling), JKK by risk class (plantation class configurable), JKM 0.3%.
   - PPh 21 monthly TER method + December annual Pasal 17 true-up; PTKP table; no-NPWP surcharge.
5. **Payment**: bank file export / cash payout list per afdeling with signed (digital) receipt list; payslips show premi formula components (Fairness/Transparansi).
6. Posting: payroll journal auto-distributed to block analytic accounts based on where the HK was worked.

**GCG controls.** Payroll run: prepared by payroll admin → verified by KTU → approved by Estate Manager; no self-approval; variance report vs previous period > threshold requires note; ghost-worker controls (BKM-sourced HK only, worker bank account uniqueness check).

---

### PLT-09 — Plasma / Kemitraan Management  *(P2 — mandatory if plasma obligation applies, size M)*

**Purpose.** Manage smallholder partners: registry, FFB intake, government pricing, loans, and statements.

**Functional requirements**
1. Plasma farmer & koperasi registry: identity, STDB, land docs, plot polygons (EUDR), bank account.
2. Plasma FFB intake at weighbridge with supplier identification; purchase priced from the Disbun table by age band automatically.
3. Loan/saprodi advance ledgers with agreed deduction % per payment; monthly farmer statement (delivery, price, gross, deductions, net — printable, transparent).
4. Kemitraan reporting pack (supports SIPERIBUN 6-monthly reporting).

**GCG controls.** Deduction rules contract-bound and approval-controlled; farmer statements immutable; price applied = published government table (Fairness).

---

### PLT-10 — Compliance & Traceability (ISPO / EUDR / Legality)  *(P1, size M)*

**Purpose.** Make audits a query, not a project.

**Functional requirements**
1. **ISPO evidence register** structured by the 7 principles (legality; GAP; environment; labor/K3; social; traceability; continuous improvement): each criterion maps to system records (e.g., GAP → PLT-04 histories; labor → contracts & payroll; traceability → SPB chain) plus uploadable documents for non-system evidence; audit-readiness dashboard with gap list.
2. **EUDR pack**: per-block (and per-plasma-plot) geolocation polygons ≥6 decimals; production-period linkage of every dispatch to source blocks; export of geolocation + supply data in DDS-ready format (GeoJSON/CSV).
3. **K3 module-lite**: APD issue records (from inventory), incident/accident log, training/sosialisasi attendance.
4. **Environmental records**: HCV areas, riparian buffers on map; fire watch log; chemical usage summary (from PLT-04) for restricted-substance reporting.
5. Legality expiry dashboard (from PLT-01).

---

### PLT-11 — Mobile Field App (Offline-First)  *(P0, size L)*

**Purpose.** The capture surface for mandor/kerani in no-signal conditions.

**Functional requirements**
1. Android app; role-based forms: BKM (upkeep), TPH harvest capture, taksasi, inspections (mutu ancak/buah, P&D census), SPB creation/scan.
2. Offline-first: local queue, background sync, idempotent server writes, conflict rules (server wins on masters, field wins on captures with review flag).
3. Auto-attach GPS + timestamp + user; photo capture with compression; QR scan (worker ID cards, TPH plates, SPB).
4. Master data sync-down (workers, blocks, rates) scoped to the user's afdeling; device registry & remote wipe of local data on de-registration.
5. UX constraints: ≤3 taps per common record, large touch targets, Bahasa Indonesia labels, works on low-end devices.

**Non-functional.** Sync of a full day's afdeling data < 2 min on 3G; app works ≥3 days fully offline; all traffic TLS; local storage encrypted.

---

### PLT-12 — GCG & Internal Control Layer (Cross-Cutting)  *(P0 skeleton with MVP, hardened P1, size M)*

**Purpose.** The governance spine over all modules — this is where "we follow GCG" is enforced technically.

**Functional requirements**
1. **Authority Matrix / Delegation of Authority engine**: configurable approval routes per document type and value band (e.g., BPB ≤ Rp X: asisten; > Rp X: Estate Manager; price masters: Direksi); enforced across all PLT modules; matrix itself is version-controlled and approved.
2. **Segregation-of-duties (SoD) rules**: role conflict matrix (e.g., gudang ⛔ approve BPB; weighbridge operator ⛔ edit SPB; payroll admin ⛔ approve payroll); violations blocked at role-assignment time.
3. **Immutable audit**: mail.thread on all models + append-only audit log of critical field changes (who/when/old/new); posted documents locked, corrections via reversal.
4. **Exception & red-flag dashboard (for SPI/internal audit and management)**: weighbridge variance > tolerance, restan > 24h, rotation > target, HK anomalies, chemical variance, SPB gaps, premi outliers, master-data changes, override log.
5. **Whistleblowing/grievance intake**: simple case log (channel, anonymized option, status, resolution) — supports GCG code-of-conduct and ISPO social criteria.
6. Period close & locking: monthly close checklist (all BKM posted, SPB reconciled, payroll posted) before accounting period lock.

---

### PLT-13 — Reporting & KPI Dashboards  *(P0 core set, P1 full, size M)*

**Core reports (MVP).**
- Daily: production per block/mandor/harvester (janjang, kg, BJR), dispatch & weighbridge log, restan, HK summary, LHM.
- Monthly: yield/ha per block (vs RKAP), cost per block & per kg TBS, premi & denda summary, mill reconciliation & sortasi deduction analysis, budget vs actual, fertilizer realization vs program.
- KPIs: t FFB/ha (annualized), BJR trend, rotation days, harvester kg/HK, cost/kg, estate-vs-mill weight variance %, ALB-risk proxy (restan aging), TBM cost accumulation per ha.

**Finance layer.** TBM capitalization report per block (PSAK 69 support), TM P&L per block, extraction-value estimate.

---

## 5. Cross-Cutting Non-Functional Requirements

| Area | Requirement |
|---|---|
| Localization | UI Bahasa Indonesia (primary) + English; Rupiah; Indonesian CoA & tax config |
| Security | Role-based access per module matrix; record rules per afdeling; SoD engine (PLT-12); TLS everywhere; daily off-site backups; audit log retention ≥ 10 years (legal/ISPO horizon) |
| Availability | Server downtime must never stop field capture (offline app); RPO ≤ 24h, RTO ≤ 8h |
| Performance | Daily posting for 500 ha (~50–150 workers, ~20–60 BKM/TPH docs/day) processed < 5 min batch |
| Data quality | Mandatory-field enforcement at capture; master-data stewardship role; no free-text where a master exists |
| Extensibility | Clean addon boundaries (each PLT = separate Odoo module with defined dependencies); no core-Odoo patching |

## 6. Roles & Authority Matrix (Baseline)

| Role | Key rights (make / check / approve) |
|---|---|
| Mandor / Kerani (field) | Make: BKM, TPH capture, taksasi, SPB draft |
| Asisten Afdeling | Check/verify field docs; make RKH, BPB; approve BKM |
| Askep | Approve exceptions, inspections QA |
| Estate Manager | Approve BPB, RKB, payroll, SPB series, master changes; overrides |
| Kepala Gudang | Issue against approved BPB only |
| Weighbridge operator | Weigh only; no SPB edit |
| KTU / Payroll admin | Prepare payroll, postings; no approval |
| Direksi / Owner | Approve RKAP, price masters, authority matrix |
| SPI / Internal audit | Read-all + exception dashboards; no transactions |

## 7. Implementation Roadmap

| Phase | Months | Content | Exit criteria |
|---|---|---|---|
| 0 — Foundations | 0–2 | Odoo setup, CoA, analytic plan, PLT-01, PLT-12 skeleton (roles/DoA), master data load | Blocks + workers live; approval routes tested |
| 1 — Harvest-to-Cash MVP | 2–5 | PLT-05, PLT-06, PLT-07, PLT-08, PLT-11 (harvest forms), PLT-13 core | ≥90% harvest captured on mobile; premi payroll paid from system 2 cycles; weighbridge/mill variance < 3% tracked |
| 2 — Upkeep & Planning | 5–8 | PLT-04 full BKM, PLT-02 (RKH/RKB→RKAP), PLT-11 upkeep forms, Fleet/Maintenance rollout | All field work digital; BPB-controlled store issues; budget-vs-actual live |
| 3 — Compliance | 8–11 | PLT-10 (ISPO register, EUDR polygons/export), K3/environment logs, PLT-12 hardening | ISPO readiness gap list produced; EUDR data pack exportable |
| 4 — Extended | 11+ | PLT-03 nursery, PLT-09 plasma, PSAK 69 templates, advanced analytics | As applicable |

**Pull-forward triggers:** buyer mill exports to EU → PLT-10 EUDR into Phase 1; ISPO audit scheduled → PLT-10 into Phase 2; active plasma obligation → PLT-09 into Phase 2/3.

## 8. Team & Effort (Indicative)

- 1 Odoo tech lead/architect, 2 Odoo backend devs, 1 mobile dev, 1 BA/QA with estate-operations knowledge (critical), part-time agronomy SME & accountant (PSAK/tax).
- Indicative build effort: ~55–75 dev-weeks across phases 0–3; weighbridge bridge service +2–4 weeks per indicator brand.
- Buy-vs-build note: evaluate Indonesian vendor modules (Witech, Pro-Int checkroll, Portcities) against PLT-04/05/06/08 before building — license + gap-customization may beat green-field on cost and time; this PRD then serves as the acceptance/gap checklist.

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Field adoption fails (mandor resistance, device issues) | ≤3-tap UX, offline reliability, phased pilot on 1 afdeling, premi visibility as user incentive, paper fallback with next-day entry SLA |
| Premi/denda rules disputed | Rates published in-app and on payslips; formal approval of rate tables; parallel-run vs manual for 2 cycles |
| Weighbridge hardware variance | Abstract bridge service per indicator protocol; certified manual-mode with dual sign-off as fallback |
| Regulation drift (ISPO implementing rules, TBS pricing revision, BPJS/PPh rates) | All statutory rates & tables effective-dated and configurable, never hard-coded |
| Data quality at cutover (block areas, worker masters, legality docs with name inconsistencies) | Dedicated data-cleansing workstream in Phase 0 with sign-off per dataset |
| Scope creep toward mill/multi-estate | Change-control board; out-of-scope list enforced |

## 10. Success Metrics (12 months post go-live)

- 100% of FFB dispatches on numbered SPB with three-way reconciliation; unexplained estate-vs-mill variance < 2%.
- ≥95% of field activities recorded digitally D+0; payroll cycle time reduced ≥50%; zero premi disputes escalated beyond afdeling in last quarter.
- Cost per kg TBS and yield/ha per block available by D+3 monthly close.
- ISPO document/evidence completeness ≥90% on audit-readiness dashboard; EUDR polygon coverage 100% of producing blocks.

---
*Prepared as the baseline PRD; each PLT module should receive a detailed functional spec (field-level, screen-level) during its phase kickoff.*
