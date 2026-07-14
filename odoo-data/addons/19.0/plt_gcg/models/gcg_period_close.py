# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class GCGPeriodCloseChecklist(models.Model):
    """Period close and locking checklist.

    Contains checklist items that must be verified before a period
    (month/quarter/year) can be closed.
    """
    _name = 'gcg.period.close.checklist'
    _inherit = ['mail.thread']
    _description = 'GCG Period Close Checklist'
    _order = 'period_start desc, id desc'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    period_start = fields.Date(
        string='Period Start',
        required=True,
        tracking=True,
    )
    period_end = fields.Date(
        string='Period End',
        required=True,
        tracking=True,
    )
    item_ids = fields.One2many(
        'gcg.period.close.item',
        'checklist_id',
        string='Checklist Items',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('locked', 'Locked'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
    )

    def action_start(self):
        self.state = 'in_progress'

    def action_complete(self):
        self.state = 'completed'

    def action_lock(self):
        self.state = 'locked'


class GCGPeriodCloseItem(models.Model):
    """Individual checklist item within a period close checklist."""
    _name = 'gcg.period.close.item'
    _description = 'GCG Period Close Item'
    _order = 'sequence, id'

    checklist_id = fields.Many2one(
        'gcg.period.close.checklist',
        string='Checklist',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    check_type = fields.Selection(
        [
            ('manual', 'Manual'),
            ('system', 'System'),
        ],
        string='Check Type',
        default='manual',
        required=True,
    )
    model_to_check = fields.Char(
        string='Model to Check',
    )
    domain_filter = fields.Char(
        string='Domain Filter',
    )
    expected_result = fields.Text(
        string='Expected Result',
    )
    actual_result = fields.Text(
        string='Actual Result',
    )
    is_compliant = fields.Boolean(
        string='Compliant',
    )
    verified_by = fields.Many2one(
        'res.users',
        string='Verified By',
    )
    verified_at = fields.Datetime(
        string='Verified At',
    )
