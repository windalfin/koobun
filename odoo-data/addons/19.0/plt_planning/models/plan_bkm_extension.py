# -*- coding: utf-8 -*-
from odoo import fields, models


class UpkeepBKM(models.Model):
    """Extend upkeep.bkm with RKH reference link (available when plt_planning is installed)."""
    _inherit = 'upkeep.bkm'

    rkh_id = fields.Many2one(
        'plan.rkh',
        string='RKH Reference',
        ondelete='set null',
        tracking=True,
        index=True,
    )
