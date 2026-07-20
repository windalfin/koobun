# -*- coding: utf-8 -*-
from odoo import models, fields


class NurseryCulling(models.Model):
    """Culling record — seedlings rejected with reason."""
    _name = 'nursery.culling'
    _description = 'Nursery Culling Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    batch_id = fields.Many2one('nursery.batch', string='Batch', required=True,
                                ondelete='cascade', tracking=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today,
                       tracking=True)
    quantity = fields.Integer(string='Quantity Culled', required=True, tracking=True)
    reason = fields.Selection([
        ('abnormal_growth', 'Abnormal Growth'),
        ('pest_disease', 'Pest / Disease'),
        ('physical_damage', 'Physical Damage'),
        ('poor_germination', 'Poor Germination'),
        ('other', 'Other'),
    ], string='Reason', required=True, tracking=True)
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
