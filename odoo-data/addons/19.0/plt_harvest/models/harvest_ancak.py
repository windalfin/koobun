# -*- coding: utf-8 -*-
from odoo import models, fields


class HarvestAncak(models.Model):
    _name = 'harvest.ancak'
    _description = 'Ancak (Daily Harvest Assignment)'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    # ── Basic Fields ──────────────────────────────────────────
    date = fields.Date(string='Date', required=True, tracking=True)
    mandor_id = fields.Many2one(
        'hr.employee', string='Mandor', required=True,
        ondelete='restrict', tracking=True,
    )
    harvester_id = fields.Many2one(
        'hr.employee', string='Harvester', required=True,
        ondelete='restrict', tracking=True,
    )
    block_id = fields.Many2one(
        'estate.block', string='Block', required=True,
        ondelete='restrict', tracking=True,
    )
    ancak_type = fields.Selection(
        selection=[
            ('tetap', 'Tetap (Fixed)'),
            ('giring', 'Giring (Roaming)'),
        ],
        string='Ancak Type', required=True, default='tetap', tracking=True,
    )
