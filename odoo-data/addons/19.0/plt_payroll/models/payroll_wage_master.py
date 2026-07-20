# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PayrollWageMaster(models.Model):
    _name = 'payroll.wage_master'
    _description = 'Wage Master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'effective_from desc, id desc'

    # ── Basic Fields ────────────────────────────────────────
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    worker_class = fields.Selection(
        selection=[
            ('BHL', 'BHL (Daily Casual)'),
            ('SKU', 'SKU (Permanent Daily)'),
            ('KHT', 'KHT (Permanent Daily)'),
            ('staff', 'Staff (Monthly)'),
        ],
        string='Worker Class',
        required=True,
        tracking=True,
    )

    # ── Wage Fields ─────────────────────────────────────────
    daily_wage = fields.Float(
        string='Daily Wage',
        digits=(16, 2),
        tracking=True,
        help='Base daily wage amount.',
    )
    hourly_rate = fields.Float(
        string='Hourly Rate',
        digits=(16, 2),
        tracking=True,
        help='Hourly rate (daily_wage / 7 for standard day).',
    )

    # ── Effective Dates ─────────────────────────────────────
    effective_from = fields.Date(
        string='Effective From',
        required=True,
        tracking=True,
    )
    effective_to = fields.Date(
        string='Effective To',
        tracking=True,
    )

    # ── State ───────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('expired', 'Expired'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
    )

    # ── Constraints ─────────────────────────────────────────
    @api.constrains('effective_from', 'effective_to')
    def _check_dates(self):
        for rec in self:
            if rec.effective_to and rec.effective_from > rec.effective_to:
                raise ValidationError(_(
                    'Effective From date cannot be after Effective To date.'
                ))

    @api.constrains('daily_wage', 'hourly_rate')
    def _check_positive_wages(self):
        for rec in self:
            if rec.daily_wage < 0:
                raise ValidationError(_('Daily wage cannot be negative.'))
            if rec.hourly_rate < 0:
                raise ValidationError(_('Hourly rate cannot be negative.'))

    # ── Actions ─────────────────────────────────────────────
    def action_approve(self):
        """Approve the wage master record."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft records can be approved.'))
            rec.state = 'approved'

    def action_set_draft(self):
        """Reset the record to draft."""
        for rec in self:
            if rec.state not in ('approved', 'expired'):
                raise UserError(_(
                    'Only approved or expired records can be reset to draft.'
                ))
            rec.state = 'draft'

    # ── Scheduled Action ────────────────────────────────────
    def _cron_expire_wages(self):
        """Cron to expire wage records whose effective_to has passed."""
        today = fields.Date.today()
        expired = self.search([
            ('state', '=', 'approved'),
            ('effective_to', '<=', today),
        ])
        expired.write({'state': 'expired'})
