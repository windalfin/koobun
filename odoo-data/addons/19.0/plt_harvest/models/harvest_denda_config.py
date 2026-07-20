# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HarvestDendaConfig(models.Model):
    _name = 'harvest.denda_config'
    _description = 'Denda (Harvest Penalty) Configuration'
    _inherit = ['mail.thread']
    _order = 'date_from desc, id desc'

    # ── Basic Fields ──────────────────────────────────────────
    event_type = fields.Selection(
        selection=[
            ('mentah', 'Mentah (Unripe)'),
            ('tangkai_panjang', 'Tangkai Panjang (Long Stalk)'),
            ('brondolan_tidak_dikutip', 'Brondolan Tidak Dikutip'),
            ('buah_tinggal', 'Buah Tinggal (Left Behind)'),
            ('pelepah_sengkleh', 'Pelepah Sengkleh'),
        ],
        string='Event Type', required=True, tracking=True,
    )
    rate_per_unit = fields.Float(
        string='Rate per Unit', digits=(16, 2), required=True, tracking=True,
        help='Penalty amount per unit/occurrence.',
    )

    # ── Effective Dates ───────────────────────────────────────
    date_from = fields.Date(string='Valid From', required=True, tracking=True)
    date_to = fields.Date(string='Valid To', tracking=True)

    # ── Status ────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
        ],
        string='State', default='draft', required=True, tracking=True,
    )

    # ── Constraints ──────────────────────────────────────────
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_to and rec.date_from and rec.date_to < rec.date_from:
                raise ValidationError(_(
                    'Valid To date must be after Valid From date.'
                ))

    # ── Actions ──────────────────────────────────────────────
    def action_approve(self):
        self.write({'state': 'approved'})

    def action_draft(self):
        self.write({'state': 'draft'})
