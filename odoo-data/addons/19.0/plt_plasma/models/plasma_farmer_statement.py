# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PlasmaFarmerStatement(models.Model):
    """Monthly farmer statement (printable, transparent)."""
    _name = 'plasma.farmer_statement'
    _description = 'Monthly Farmer Statement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, month, farmer_id'

    farmer_id = fields.Many2one('plasma.farmer', string='Farmer', required=True, ondelete='restrict', tracking=True)
    year = fields.Integer(string='Year', required=True, default=lambda self: fields.Date.context_today(self).year, tracking=True)
    month = fields.Selection([
        ('1', 'January'), ('2', 'February'), ('3', 'March'),
        ('4', 'April'), ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'), ('9', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December'),
    ], string='Month', required=True, tracking=True)

    total_delivery_kg = fields.Float(string='Total Delivery (KG)', digits=(12, 2), tracking=True)
    gross_revenue = fields.Monetary(string='Gross Revenue', currency_field='currency_id', tracking=True)
    total_deductions = fields.Monetary(string='Total Deductions', currency_field='currency_id', tracking=True)
    net_payment = fields.Monetary(string='Net Payment', currency_field='currency_id', compute='_compute_net', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)
    notes = fields.Text(string='Notes')

    @api.depends('gross_revenue', 'total_deductions')
    def _compute_net(self):
        for rec in self:
            rec.net_payment = (rec.gross_revenue or 0.0) - (rec.total_deductions or 0.0)

    def action_post(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft statements can be posted.'))
            rec.state = 'posted'
