# 🌴 Koobun — Plantation Management Suite for Odoo 19

A complete, open-source plantation management system built as an Odoo 19 Enterprise addon suite. Designed for **oil palm estates** (100–500 ha) in Indonesia, covering everything from land registry to harvest-to-cash, payroll, and compliance.

---

## ✨ Features at a Glance

| Module | Phase | What It Does |
|--------|-------|--------------|
| `plt_estate` | Foundation | Estate master data: afdeling, blocks, ancak, TPH, land registry, census |
| `plt_gcg` | Foundation | Governance: authority matrix, segregation of duties, audit log, whistleblowing |
| `plt_harvest` | Harvest | Taksasi, TPH capture, quality scoring, premi/denda, inspections |
| `plt_transport` | Harvest | SPB (surat perintah bongkar), weighbridge, restan, reconciliation |
| `plt_sales` | Harvest | TBS pricing, mill reception, sortasi analysis, invoicing, revenue distribution |
| `plt_payroll` | Harvest | Worker contracts, wage master, BPJS, PPh21, THR, PTKP, payslips |
| `plt_upkeep` | Operations | Digital BKM (buku kerja mandor), BPB, fertilizer programs, P&D census |
| `plt_planning` | Planning | RKAP, RKB, RKH, norma kerja, budget vs actual |
| `plt_plasma` | Partnership | Plasma/farmer management, koperasi, FFB intake, disbun pricing, loans |
| `plt_compliance` | Compliance | ISPO evidence, EUDR geolocation, K3 incidents, APD tracking, environmental |
| `plt_nursery` | Extended | Nursery batches, seedling tracking, culling, transfers |
| `plt_reporting` | Reporting | SQL-based dashboards: daily production, yield, restan, cost, LHM, payslip summary |

**277 automated tests** · **0 failures** · **100% Bahasa Indonesia UI**

---

## 📋 Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| PostgreSQL | 14+ |
| Odoo | 19.0 Enterprise (community may work with minor adjustments) |
| OS | Linux (Ubuntu 22.04+ recommended) |

---

## 🚀 Quick Install (Development)

```bash
# 1. Clone the repo into your Odoo addons directory
cd /path/to/odoo-data/addons/
git clone git@github.com:windalfin/koobun.git 19.0

# 2. Make sure Odoo can find the addons
# In your odoo.conf:
#   addons_path = /path/to/odoo/addons,/path/to/odoo-data/addons/19.0

# 3. Install via Odoo (UI or CLI)
odoo -d your_db -i plt_estate --stop-after-init
```

### Install All 12 Modules at Once

```bash
odoo -d your_db \
  --init=plt_estate,plt_gcg,plt_harvest,plt_transport,plt_sales,plt_payroll,plt_upkeep,plt_planning,plt_plasma,plt_compliance,plt_nursery,plt_reporting \
  --stop-after-init
```

---

## 🏗️ Install (Production)

### 1. System Setup

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y python3 python3-venv python3-pip postgresql libpq-dev

# Create Odoo system user
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Start PostgreSQL
sudo systemctl enable postgresql
```

### 2. Odoo 19 Installation

```bash
sudo su - odoo

# Python virtual environment
python3 -m venv odoo-venv
source odoo-venv/bin/activate
pip install odoo --find-links=https://nightly.odoo.com/19.0/nightly/deb/
# Or install from source:
# git clone https://github.com/odoo/odoo.git --depth 1 -b 19.0 odoo-src
```

### 3. Deploy Koobun

```bash
# Clone into addons
cd ~/addons/19.0
git clone git@github.com:windalfin/koobun.git plt_management
```

### 4. Configuration (`odoo.conf`)

```ini
[options]
addons_path = /opt/odoo/odoo-src/odoo/addons,/opt/odoo/addons/19.0
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_db_password
admin_passwd = your_master_password
http_port = 8069
workers = 4
```

### 5. Create Database & Install

```bash
# Create a new database
createdb -U odoo your_estate_db

# Install all PLT modules
odoo -c /opt/odoo/odoo.conf -d your_estate_db \
  --init=plt_estate,plt_gcg,plt_harvest,plt_transport,plt_sales,plt_payroll,plt_upkeep,plt_planning,plt_plasma,plt_compliance,plt_nursery,plt_reporting \
  --stop-after-init

# Start the server
odoo -c /opt/odoo/odoo.conf -d your_estate_db
```

### 6. Systemd Service (Optional)

```ini
# /etc/systemd/system/odoo.service
[Unit]
Description=Odoo 19 Plantation Management
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
ExecStart=/opt/odoo/odoo-venv/bin/odoo -c /opt/odoo/odoo.conf -d your_estate_db
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now odoo
```

---

## 🧪 Running Tests

```bash
# Run all 277 tests
cd /path/to/kebun
source odoo-venv/bin/activate

odoo -c odoo.conf -d your_test_db \
  --test-enable \
  --test-tags=plt_estate,plt_gcg,plt_harvest,plt_transport,plt_sales,plt_payroll,plt_upkeep,plt_planning,plt_plasma,plt_compliance,plt_nursery,plt_reporting \
  --stop-after-init --no-http
