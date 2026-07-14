# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class UpkeepBKM(models.Model):
    """Buku Kerja Mandor — daily field work record."""
    _name = 'upkeep.bkm'
    _description = 'Buku Kerja Mandor (BKM)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id'

    # ── Header ──────────────────────────────────────────────
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
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('verified', 'Verified'),
            ('approved', 'Approved'),
            ('posted', 'Posted'),
            ('cancelled', 'Cancelled'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
    )

    # ── Workers & Output ────────────────────────────────────
    worker_count = fields.Integer(
        string='Worker Count',
        default=1,
        tracking=True,
    )
    worker_ids = fields.Many2many(
        'hr.employee', 'upkeep_bkm_worker_rel',
        'bkm_id', 'employee_id',
        string='Workers',
        tracking=True,
    )
    output_per_worker = fields.Float(
        string='Output / Worker',
        digits=(12, 2),
        tracking=True,
    )
    output_uom = fields.Char(
        string='UoM',
        default='HK',
    )

    # ── Materials ───────────────────────────────────────────
    material_consumed = fields.Text(
        string='Materials Consumed',
        tracking=True,
        help='Description of materials used (type, quantity).',
    )

    # ── Notes ───────────────────────────────────────────────
    notes = fields.Text(
        string='Notes',
    )

    # ── State Actions ───────────────────────────────────────
    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft BKMs can be submitted.'))
            rec.state = 'submitted'

    def action_verify(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_('Only submitted BKMs can be verified.'))
            rec.state = 'verified'

    def action_approve(self):
        for rec in self:
            if rec.state != 'verified':
                raise UserError(_('Only verified BKMs can be approved.'))
            rec.state = 'approved'

    def action_post(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_('Only approved BKMs can be posted.'))
            rec.state = 'posted'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
