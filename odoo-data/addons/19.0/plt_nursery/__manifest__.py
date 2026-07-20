{
    "name": "PLT-03 — Nursery Management (Pembibitan)",
    "version": "19.0.1.0.0",
    "category": "Plantation/Nursery",
    "summary": "Track seedlings from pre-nursery to field transfer",
    "description": """
PLT-03 manages the oil palm nursery:
- Seedling batch tracking (source, variety, quantity, date received)
- Culling records (rejected seedlings with reason)
- Transfer to field tracking (nursery → block)
- Germination rate and survival rate KPIs
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "stock", "plt_estate", "plt_gcg"],
    "data": [
        "security/nursery_security.xml",
        "security/ir.model.access.csv",
        "views/nursery_views.xml",
        "views/nursery_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
