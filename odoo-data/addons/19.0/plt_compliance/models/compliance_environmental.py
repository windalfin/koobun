# -*- coding: utf-8 -*-
from odoo import models, fields


class ComplianceEnvironmental(models.Model):
    """Environmental records: HCV, fire watch, chemical usage."""
    _name = 'compliance.environmental'
    _description = 'Environmental Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, tracking=True)
    record_type = fields.Selection([
        ('hcv', 'HCV Area Monitoring'),
        ('riparian', 'Riparian Buffer'),
        ('fire_watch', 'Fire Watch'),
        ('chemical', 'Chemical Usage Summary'),
        ('waste', 'Waste Management'),
        ('other', 'Other'),
    ], string='Type', required=True, tracking=True)
    block_id = fields.Many2one('estate.block', string='Block', ondelete='restrict', tracking=True)
    description = fields.Text(string='Description', required=True, tracking=True)
    photo = fields.Binary(string='Photo', tracking=True)
    status = fields.Selection([
        ('recorded', 'Recorded'),
        ('reviewed', 'Reviewed'),
        ('action_required', 'Action Required'),
    ], string='Status', default='recorded', required=True, tracking=True)
    notes = fields.Text(string='Notes')
