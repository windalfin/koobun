# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PayrollBpjsConfig(models.Model):
    _name = 'payroll.bpjs_config'
    _description = 'BPJS Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'effective_from desc, id desc'

    # ── Basic Fields ────────────────────────────────────────
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    bpjs_type = fields.Selection(
        selection=[
            ('kesehatan', 'BPJS Kesehatan'),
            ('JHT', 'JHT (Jaminan Hari Tua)'),
            ('JP', 'JP (Jaminan Pensiun)'),
            ('JKK', 'JKK (Jaminan Kecelakaan Kerja)'),
            ('JKM', 'JKM (Jaminan Kematian)'),
        ],
        string='BPJS Type',
        required=True,
        tracking=True,
    )

    # ── Rate Fields ─────────────────────────────────────────
    employer_pct = fields.Float(
        string='Employer Rate (%)',
        digits=(16, 4),
        tracking=True,
    )
    employee_pct = fields.Float(
        string='Employee Rate (%)',
        digits=(16, 4),
        tracking=True,
    )
    ceiling_amount = fields.Float(
        string='Ceiling Amount',
        digits=(16, 2),
        tracking=True,
        help='Maximum base wage used for BPJS calculation.',
    )

    # ── Risk Class (JKK-specific) ───────────────────────────
    risk_class = fields.Char(
        string='Risk Class',
        help='Risk classification for JKK premium rate.',
        tracking=True,
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

    @api.constrains('employer_pct', 'employee_pct')
    def _check_rates(self):
        for rec in self:
            if rec.employer_pct < 0 or rec.employee_pct < 0:
                raise ValidationError(_('Rates cannot be negative.'))

    # ── Actions ─────────────────────────────────────────────
    def action_approve(self):
        """Approve the BPJS config record."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft records can be approved.'))
            rec.state = 'approved'

    def action_set_draft(self):
        """Reset to draft."""
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_(
                    'Only approved records can be reset to draft.'
                ))
            rec.state = 'draft'

    # ── Compute BPJS Amounts ────────────────────────────────
    def compute_contribution(self, base_wage):
        """Compute employer and employee BPJS contributions from a base wage.
        Returns (employer_amount, employee_amount)."""
        self.ensure_one()
        effective_base = min(base_wage, self.ceiling_amount) \
            if self.ceiling_amount else base_wage
        employer = effective_base * self.employer_pct / 100.0
        employee = effective_base * self.employee_pct / 100.0
        return employer, employee
