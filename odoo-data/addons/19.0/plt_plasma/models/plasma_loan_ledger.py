# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PlasmaLoanLedger(models.Model):
    """Saprodi/advance loan entries with configurable deduction %."""
    _name = 'plasma.loan_ledger'
    _description = 'Plasma Loan Ledger'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, farmer_id'

    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, tracking=True)
    farmer_id = fields.Many2one('plasma.farmer', string='Farmer', required=True, ondelete='restrict', tracking=True)
    description = fields.Char(string='Description', required=True, tracking=True)
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True, tracking=True)
    deduction_pct = fields.Float(string='Deduction (%)', digits=(4, 2), required=True, default=20.0, tracking=True)
    remaining_balance = fields.Monetary(string='Remaining Balance', currency_field='currency_id', compute='_compute_balance', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('active', 'Active'),
        ('settled', 'Settled'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='active', required=True, tracking=True)
    notes = fields.Text(string='Notes')

    @api.depends('amount')
    def _compute_balance(self):
        for rec in self:
            # Simplified: remaining = original amount
            rec.remaining_balance = rec.amount
