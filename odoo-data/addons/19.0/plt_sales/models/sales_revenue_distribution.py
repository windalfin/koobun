# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SalesRevenueDistribution(models.Model):
    _name = 'sales.revenue_distribution'
    _description = 'Distribusi Pendapatan per Blok (Pro-Rata)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ── Core Fields ───────────────────────────────────────────
    invoice_id = fields.Many2one(
        'sales.invoice', string='Invoice',
        ondelete='cascade', tracking=True,
    )
    block_id = fields.Many2one(
        'estate.block', string='Blok', required=True,
        ondelete='restrict', tracking=True,
    )
    weight_kg = fields.Float(
        string='Berat (kg)', digits=(16, 2),
        default=0.0, tracking=True,
    )
    revenue_amount = fields.Float(
        string='Jumlah Pendapatan', digits=(16, 2),
        default=0.0, tracking=True,
    )

    # ── Related ──────────────────────────────────────────────
    analytic_account_id = fields.Many2one(
        related='block_id.analytic_account_id',
        string='Akun Analitik', store=True, readonly=True,
    )

    # ── State ─────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
        ],
        string='Status', default='draft', required=True, tracking=True,
    )

    # ── Actions ───────────────────────────────────────────────
    def action_compute_revenue(self):
        """Compute revenue_amount pro-rata by block weight share.

        For each set of lines sharing the same invoice_id, distribute the
        invoice's line_amount across blocks proportional to weight_kg.
        """
        for rec in self:
            if not rec.invoice_id:
                continue
            invoice = rec.invoice_id
            all_lines = self.search([('invoice_id', '=', invoice.id)])
            total_weight = sum(all_lines.mapped('weight_kg'))
            if total_weight and rec.weight_kg:
                share = rec.weight_kg / total_weight
                rec.revenue_amount = (invoice.line_amount or 0.0) * share
            else:
                rec.revenue_amount = 0.0

    def action_post(self):
        for rec in self:
            rec.state = 'posted'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'