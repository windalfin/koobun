# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PayrollPtkpTable(models.Model):
    """PTKP (Penghasilan Tidak Kena Pajak) table.

    Holds the non-taxable income thresholds per taxpayer category
    (TK/0, TK/1, K/0, K/1, K/2, K/3, etc.) with effective dates.
    """
    _name = 'payroll.ptkp_table'
    _description = 'Tabel PTKP (Penghasilan Tidak Kena Pajak)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'effective_from desc, code'

    code = fields.Char(
        string='Kode PTKP',
        required=True,
        tracking=True,
        help='Kategori PTKP, mis. TK/0, TK/1, K/0, K/1, K/2, K/3.',
    )
    name = fields.Char(
        string='Keterangan',
        required=True,
        tracking=True,
        help='Keterangan kategori PTKP.',
    )
    amount = fields.Float(
        string='Jumlah PTKP (Rp/tahun)',
        required=True,
        digits=(16, 2),
        tracking=True,
        help='Besaran Penghasilan Tidak Kena Pajak per tahun.',
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
        ('unique_code_effective',
         'UNIQUE(code, effective_from)',
         'Kode PTKP dengan tanggal berlaku yang sama tidak boleh duplikat!'),
    ]

    @api.constrains('effective_from', 'effective_to')
    def _check_dates(self):
        for rec in self:
            if rec.effective_to and rec.effective_from > rec.effective_to:
                raise ValidationError(_(
                    'Tanggal "Berlaku Mulai" tidak boleh setelah '
                    '"Berlaku Sampai".'
                ))

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError(_(
                    'Jumlah PTKP tidak boleh negatif.'
                ))

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

    @api.model
    def get_ptkp_amount(self, code, date):
        """Return the approved PTKP amount for *code* effective on *date*.

        :param code: PTKP category code, e.g. ``'TK/0'``
        :param date: date string or date object
        :return: float amount, 0.0 if not found
        """
        domain = [
            ('code', '=', code),
            ('state', '=', 'approved'),
            ('effective_from', '<=', date),
        ]
        rec = self.search(domain, order='effective_from desc', limit=1)
        if rec and (not rec.effective_to or rec.effective_to >= date):
            return rec.amount
        return 0.0