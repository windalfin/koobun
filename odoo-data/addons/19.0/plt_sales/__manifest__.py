{
    "name": "PLT-07 — TBS Sales, Pricing & Mill Reconciliation",
    "version": "19.0.1.0.0",
    "category": "Plantation/Sales",
    "summary": "Turn dispatched FFB into correct, reconciled revenue",
    "description": """
PLT-07 manages TBS sales and mill reconciliation:
- Mill/customer master with contract terms
- TBS price master (market + Disbun government prices)
- Mill reception capture & sortasi deduction tracking
- Auto-matching SPB ↔ estate net ↔ mill net
- Revenue auto-distributed to block analytic accounts
- Sortasi deduction trend analysis (feedback to PLT-05)
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "account", "plt_estate", "plt_transport", "plt_gcg"],
    "data": [
        "security/sales_security.xml",
        "security/ir.model.access.csv",
        "views/sales_mill_views.xml",
        "views/sales_tbs_price_views.xml",
        "views/sales_mill_reception_views.xml",
        "views/sales_invoice_views.xml",
        "views/sales_sortasi_analysis_views.xml",
        "views/sales_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
