# -*- coding: utf-8 -*-
from odoo import models, fields


class NurserySeedling(models.Model):
    """Individual seedling tracking within a batch."""
    _name = 'nursery.seedling'
    _description = 'Nursery Seedling'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    batch_id = fields.Many2one('nursery.batch', string='Batch', required=True,
                                ondelete='cascade', tracking=True)
    tag_number = fields.Char(string='Tag Number', tracking=True)
    status = fields.Selection([
        ('healthy', 'Healthy'),
        ('culled', 'Culled'),
        ('transferred', 'Transferred'),
    ], string='Status', default='healthy', required=True, tracking=True)
    cull_reason = fields.Text(string='Cull Reason')
    transfer_date = fields.Date(string='Transfer Date')
    notes = fields.Text(string='Notes')
