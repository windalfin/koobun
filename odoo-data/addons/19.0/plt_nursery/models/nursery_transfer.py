# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class NurseryTransfer(models.Model):
    """Transfer seedlings from nursery to field (block)."""
    _name = 'nursery.transfer'
    _description = 'Nursery Transfer to Field'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    batch_id = fields.Many2one('nursery.batch', string='Batch', required=True,
                                ondelete='cascade', tracking=True)
    date = fields.Date(string='Transfer Date', required=True,
                       default=fields.Date.context_today, tracking=True)
    block_id = fields.Many2one('estate.block', string='Target Block', required=True,
                                ondelete='restrict', tracking=True)
    quantity = fields.Integer(string='Quantity Transferred', required=True, tracking=True)
    spacing_m = fields.Float(string='Spacing (m)', digits=(4, 2),
                              default=9.0, tracking=True,
                              help='Planting spacing in meters (e.g., 9m triangular)')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ], string='State', default='draft', required=True, tracking=True)
    notes = fields.Text(string='Notes')

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_complete(self):
        for rec in self:
            rec.state = 'completed'
            # Mark the batch as transferred
            if rec.batch_id.stage != 'transferred':
                rec.batch_id.stage = 'transferred'
                rec.batch_id.block_id = rec.block_id
