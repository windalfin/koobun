# -*- coding: utf-8 -*-
{
    'name': 'PLT Dashboard',
    'version': '19.0.1.0.0',
    'summary': 'Plantation Dashboard — overview of all PLT modules',
    'description': """
Dashboard views for the 12 Plantation (PLT) modules:
Estate, Harvest, Transport, Sales, Payroll, Upkeep,
Planning, Plasma, Compliance, Nursery, Reporting, and GCG.
    """,
    'category': 'Services/Dashboard',
    'author': 'PLT Team',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'board',
        'plt_estate',
        'plt_harvest',
        'plt_transport',
        'plt_sales',
        'plt_payroll',
        'plt_upkeep',
        'plt_planning',
        'plt_plasma',
        'plt_compliance',
        'plt_nursery',
        'plt_reporting',
        'plt_gcg',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'data/dashboard_data.xml',
        'views/dashboard_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