```

### Run Tests for a Single Module

```bash
odoo -c odoo.conf -d your_test_db \
  --init=plt_harvest --test-enable --test-tags=plt_harvest \
  --stop-after-init --no-http
```

---

## 📁 Project Structure

```
koobun/
├── plt_estate/          # Estate master data & land registry
│   ├── models/          # 7 models (estate, afdeling, block, ancak, tph, census, land doc)
│   ├── views/           # List, form, search views + menus
│   ├── security/        # Access control (ir.model.access.csv, ir.rule XML)
│   └── tests/           # 46 tests + integration test
├── plt_gcg/             # Governance & internal control
│   ├── models/          # 6 models (authority, SoD, audit log, exception, whistleblowing, period)
│   └── tests/           # 56 tests
├── plt_harvest/         # Harvest management
│   ├── models/          # 9 models (taksasi, TPH, quality, premi, denda, inspection, premi statement)
│   └── tests/           # 55 tests
├── plt_transport/       # Transport & weighbridge
│   ├── models/          # 4 models (SPB, weighbridge, restan, reconciliation)
│   └── tests/           # 36 tests
├── plt_sales/           # TBS sales & mill reconciliation
│   ├── models/          # 6 models (mill, price, reception, invoice, sortasi, revenue distribution)
│   └── tests/           # 35 tests
├── plt_payroll/         # Indonesian payroll (PPh21, BPJS, THR)
│   ├── models/          # 9 models (contract, wage, BPJS, PPh21, salary rules, payslip, batch, PTKP, THR)
│   └── tests/           # 72 tests
├── plt_upkeep/          # Agronomy operations (digital BKM)
│   ├── models/          # 5 models (activity code, BKM, BPB, fertilizer, P&D census)
│   └── tests/           # 22 tests
├── plt_planning/        # Annual & monthly planning (RKAP/RKB/RKH)
│   ├── models/          # 6 models (norma kerja, RKAP, RKB, RKH, budget actual, BKM extension)
│   └── tests/           # 25 tests
├── plt_plasma/          # Plasma/smallholder management
│   ├── models/          # 7 models (farmer, koperasi, FFB intake, disbun price, loans, statements, siperibun)
│   └── tests/           # 22 tests
├── plt_compliance/      # ISPO, EUDR, K3 compliance
│   ├── models/          # 5 models (ISPO evidence, EUDR export, K3 incident, APD, environmental)
│   └── tests/           # 11 tests
├── plt_nursery/         # Nursery management
│   ├── models/          # 4 models (batch, seedling, culling, transfer)
│   └── tests/           # 6 tests
└── plt_reporting/       # SQL-based reporting dashboards
    ├── models/          # 6 SQL views (daily prod, yield, restan, cost, LHM, payslip summary)
    └── tests/           # 9 tests
```

---

## 🔧 Development

### Tech Stack

- **Backend:** Python 3.12, Odoo 19 ORM
- **Database:** PostgreSQL with SQL views for reporting
- **Frontend:** Odoo XML views (list, form, search)
- **Testing:** Odoo `TransactionCase` with TDD approach

### Adding a New Module

1. Create module directory: `plt_mymodule/`
2. Add `__manifest__.py`, `__init__.py`, `models/__init__.py`
3. Write tests FIRST in `tests/test_mymodule.py`
4. Implement models in `models/mymodule_model.py`
5. Add views in `views/mymodule_views.xml`
6. Add security in `security/ir.model.access.csv`
7. Register in `__manifest__.py` data list

### Odoo 19 Gotchas

| Issue | Fix |
|-------|-----|
| `groups_id` on `res.users` | Use `group_ids` instead |
| `<tree>` in views | Use `<list>` |
| `attrs=` on fields | Use `invisible=`, `readonly=`, `required=` directly |
| `hr.contract` model | Not available — use standalone model |
| `<group>` in search views | Not allowed in Odoo 19 |
| SQL view column changes | Must `DROP VIEW IF EXISTS` before `CREATE OR REPLACE VIEW` |
| JSONB name fields | Use `name->>'en_US'` in SQL |

---

## 📊 Database Schema Overview

Key tables by module:

| Table | Module | Purpose |
|-------|--------|---------|
| `estate_block` | plt_estate | Block master data (area, afdeling, age, planting date) |
| `estate_tph` | plt_estate | Tempat Pengumpulan Hasil (collection points) |
| `harvest_tph_record` | plt_harvest | Harvest records per TPH per day |
| `transport_spb` | plt_transport | Surat Perintah Bongkar (delivery orders) |
| `transport_weighbridge_ticket` | plt_transport | Weighbridge readings |
| `payroll_payslip_line` | plt_payroll | Per-employee payslip details |
| `upkeep_bkm` | plt_upkeep | Buku Kerja Mandor (foreman daily log) |
| `plan_rkap` | plt_planning | Annual budget plan |
| `plasma_farmer` | plt_plasma | Plasma farmer registry |

---

## 📄 License

This project is proprietary software developed for internal use.
Contact the repository owner for licensing inquiries.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Write tests first (TDD)
4. Implement the feature
5. Ensure all 277+ tests pass
6. Submit a pull request

---

## 📞 Support

For issues and questions, please open a GitHub issue at:
https://github.com/windalfin/koobun/issues
