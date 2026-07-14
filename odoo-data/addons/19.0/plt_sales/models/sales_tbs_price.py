# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesTbsPrice(models.Model):
    """Effective-dated TBS price table with market and Disbun government
    pricing tiers by age band and rendemen."""
    _name = 'sales.tbs_price'
    _description = 'TBS Price Table'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc, age_band_min, id'

    # ── Core ───────────────────────────────────────────────────
    name = fields.Char(
        string='Price Name', required=True, tracking=True,
    )
    price_type = fields.Selection(
        selection=[
            ('market', 'Market Price'),
            ('disbun_permentan01', 'Disbun Permentan 01'),
        ],
        string='Price Type', required=True, default='market',
        tracking=True,
    )
    age_band_min = fields.Integer(
        string='Age Band Min (years)', required=True, default=0,
        tracking=True,
    )
    age_band_max = fields.Integer(
        string='Age Band Max (years)', required=True, default=99,
        tracking=True,
    )
    rendemen_pct = fields.Float(
        string='Rendemen (%)', digits=(5, 2), default=0.0,
        tracking=True,
    )
    indeks_k = fields.Float(
        string='Indeks K', digits=(5, 4), default=1.0,
        tracking=True,
    )
    price_per_kg = fields.Float(
        string='Price per Kg', digits=(10, 2), default=0.0,
        tracking=True,
    )
    cp_oil_reference = fields.Float(
        string='CPO Reference Price', digits=(10, 2), default=0.0,
        help='Reference CPO price this TBS price was derived from.',
        tracking=True,
    )
    date_from = fields.Date(
        string='Valid From', required=True, tracking=True,
    )
    date_to = fields.Date(
        string='Valid To', required=True, tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('expired', 'Expired'),
        ],
        string='State', default='draft', required=True, tracking=True,
    )

    # ── Constraints ────────────────────────────────────────────
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(_(
                    'Valid From date cannot be after Valid To date.'
                ))

    @api.constrains('age_band_min', 'age_band_max')
    def _check_age_band(self):
        for rec in self:
            if rec.age_band_min > rec.age_band_max:
                raise ValidationError(_(
                    'Age Band Min cannot be greater than Age Band Max.'
                ))

    @api.constrains('price_per_kg')
    def _check_price_positive(self):
        for rec in self:
            if rec.price_per_kg < 0:
                raise ValidationError(_(
                    'Price per Kg cannot be negative.'
                ))

    # ── Actions ────────────────────────────────────────────────
    def action_approve(self):
        self.write({'state': 'approved'})

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_draft(self):
        self.write({'state': 'draft'})
