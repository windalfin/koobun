# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import models, fields, api


class HarvestRotation(models.Model):
    _name = 'harvest.rotation'
    _description = 'Harvest Rotation / Section Management'
    _inherit = ['mail.thread']
    _order = 'name'

    # ── Basic Fields ──────────────────────────────────────────
    name = fields.Char(string='Name', required=True, tracking=True)
    block_ids = fields.Many2many(
        'estate.block', 'harvest_rotation_block_rel',
        'rotation_id', 'block_id',
        string='Blocks', tracking=True,
    )
    rotation_interval_days = fields.Integer(
        string='Rotation Interval (Days)', default=14, tracking=True,
    )
    last_harvest_date = fields.Date(string='Last Harvest Date', tracking=True)

    # ── Computed ──────────────────────────────────────────────
    next_harvest_date = fields.Date(
        string='Next Harvest Date',
        compute='_compute_next_harvest_date', store=True,
    )

    @api.depends('last_harvest_date', 'rotation_interval_days')
    def _compute_next_harvest_date(self):
        for rec in self:
            if rec.last_harvest_date and rec.rotation_interval_days:
                rec.next_harvest_date = (
                    rec.last_harvest_date
                    + timedelta(days=rec.rotation_interval_days)
                )
            else:
                rec.next_harvest_date = False
