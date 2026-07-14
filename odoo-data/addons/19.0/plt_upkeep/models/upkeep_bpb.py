# -*- coding: utf-8 -*-
from odoo import models, fields, _


class UpkeepBPB(models.Model):
    """Bon Permintaan Barang — material requisition."""
    _name = 'upkeep.bpb'
    _description = 'Bon Permintaan Barang (BPB)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, number'

    number = fields.Char(
        string='BPB Number',
        required=True,
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    requestor_id = fields.Many2one(
        'hr.employee',
        string='Requestor',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    items_description = fields.Text(
        string='Items',
        required=True,
        tracking=True,
        help='List of requested items with quantities.',
    )
    approved_by_id = fields.Many2one(
        'hr.employee',
        string='Approved By',
        ondelete='restrict',
        tracking=True,
    )
    issued_by_id = fields.Many2one(
        'hr.employee',
        string='Issued By',
        ondelete='restrict',
        tracking=True,
    )
    issued_qty = fields.Float(
        string='Issued Quantity',
        digits=(12, 2),
        tracking=True,
    )
    return_qty = fields.Float(
        string='Return Quantity',
        digits=(12, 2),
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('issued', 'Issued'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
    )
    notes = fields.Text(
        string='Notes',
    )

    _sql_constraints = [
        ('unique_number', 'UNIQUE(number)', 'BPB number must be unique!'),
    ]
