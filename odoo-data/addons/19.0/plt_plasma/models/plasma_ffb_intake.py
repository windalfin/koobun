# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PlasmaFFBIntake(models.Model):
    """Plasma FFB intake at weighbridge with auto Disbun pricing."""
    _name = 'plasma.ffb_intake'
    _description = 'Plasma FFB Intake'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id'

    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, tracking=True)
    farmer_id = fields.Many2one('plasma.farmer', string='Farmer', required=True, ondelete='restrict', tracking=True)
    spb_id = fields.Many2one('transport.spb', string='SPB', ondelete='restrict', tracking=True)
    net_kg = fields.Float(string='Net Weight (KG)', required=True, digits=(12, 2), tracking=True)
    disbun_price_id = fields.Many2one('sales.tbs_price', string='Disbun Price', tracking=True)
    price_per_kg = fields.Float(string='Price/KG', digits=(12, 4), compute='_compute_price', store=True)
    gross_amount = fields.Monetary(string='Gross Amount', currency_field='currency_id', compute='_compute_gross', store=True)
    deduction_pct = fields.Float(string='Deduction (%)', digits=(4, 2), default=0.0, tracking=True)
    net_amount = fields.Monetary(string='Net Amount', currency_field='currency_id', compute='_compute_net', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)
    notes = fields.Text(string='Notes')

    @api.depends('disbun_price_id')
    def _compute_price(self):
        for rec in self:
            rec.price_per_kg = rec.disbun_price_id.market_price or 0.0

    @api.depends('net_kg', 'price_per_kg')
    def _compute_gross(self):
        for rec in self:
            rec.gross_amount = rec.net_kg * rec.price_per_kg

    @api.depends('gross_amount', 'deduction_pct')
    def _compute_net(self):
        for rec in self:
            rec.net_amount = rec.gross_amount * (1 - rec.deduction_pct / 100.0)
