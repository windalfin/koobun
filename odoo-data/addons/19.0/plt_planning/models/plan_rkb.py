# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PlanRKB(models.Model):
    """Monthly work plan derived from RKAP with adjustment workflow."""
    _name = 'plan.rkb'
    _description = 'RKB (Rencana Kerja Bulanan)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year, month, block_id'

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

    physical_qty = fields.Float(
        string='Physical Quantity',
        required=True,
        digits=(12, 2),
        tracking=True,
    )
    hk_planned = fields.Float(
        string='HK Planned',
        digits=(12, 2),
        tracking=True,
    )
    deviation_pct = fields.Float(
        string='Deviation from RKAP (%)',
        compute='_compute_deviation',
        store=True,
        tracking=True,
    )
    deviation_justification = fields.Text(
        string='Deviation Justification',
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)
    notes = fields.Text(string='Notes')

    @api.depends('physical_qty', 'block_id', 'activity_code_id', 'year', 'month')
    def _compute_deviation(self):
        for rec in self:
            rkap = self.env['plan.rkap'].search([
                ('block_id', '=', rec.block_id.id),
                ('activity_code_id', '=', rec.activity_code_id.id),
                ('year', '=', rec.year),
                ('month', '=', rec.month),
                ('state', '=', 'approved'),
            ], limit=1)
            if rkap and rkap.physical_qty:
                rec.deviation_pct = ((rec.physical_qty - rkap.physical_qty) /
                                     rkap.physical_qty * 100)
            else:
                rec.deviation_pct = 0.0

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft RKB can be submitted.'))
            rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_('Only submitted RKB can be approved.'))
            rec.state = 'approved'
