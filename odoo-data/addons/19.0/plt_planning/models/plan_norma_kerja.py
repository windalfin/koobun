# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PlanNormaKerja(models.Model):
    """Standard work norms: output per HK and cost per unit per activity."""
    _name = 'plan.norma_kerja'
    _description = 'Norma Kerja (Work Norm)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'activity_code_id, effective_from desc'

    activity_code_id = fields.Many2one(
        'upkeep.activity_code',
        string='Activity',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    output_per_hk = fields.Float(
        string='Output per HK',
        required=True,
        digits=(12, 2),
        tracking=True,
        help='Standard output per worker per day (e.g., ha/HK, pokok/HK).',
    )
    output_uom = fields.Char(
        string='Output UoM',
        default='HK',
        tracking=True,
    )
    cost_per_unit = fields.Monetary(
        string='Cost per Unit',
        currency_field='currency_id',
        digits=(12, 2),
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    effective_from = fields.Date(
        string='Effective From',
        required=True,
        tracking=True,
    )
    effective_to = fields.Date(
        string='Effective To',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('expired', 'Expired'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
    )
    notes = fields.Text(string='Notes')

    @api.constrains('effective_from', 'effective_to')
    def _check_dates(self):
        for rec in self:
            if rec.effective_to and rec.effective_to < rec.effective_from:
                raise ValidationError(_(
                    'Effective To cannot be before Effective From.'
                ))
