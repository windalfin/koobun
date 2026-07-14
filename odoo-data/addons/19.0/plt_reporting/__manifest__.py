{
    "name": "PLT-13 — Reporting & KPI Dashboards",
    "version": "19.0.1.0.0",
    "category": "Plantation/Reporting",
    "summary": "Core operational and financial reports for the estate",
    "description": """
PLT-13 provides reporting and KPI dashboards:
- Daily: production per block/mandor, dispatch log, restan, HK summary
- Monthly: yield/ha vs RKAP, cost per block & per kg TBS
- KPIs: yield/ha, BJR trend, rotation days, harvester kg/HK
- Finance: TBM capitalization report (PSAK 69), TM P&L per block
    """,
    "author": "Kebun Plantation",
    "license": "LGPL-3",
    "depends": ["base", "mail", "account", "plt_estate", "plt_harvest",
                "plt_transport", "plt_sales", "plt_payroll", "plt_upkeep", "plt_gcg"],
    "data": [
        "security/reporting_security.xml",
        "security/ir.model.access.csv",
        "views/reporting_views.xml",
        "views/reporting_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
