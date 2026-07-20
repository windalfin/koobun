{
    "name": "PLT-02 — Planning & Budgeting (RKAP / RKB / RKH)",
    "version": "19.0.1.0.0",
    "category": "Plantation/Planning",
    "summary": "Digitize the planning cascade and lock execution to plan",
    "description": """
PLT-02 manages the plantation planning hierarchy:
- Norma kerja master: standard output & cost norms per activity
- RKAP (annual plan per block x activity x month)
- RKB (monthly breakdown with adjustment workflow)
- RKH (daily work orders per mandor team)
- Budget vs actual: physical + financial, per block/afdeling/estate
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "account", "analytic", "plt_estate", "plt_gcg", "plt_upkeep"],
    "data": [
        "security/planning_security.xml",
        "security/ir.model.access.csv",
        "views/planning_views.xml",
        "views/budget_actual_views.xml",
        "views/planning_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
