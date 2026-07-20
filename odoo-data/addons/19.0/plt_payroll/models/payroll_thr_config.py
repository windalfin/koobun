# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PayrollThrConfig(models.Model):
    """THR (Tunjangan Hari Raya) configuration.

    Stores the THR calculation parameters per year/month: the rate
    percentage, the prorate basis (full year vs. proportional), and
    the effective date range.
    """
    _name = 'payroll.thr_config'
    _description = 'Konfigurasi THR (Tunjangan Hari Raya)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, month'

    name = fields.Char(
        string='Nama',
        required=True,
        tracking=True,
    )
    year = fields.Integer(
        string='Tahun',
        required=True,
        tracking=True,
    )
    month = fields.Selection([
        ('1', 'Januari'), ('2', 'Februari'), ('3', 'Maret'),
        ('4', 'April'), ('5', 'Mei'), ('6', 'Juni'),
        ('7', 'Juli'), ('8', 'Agustus'), ('9', 'September'),
        ('10', 'Oktober'), ('11', 'November'), ('12', 'Desember'),
    ], string='Bulan Pembayaran', required=True, tracking=True)
    rate_pct = fields.Float(
        string='Tarif (%)',
        required=True,
        digits=(6, 2),
        default=100.0,
        tracking=True,
        help='Persentase THR terhadap 1 bulan gaji (default 100%).',
    )
    prorate_basis = fields.Selection([
        ('full_year', 'Penuh 1 Tahun (1x gaji)'),
        ('proportional', 'Proporsional (prorate bulan)'),
    ], string='Dasar Prorate', required=True,
       default='full_year', tracking=True,
       help='Penuh: karyawan ≥12 bulan dapat 1x gaji. '
            'Proporsional: prorated berdasarkan masa kerja.',
    )
    effective_from = fields.Date(
        string='Berlaku Mulai',
        required=True,
        tracking=True,
    )
    effective_to = fields.Date(
        string='Berlaku Sampai',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Disetujui'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        ('unique_year_month',
         'UNIQUE(year, month)',
         'Konfigurasi THR per tahun + bulan tidak boleh duplikat!'),
    ]

    @api.constrains('effective_from', 'effective_to')
    def _check_dates(self):
        for rec in self:
            if rec.effective_to and rec.effective_from > rec.effective_to:
                raise ValidationError(_(
                    'Tanggal "Berlaku Mulai" tidak boleh setelah '
                    '"Berlaku Sampai".'
                ))

    @api.constrains('rate_pct')
    def _check_rate(self):
        for rec in self:
            if rec.rate_pct < 0:
                raise ValidationError(_('Tarif THR tidak boleh negatif.'))

    def action_approve(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Hanya record draft yang dapat disetujui.'))
            rec.state = 'approved'

    def action_set_draft(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_(
                    'Hanya record yang sudah disetujui dapat dikembalikan '
                    'ke draft.'
                ))
            rec.state = 'draft'

    def compute_thr(self, monthly_salary, months_employed=12):
        """Compute the THR amount for a worker.

        :param monthly_salary: float — the worker's monthly base salary
        :param months_employed: int — months employed in the THR year
        :return: float THR amount
        """
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_(
                'THR config must be approved before computing THR.'
            ))
        base = monthly_salary * (self.rate_pct / 100.0)
        if self.prorate_basis == 'proportional' and months_employed < 12:
            base = base * (months_employed / 12.0)
        return round(base, 2)