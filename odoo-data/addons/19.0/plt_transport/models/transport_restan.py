# -*- coding: utf-8 -*-
from datetime import datetime, timezone

from odoo import models, fields, api


class TransportRestan(models.Model):
    _name = 'transport.restan'
    _description = 'Restan (Uncollected FFB)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # ── Basic Fields ─────────────────────────────────────────
    date = fields.Date(
        string='Date', required=True, default=fields.Date.context_today,
        tracking=True,
    )
    block_id = fields.Many2one(
        'estate.block', string='Block', required=True,
        ondelete='restrict', tracking=True,
    )
    tph_id = fields.Many2one(
        'estate.tph', string='TPH', required=True,
        ondelete='restrict', tracking=True,
    )

    # ── Counts ───────────────────────────────────────────────
    janjang_count = fields.Integer(
        string='Janjang Count', tracking=True,
    )
    estimated_kg = fields.Float(
        string='Estimated KG', digits=(16, 2), tracking=True,
    )

    # ── Computed ─────────────────────────────────────────────
    age_hours = fields.Float(
        string='Age (Hours)',
        compute='_compute_age_hours', store=False,
        help='Hours since this restan record was created.',
    )
    escalated = fields.Boolean(
        string='Escalated', default=False,
        tracking=True,
    )

    # ── Computed Methods ─────────────────────────────────────
    @api.depends('create_date')
    def _compute_age_hours(self):
        for rec in self:
            if rec.create_date:
                now = datetime.now()
                delta = now - rec.create_date
                rec.age_hours = delta.total_seconds() / 3600.0
            else:
                rec.age_hours = 0.0

    # ── Actions ──────────────────────────────────────────────
    def action_escalate(self):
        for rec in self:
            rec.escalated = True
