{
    "name": "PLT-12 — GCG & Internal Control Layer",
    "version": "19.0.1.0.0",
    "category": "Plantation/Governance",
    "summary": "Governance spine enforcing TARIF GCG principles across all PLT modules",
    "description": """
PLT-12 is the cross-cutting governance layer enforcing GCG (Good Corporate Governance)
across the entire PLT suite.

Features:
- Authority Matrix / Delegation of Authority engine
- Segregation-of-Duties (SoD) conflict rules
- Immutable audit trail on all critical field changes
- Exception & red-flag dashboard for SPI/internal audit
- Whistleblowing/grievance intake
- Period close & locking checklist
- Role-based constraints (maker-checker-approver enforcement)
    """,
    "author": "Kebun Plantation",
    "website": "https://kebun.example.com",
    "license": "LGPL-3",
    "depends": ["base", "mail", "hr", "plt_estate"],
    "data": [
        "security/gcg_security.xml",
        "security/ir.model.access.csv",
        "views/gcg_authority_matrix_views.xml",
        "views/gcg_sod_rule_views.xml",
        "views/gcg_audit_log_views.xml",
        "views/gcg_exception_views.xml",
        "views/gcg_whistleblowing_views.xml",
        "views/gcg_period_close_views.xml",
        "views/gcg_menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
