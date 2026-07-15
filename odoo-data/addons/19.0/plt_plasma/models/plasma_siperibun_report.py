# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PlasmaSiperibunReport(models.Model):
    """SIPERIBUN — 6-monthly reporting pack for the plasma program."""
    _name = 'plasma.siperibun_report'
    _description = 'Laporan SIPERIBUN (6 Bulanan)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'period_end desc, id desc'

    period_start = fields.Date(
        string='Periode Awal',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    period_end = fields.Date(
        string='Periode Akhir',
        required=True,
        tracking=True,
    )
    total_farmers = fields.Integer(
        string='Jumlah Petani',
        default=0,
        tracking=True,
    )
    total_delivery_kg = fields.Float(
        string='Total Kiriman (kg)',
        digits=(12, 2),
        default=0.0,
        tracking=True,
    )
    total_payment = fields.Monetary(
        string='Total Pembayaran',
        currency_field='currency_id',
        default=0.0,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Disampaikan'),
    ], string='Status', default='draft', required=True, tracking=True)
    notes = fields.Text(string='Catatan')

    @api.constrains('period_start', 'period_end')
    def _check_period(self):
        for rec in self:
            if rec.period_start and rec.period_end \
                    and rec.period_start > rec.period_end:
                raise UserError(_(
                    'Periode awal tidak boleh setelah periode akhir.'
                ))

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(
                    'Hanya laporan berstatus draft yang dapat disampaikan.'
                ))
            rec.state = 'submitted'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'