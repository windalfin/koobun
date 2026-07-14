{
    "name": "PLT-05 — Harvest Management (Panen, Premi & Denda)",
    "version": "19.0.1.0.0",
    "category": "Plantation/Harvest",
    "summary": "Full harvest chain: taksasi → ancak → TPH capture → quality → premi/denda",
    "description": """
PLT-05 manages the complete harvest chain for oil palm estates:
- Taksasi/AKP (D-1 crop estimate)
- Harvest rotation & section management
- Ancak assignment (tetap/giring)
- TPH harvest capture (mobile-ready, offline)
- Quality grading & denda (penalties)
- Premi engine (configurable formula tables, effective-dated)
- Mutu ancak / mutu buah inspections
- Daily premi statement per harvester
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "hr", "plt_estate", "plt_gcg"],
    "data": [
        "security/harvest_security.xml",
        "security/ir.model.access.csv",
        "views/harvest_taksasi_views.xml",
        "views/harvest_rotation_views.xml",
        "views/harvest_ancak_views.xml",
        "views/harvest_tph_record_views.xml",
        "views/harvest_quality_event_views.xml",
        "views/harvest_premi_config_views.xml",
        "views/harvest_denda_config_views.xml",
        "views/harvest_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
