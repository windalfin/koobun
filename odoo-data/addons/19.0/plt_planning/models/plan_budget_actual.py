# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PlanBudgetActual(models.Model):
    """Budget vs Actual per block × activity × month."""
    _name = 'plan.budget_actual'
    _description = 'Anggaran vs Realisasi per Blok per Aktivitas per Bulan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, month, block_id, activity_code_id'

    name = fields.Char(
        string='Nama',
        compute='_compute_name',
        store=True,
    )
    block_id = fields.Many2one(
        'estate.block',
        string='Blok',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    activity_code_id = fields.Many2one(
        'upkeep.activity_code',
        string='Aktivitas',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    year = fields.Integer(
        string='Tahun',
        required=True,
        default=lambda self: fields.Date.context_today(self).year,
        tracking=True,
    )
    month = fields.Selection([
        ('1', 'Januari'), ('2', 'Februari'), ('3', 'Maret'),
        ('4', 'April'), ('5', 'Mei'), ('6', 'Juni'),
        ('7', 'Juli'), ('8', 'Agustus'), ('9', 'September'),
        ('10', 'Oktober'), ('11', 'November'), ('12', 'Desember'),
    ], string='Bulan', required=True, tracking=True)

    budgeted_cost = fields.Monetary(
        string='Anggaran (Rp)',
        currency_field='currency_id',
        default=0.0,
        tracking=True,
    )
    actual_cost = fields.Monetary(
        string='Realisasi (Rp)',
        currency_field='currency_id',
        default=0.0,
        tracking=True,
    )
    variance = fields.Monetary(
        string='Selisih (Rp)',
        currency_field='currency_id',
        compute='_compute_variance',
        store=True,
        help='Positif = under budget (hemat), negatif = over budget.',
    )
    variance_pct = fields.Float(
        string='Selisih (%)',
        digits=(6, 2),
        compute='_compute_variance',
        store=True,
        help='Persentase selisih terhadap anggaran.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    notes = fields.Text(string='Keterangan')

    @api.depends('block_id', 'activity_code_id', 'year', 'month')
    def _compute_name(self):
        for rec in self:
            parts = []
            if rec.block_id:
                parts.append(rec.block_id.code or rec.block_id.name)
            if rec.activity_code_id:
                parts.append(rec.activity_code_id.code or rec.activity_code_id.name)
            parts.append(str(rec.year))
            parts.append(dict(rec._fields['month'].selection).get(rec.month, ''))
            rec.name = ' / '.join(p for p in parts if p)

    @api.depends('budgeted_cost', 'actual_cost')
    def _compute_variance(self):
        for rec in self:
            rec.variance = (rec.budgeted_cost or 0.0) - (rec.actual_cost or 0.0)
            if rec.budgeted_cost:
                rec.variance_pct = (
                    rec.variance / rec.budgeted_cost * 100.0
                )
            else:
                rec.variance_pct = 0.0