# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class NurseryBatch(models.Model):
    """Seedling batch — a group of seedlings from the same source."""
    _name = 'nursery.batch'
    _description = 'Nursery Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_received desc, variety'

    name = fields.Char(string='Batch Name', required=True, tracking=True)
    variety = fields.Char(string='Variety', required=True, tracking=True,
                          help='e.g., DxP Simalungun, DxP PPKS 540, Tenera')
    source = fields.Char(string='Source', required=True, tracking=True,
                         help='Seed producer or supplier name')
    quantity_received = fields.Integer(string='Quantity Received', required=True, tracking=True)
    date_received = fields.Date(string='Date Received', required=True,
                                 default=fields.Date.context_today, tracking=True)
    germination_rate = fields.Float(string='Germination Rate (%)', digits=(5, 2),
                                     tracking=True)
    survival_count = fields.Integer(string='Survival Count', tracking=True)
    stage = fields.Selection([
        ('pre_nursery', 'Pre-Nursery'),
        ('main_nursery', 'Main Nursery'),
        ('ready_transfer', 'Ready for Transfer'),
        ('transferred', 'Transferred'),
        ('cancelled', 'Cancelled'),
    ], string='Stage', default='pre_nursery', required=True, tracking=True)
    block_id = fields.Many2one('estate.block', string='Transfer Block',
                                ondelete='restrict', tracking=True)
    notes = fields.Text(string='Notes')

    seedling_ids = fields.One2many('nursery.seedling', 'batch_id', string='Seedlings')
    culling_ids = fields.One2many('nursery.culling', 'batch_id', string='Cullings')
    transfer_ids = fields.One2many('nursery.transfer', 'batch_id', string='Transfers')

    def action_advance_stage(self):
        for rec in self:
            if rec.stage == 'pre_nursery':
                rec.stage = 'main_nursery'
            elif rec.stage == 'main_nursery':
                rec.stage = 'ready_transfer'
