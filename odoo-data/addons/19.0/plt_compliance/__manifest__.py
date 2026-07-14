{
    "name": "PLT-10 — Compliance & Traceability (ISPO / EUDR)",
    "version": "19.0.1.0.0",
    "category": "Plantation/Compliance",
    "summary": "Make audits a query, not a project",
    "description": """
PLT-10 provides compliance and traceability for ISPO and EUDR:
- ISPO evidence register structured by 7 principles
- EUDR pack: per-block geolocation + production-period linkage -> DDS export
- K3 module-lite: APD issue records, incident/accident log
- Environmental records: HCV areas, fire watch, chemical usage
- Legality expiry dashboard (from PLT-01)
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "plt_estate", "plt_transport", "plt_upkeep", "plt_gcg"],
    "data": [
        "security/compliance_security.xml",
        "security/ir.model.access.csv",
        "views/compliance_views.xml",
        "views/compliance_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
