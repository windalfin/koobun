# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PayrollPph21Config(models.Model):
    _name = 'payroll.pph21_config'
    _description = 'PPh 21 TER Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'effective_from desc, id desc'

    # ── Basic Fields ────────────────────────────────────────
    ptkp_category = fields.Char(
        string='PTKP Category',
        required=True,
        tracking=True,
        help='TK/0, TK/1, K/0, K/1, K/2, K/3, etc.',
    )
    ter_category = fields.Char(
        string='TER Category',
        required=True,
        tracking=True,
        help='TER A, TER B, TER C, per PP 58/2023.',
    )
    rate_pct = fields.Float(
        string='Rate (%)',
        digits=(16, 4),
        required=True,
        tracking=True,
    )

    # ── Effective Dates ─────────────────────────────────────
    effective_from = fields.Date(
        string='Effective From',
        required=True,
        tracking=True,
    )
    effective_to = fields.Date(
        string='Effective To',
        tracking=True,
    )

    # ── Constraints ─────────────────────────────────────────
    @api.constrains('effective_from', 'effective_to')
    def _check_dates(self):
        for rec in self:
            if rec.effective_to and rec.effective_from > rec.effective_to:
                raise ValidationError(_(
                    'Effective From date cannot be after Effective To date.'
                ))

    @api.constrains('rate_pct')
    def _check_rate(self):
        for rec in self:
            if rec.rate_pct < 0 or rec.rate_pct > 100:
                raise ValidationError(_(
                    'Rate must be between 0 and 100.'
                ))
