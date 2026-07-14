# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HarvestTaksasi(models.Model):
    _name = 'harvest.taksasi'
    _description = 'Taksasi (D-1 Crop Estimate)'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    # ── Basic Fields ──────────────────────────────────────────
    date = fields.Date(string='Date', required=True, tracking=True)
    block_id = fields.Many2one(
        'estate.block', string='Block', required=True,
        ondelete='restrict', tracking=True,
    )
    section = fields.Char(string='Section', tracking=True)
    pokok_sampled = fields.Integer(string='Pokok Sampled', tracking=True)
    bunches_counted = fields.Integer(string='Bunches Counted', tracking=True)

    # ── AKP (Angka Kerapatan Panen) ───────────────────────────
    AKP = fields.Float(
        string='AKP', digits=(16, 4), tracking=True,
        help='Angka Kerapatan Panen (Harvest Density Rate)',
    )

    # ── Estimates ─────────────────────────────────────────────
    estimated_janjang = fields.Integer(
        string='Estimated Janjang', tracking=True,
        help='Estimated bunches for next day',
    )
    estimated_tonnage = fields.Float(
        string='Estimated Tonnage', digits=(16, 2), tracking=True,
        help='Estimated tonnage for next day',
    )

    # ── Resource Planning ─────────────────────────────────────
    required_harvesters = fields.Integer(
        string='Required Harvesters', tracking=True,
    )
    required_trucks = fields.Integer(
        string='Required Trucks', tracking=True,
    )

    # ── Status ────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        string='State', default='draft', required=True, tracking=True,
    )

    # ── Constraints ──────────────────────────────────────────
    @api.constrains('pokok_sampled', 'bunches_counted')
    def _check_taksasi_positive(self):
        for rec in self:
            if rec.pokok_sampled and rec.pokok_sampled <= 0:
                raise ValidationError(_('Pokok sampled must be positive.'))
            if rec.bunches_counted and rec.bunches_counted < 0:
                raise ValidationError(_('Bunches counted cannot be negative.'))

    # ── Actions ──────────────────────────────────────────────
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})
