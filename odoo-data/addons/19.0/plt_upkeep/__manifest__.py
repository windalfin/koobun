{
    "name": "PLT-04 — Upkeep / Agronomy Operations (Digital BKM)",
    "version": "19.0.1.0.0",
    "category": "Plantation/Upkeep",
    "summary": "Digital Buku Kerja Mandor for all non-harvest field work",
    "description": """
PLT-04 digitizes the Buku Kerja Mandor (BKM) for upkeep operations:
- BKM record: mandor, block, activity, workers, output, materials
- BPB (Bon Permintaan Barang): material requisition workflow
- Fertilizer program vs realization tracking (5T compliance)
- Pest & disease monitoring (Ganoderma, Oryctes, etc.)
- Activity code catalog for all upkeep operations
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "hr", "stock", "plt_estate", "plt_gcg"],
    "data": [
        "security/upkeep_security.xml",
        "security/ir.model.access.csv",
        "views/upkeep_views.xml",
        "views/upkeep_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
