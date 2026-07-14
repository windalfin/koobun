# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PlanRKH(models.Model):
    """Daily work order — the parent of BKM records."""
    _name = 'plan.rkh'
    _description = 'RKH (Rencana Kerja Harian)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, block_id'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    mandor_id = fields.Many2one(
        'hr.employee',
        string='Mandor',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    block_id = fields.Many2one(
        'estate.block',
        string='Block',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    activity_code_id = fields.Many2one(
        'upkeep.activity_code',
        string='Activity',
        required=True,
        ondelete='restrict',
        tracking=True,
    )

    # Target
    target_qty = fields.Float(
        string='Target Quantity',
        digits=(12, 2),
        tracking=True,
    )
    target_uom = fields.Char(string='UoM', default='Ha')

    # Workers
    worker_count = fields.Integer(
        string='Worker Count',
        default=1,
        tracking=True,
    )
    worker_ids = fields.Many2many(
        'hr.employee', 'plan_rkh_worker_rel',
        'rkh_id', 'employee_id',
        string='Workers',
        tracking=True,
    )

    # Materials
    planned_materials = fields.Text(
        string='Planned Materials',
        tracking=True,
    )

    # Link to BKM
    bkm_ids = fields.One2many(
        'upkeep.bkm', 'rkh_id',
        string='BKM Records',
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)
    notes = fields.Text(string='Notes')

    def action_issue(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft RKH can be issued.'))
            rec.state = 'issued'

    def action_complete(self):
        for rec in self:
            if rec.state != 'issued':
                raise UserError(_('Only issued RKH can be completed.'))
            rec.state = 'completed'
