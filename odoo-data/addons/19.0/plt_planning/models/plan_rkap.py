# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PlanRKAP(models.Model):
    """Annual work plan per block × activity × month."""
    _name = 'plan.rkap'
    _description = 'RKAP (Rencana Kerja Anggaran Perusahaan)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year, block_id, activity_code_id, month'

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
    year = fields.Integer(
        string='Year',
        required=True,
        default=lambda self: fields.Date.context_today(self).year,
        tracking=True,
    )
    month = fields.Selection([
        ('1', 'January'), ('2', 'February'), ('3', 'March'),
        ('4', 'April'), ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'), ('9', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December'),
    ], string='Month', required=True, tracking=True)

    # Physical plan
    physical_qty = fields.Float(
        string='Physical Quantity',
        required=True,
        digits=(12, 2),
        tracking=True,
    )
    physical_uom = fields.Char(string='UoM', default='Ha')

    # Manpower plan
    hk_planned = fields.Float(
        string='HK Planned',
        digits=(12, 2),
        tracking=True,
    )

    # Cost plan
    material_cost = fields.Monetary(
        string='Material Cost',
        currency_field='currency_id',
        digits=(12, 2),
        tracking=True,
    )
    labor_cost = fields.Monetary(
        string='Labor Cost',
        currency_field='currency_id',
        digits=(12, 2),
        tracking=True,
    )
    total_cost = fields.Monetary(
        string='Total Cost',
        currency_field='currency_id',
        compute='_compute_total_cost',
        store=True,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)

    version = fields.Integer(string='Version', default=1, tracking=True)
    notes = fields.Text(string='Notes')

    @api.depends('material_cost', 'labor_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = (rec.material_cost or 0.0) + (rec.labor_cost or 0.0)

    def action_propose(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft plans can be proposed.'))
            rec.state = 'proposed'

    def action_approve(self):
        for rec in self:
            if rec.state != 'proposed':
                raise UserError(_('Only proposed plans can be approved.'))
            rec.state = 'approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
