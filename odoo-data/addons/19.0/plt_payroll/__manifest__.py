{
    "name": "PLT-08 — Plantation Payroll Indonesia",
    "version": "19.0.1.0.0",
    "category": "Plantation/Payroll",
    "summary": "Pay every worker class correctly: BHL, SKU/KHT, staff, borongan",
    "description": """
PLT-08 manages plantation payroll for all worker classes:
- BHL (daily casual), SKU/KHT (permanent daily), monthly staff
- Auto-fed HK from PLT-04 BKM, premi/denda from PLT-05
- BPJS Kesehatan & Ketenagakerjaan auto-calculation
- PPh 21 TER method + annual true-up
- Payroll journal auto-distributed to block analytic accounts
- Payslips showing premi formula components (Fairness)
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
        "hr_payroll",
        "plt_estate",
        "plt_harvest",
        "plt_gcg",
        "account",
    ],
    "data": [
        "security/payroll_security.xml",
        "security/ir.model.access.csv",
        "views/payroll_worker_contract_views.xml",
        "views/payroll_wage_master_views.xml",
        "views/payroll_bpjs_config_views.xml",
        "views/payroll_pph21_config_views.xml",
        "views/payroll_salary_rule_views.xml",
        "views/payroll_payroll_batch_views.xml",
        "views/payroll_payslip_line_views.xml",
        "views/payroll_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
