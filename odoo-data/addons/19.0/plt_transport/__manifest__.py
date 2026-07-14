{
    "name": "PLT-06 — FFB Transport & Weighbridge (SPB / Timbangan)",
    "version": "19.0.1.0.0",
    "category": "Plantation/Transport",
    "summary": "Control FFB movement from TPH to mill: no fruit moves without papers",
    "description": """
PLT-06 manages the FFB transport chain:
- SPB (Surat Pengantar Buah) — numbered, gap-controlled dispatch documents
- Weighbridge integration (estate-estimate mode for MVP)
- Restan management (uncollected FFB tracking)
- Three-way reconciliation: SPB ↔ weighbridge ↔ mill
- Trip & fleet economics (transport cost per kg per block)
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "fleet", "plt_estate", "plt_harvest", "plt_gcg"],
    "data": [
        "security/transport_security.xml",
        "security/ir.model.access.csv",
        "views/transport_spb_views.xml",
        "views/transport_weighbridge_views.xml",
        "views/transport_restan_views.xml",
        "views/transport_reconciliation_views.xml",
        "views/transport_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
