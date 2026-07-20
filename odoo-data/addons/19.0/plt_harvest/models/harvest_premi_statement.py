# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HarvestPremiStatement(models.Model):
    _name = 'harvest.premi_statement'
    _description = 'Daily Premi Statement per Harvester'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # ── Basic Fields ──────────────────────────────────────────
    date = fields.Date(
        string='Tanggal', required=True,
        default=fields.Date.context_today, tracking=True,
    )
    harvester_id = fields.Many2one(
        'hr.employee', string='Pemanen', required=True,
        ondelete='restrict', tracking=True,
    )

    # ── Amounts ───────────────────────────────────────────────
    premi_amount = fields.Float(
        string='Premi', digits=(16, 2),
        default=0.0, tracking=True,
    )
    denda_amount = fields.Float(
        string='Denda', digits=(16, 2),
        default=0.0, tracking=True,
    )
    net_premi = fields.Float(
        string='Net Premi', digits=(16, 2),
        compute='_compute_net_premi', store=True,
    )

    # ── State ─────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
        ],
        string='Status', default='draft', required=True, tracking=True,
    )

    # ── Computed ──────────────────────────────────────────────
    @api.depends('premi_amount', 'denda_amount')
    def _compute_net_premi(self):
        for rec in self:
            rec.net_premi = rec.premi_amount - rec.denda_amount

    # ── Actions ───────────────────────────────────────────────
    def action_post(self):
        for rec in self:
            rec.state = 'posted'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'