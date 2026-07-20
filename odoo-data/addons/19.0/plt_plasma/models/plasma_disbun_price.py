# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PlasmaDisbunPrice(models.Model):
    """Effective-dated government (Disbun) FFB price table by age band.

    Stores the price per kg of TBS (Fresh Fruit Bunches) as published by
    Dinas Perkebunan, segmented by the age of the palm trees, with an
    effective date range.
    """
    _name = 'plasma.disbun_price'
    _description = 'Harga Disbun per Kelompok Umur Tanaman'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'effective_from desc, age_band_min'

    name = fields.Char(
        string='Nama',
        compute='_compute_name',
        store=True,
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
    age_band_min = fields.Integer(
        string='Umur Minimum (tahun)',
        required=True,
        default=0,
        tracking=True,
    )
    age_band_max = fields.Integer(
        string='Umur Maksimum (tahun)',
        required=True,
        tracking=True,
    )
    price_per_kg = fields.Float(
        string='Harga per KG (Rp)',
        required=True,
        digits=(12, 4),
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

    @api.depends('age_band_min', 'age_band_max', 'effective_from')
    def _compute_name(self):
        for rec in self:
            eff = ''
            if rec.effective_from:
                eff = rec.effective_from.strftime('%Y-%m-%d')
            rec.name = f'Umur {rec.age_band_min}-{rec.age_band_max} thn ({eff})'

    @api.constrains('effective_from', 'effective_to')
    def _check_dates(self):
        for rec in self:
            if rec.effective_to and rec.effective_from > rec.effective_to:
                raise ValidationError(_(
                    'Tanggal "Berlaku Mulai" tidak boleh setelah '
                    '"Berlaku Sampai".'
                ))

    @api.constrains('age_band_min', 'age_band_max')
    def _check_age_band(self):
        for rec in self:
            if rec.age_band_max < rec.age_band_min:
                raise ValidationError(_(
                    'Umur maksimum tidak boleh lebih kecil dari umur minimum.'
                ))

    @api.constrains('price_per_kg')
    def _check_price(self):
        for rec in self:
            if rec.price_per_kg < 0:
                raise ValidationError(_(
                    'Harga per KG tidak boleh negatif.'
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
    def get_price_for_age(self, age, date):
        """Return the approved Disbun price for a tree of *age* on *date*.

        :param age: int — age of the palm tree in years
        :param date: date string or date object
        :return: float price per kg, 0.0 if not found
        """
        domain = [
            ('state', '=', 'approved'),
            ('age_band_min', '<=', age),
            ('age_band_max', '>=', age),
            ('effective_from', '<=', date),
        ]
        rec = self.search(domain, order='effective_from desc', limit=1)
        if rec and (not rec.effective_to or rec.effective_to >= date):
            return rec.price_per_kg
        return 0.0