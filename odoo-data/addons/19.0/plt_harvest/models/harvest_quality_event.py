# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HarvestQualityEvent(models.Model):
    _name = 'harvest.quality_event'
    _description = 'Harvest Quality Event / Grading'
    _inherit = ['mail.thread']
    _order = 'id desc'

    # ── Basic Fields ──────────────────────────────────────────
    tph_record_id = fields.Many2one(
        'harvest.tph_record', string='TPH Record', required=True,
        ondelete='cascade', tracking=True,
    )
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
    quantity = fields.Integer(string='Quantity', required=True, tracking=True)
    rate = fields.Float(
        string='Rate (% of total)', digits=(16, 2), tracking=True,
    )
    denda_amount = fields.Float(
        string='Denda Amount', digits=(16, 2),
        compute='_compute_denda_amount', store=True,
    )
    photo = fields.Binary(string='Photo', attachment=True)

    # ── Computed ──────────────────────────────────────────────
    @api.depends('quantity', 'rate')
    def _compute_denda_amount(self):
        for rec in self:
            # Denda amount is computed from matching denda_config
            # For now, placeholder: quantity × rate
            if rec.quantity and rec.rate:
                rec.denda_amount = rec.quantity * rec.rate
            else:
                rec.denda_amount = 0.0
