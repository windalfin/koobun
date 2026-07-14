{
    "name": "PLT-01 — Estate Master Data & Land Registry",
    "version": "19.0.1.0.0",
    "category": "Plantation/Estate",
    "summary": "Single source of truth for the physical estate and its legality",
    "description": """
PLT-01 manages the estate hierarchy, block registry, palm census,
GIS geolocation, and land legality documents.

Features:
- Hierarchy: Estate → Afdeling → Block → Ancak (optional)
- Block attributes: area, tahun tanam, SPH, TBM/TM status with dated history
- Palm census (sensus pokok) per block
- GIS GeoJSON polygons per block with auto area calculation
- Land legality document register with expiry alerts
- TPH, Gudang, Road/Bridge asset registry
- Automatic analytic account creation per block
- Master data change approval workflows
- PSAK 69-aware: TBM costs capitalized, TM costs expensed
    """,
    "author": "Kebun Plantation",
    "website": "https://kebun.example.com",
    "license": "LGPL-3",
    "depends": ["base", "mail", "account", "analytic", "hr"],
    "data": [
        "security/estate_security.xml",
        "security/ir.model.access.csv",
        "data/estate_data.xml",
        "views/estate_estate_views.xml",
        "views/estate_afdeling_views.xml",
        "views/estate_block_views.xml",
        "views/estate_ancak_views.xml",
        "views/estate_tph_views.xml",
        "views/estate_census_views.xml",
        "views/estate_land_document_views.xml",
        "views/estate_menus.xml",
    ],
    "demo": [
        "demo/estate_demo.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
