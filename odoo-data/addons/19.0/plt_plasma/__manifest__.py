{
    "name": "PLT-09 — Plasma / Kemitraan Management",
    "version": "19.0.1.0.0",
    "category": "Plantation/Plasma",
    "summary": "Manage smallholder partners: registry, FFB intake, pricing, loans",
    "description": """
PLT-09 manages plasma smallholder programs:
- Farmer & koperasi registry with plot polygons (EUDR-ready)
- Plasma FFB intake at weighbridge with auto Disbun pricing
- Loan/saprodi advance ledgers with configurable deduction %
- Monthly farmer statements (printable, transparent)
- SIPERIBUN 6-monthly reporting pack
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "account", "plt_estate", "plt_transport", "plt_sales", "plt_gcg"],
    "data": [
        "security/plasma_security.xml",
        "security/ir.model.access.csv",
        "views/plasma_views.xml",
        "views/disbun_price_views.xml",
        "views/plasma_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
