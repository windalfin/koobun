# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SalesSortasiAnalysis(models.Model):
    """Sortasi deduction trend analysis — provides feedback from mill
    reception data for quality improvement."""
    _name = 'sales.sortasi_analysis'
    _description = 'Sortasi Deduction Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'period_start desc, deduction_reason, id'

    # ── Core ───────────────────────────────────────────────────
    mill_id = fields.Many2one(
        'sales.mill', string='Mill', required=True,
        ondelete='restrict', tracking=True, index=True,
    )
    period_start = fields.Date(
        string='Period Start', required=True, tracking=True,
    )
    period_end = fields.Date(
        string='Period End', required=True, tracking=True,
    )
    block_id = fields.Many2one(
        'estate.block', string='Block',
        ondelete='restrict', tracking=True,
    )
    mandor_id = fields.Many2one(
        'hr.employee', string='Mandor',
        ondelete='restrict', tracking=True,
    )
    deduction_reason = fields.Char(
        string='Deduction Reason', required=True, tracking=True,
        help='e.g. "buah mentah", "tangkai panjang", "sampah".',
    )
    total_deduction_kg = fields.Float(
        string='Total Deduction (kg)', digits=(12, 2), default=0.0,
        tracking=True,
    )
    frequency_count = fields.Integer(
        string='Frequency Count', default=1,
        help='Number of occurrences of this deduction reason in the period.',
        tracking=True,
    )
    trend_pct = fields.Float(
        string='Trend (%)', digits=(5, 2), default=0.0,
        help='Percentage contribution of this deduction reason to total deductions.',
        tracking=True,
    )
