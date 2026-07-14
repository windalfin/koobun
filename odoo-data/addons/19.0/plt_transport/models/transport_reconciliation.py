# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TransportReconciliation(models.Model):
    _name = 'transport.reconciliation'
    _description = 'Three-Way Reconciliation (SPB ↔ Weighbridge ↔ Mill)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ── Link to SPB ──────────────────────────────────────────
    spb_id = fields.Many2one(
        'transport.spb', string='SPB', required=True,
        ondelete='restrict', index=True, tracking=True,
    )

    # ── SPB Data (snapshot at reconciliation time) ───────────
    spb_janjang = fields.Integer(
        string='SPB Janjang', tracking=True,
    )
    spb_est_kg = fields.Float(
        string='SPB Estimated KG', digits=(16, 2), tracking=True,
    )

    # ── Weighbridge Data ─────────────────────────────────────
    weighbridge_net = fields.Float(
        string='Weighbridge Net KG', digits=(16, 2), tracking=True,
    )

    # ── Mill Data ────────────────────────────────────────────
    mill_net = fields.Float(
        string='Mill Net KG', digits=(16, 2), tracking=True,
    )

    # ── Computed ─────────────────────────────────────────────
    variance_pct = fields.Float(
        string='Variance (%)', digits=(16, 2),
        compute='_compute_variance_pct', store=True,
    )
    status = fields.Selection(
        selection=[
            ('matched', 'Matched'),
            ('variance', 'Variance'),
            ('exception', 'Exception'),
        ],
        string='Status', compute='_compute_status', store=True,
        tracking=True,
    )

    # ── Notes ────────────────────────────────────────────────
    notes = fields.Text(
        string='Notes', tracking=True,
    )

    # ── Computed Methods ─────────────────────────────────────
    @api.depends('weighbridge_net', 'mill_net')
    def _compute_variance_pct(self):
        for rec in self:
            if rec.mill_net and rec.mill_net > 0:
                rec.variance_pct = abs(
                    (rec.weighbridge_net - rec.mill_net) / rec.mill_net
                ) * 100.0
            else:
                rec.variance_pct = 0.0

    @api.depends('variance_pct', 'spb_janjang', 'spb_est_kg',
                 'weighbridge_net', 'mill_net')
    def _compute_status(self):
        for rec in self:
            if not rec.weighbridge_net or not rec.mill_net:
                rec.status = 'exception'
            elif rec.variance_pct <= 2.0:
                rec.status = 'matched'
            elif rec.variance_pct <= 10.0:
                rec.status = 'variance'
            else:
                rec.status = 'exception'
