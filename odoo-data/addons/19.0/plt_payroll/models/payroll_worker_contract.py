# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PayrollWorkerContract(models.Model):
    _name = 'payroll.worker_contract'
    _description = 'Worker Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'worker_class, employee_id'

    # ── Basic Contract Fields (replacing hr.contract, removed in Odoo 19) ──
    name = fields.Char(
        string='Contract Reference',
        required=True,
        default=lambda self: _('New'),
        tracking=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
    )
    date_end = fields.Date(
        string='End Date',
        tracking=True,
    )
    wage = fields.Monetary(
        string='Wage',
        currency_field='currency_id',
        tracking=True,
        help='Base wage per period (daily rate for BHL/SKU/KHT, monthly for staff).',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        tracking=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('terminated', 'Terminated'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
    )

    # ── Worker Class ────────────────────────────────────────
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

    # ── Contract Type ───────────────────────────────────────
    contract_type = fields.Selection(
        selection=[
            ('PKWT', 'PKWT (Fixed Term)'),
            ('PKWTT', 'PKWTT (Permanent)'),
        ],
        string='Contract Type',
        required=True,
        default='PKWT',
        tracking=True,
    )

    # ── Wage Master Link ────────────────────────────────────
    wage_master_id = fields.Many2one(
        'payroll.wage_master',
        string='Wage Master',
        tracking=True,
        help='Reference to the applicable wage master record.',
    )

    # ── BPJS & PPh 21 Flags ─────────────────────────────────
    bpjs_applicable = fields.Boolean(
        string='BPJS Applicable',
        default=True,
        tracking=True,
    )
    pph21_applicable = fields.Boolean(
        string='PPh 21 Applicable',
        default=True,
        tracking=True,
    )

    # ── Constraints ─────────────────────────────────────────
    @api.constrains('worker_class', 'contract_type')
    def _check_worker_class_contract_type(self):
        for rec in self:
            if rec.worker_class == 'staff' and rec.contract_type not in ('PKWTT',):
                raise ValidationError(_(
                    'Staff workers must have PKWTT contract type.'
                ))

    # ── Create ──────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'payroll.worker_contract') or _('New')
            if vals.get('worker_class') and not vals.get('wage_master_id'):
                wage = self.env['payroll.wage_master'].search([
                    ('worker_class', '=', vals['worker_class']),
                    ('state', '=', 'approved'),
                ], limit=1)
                if wage:
                    vals['wage_master_id'] = wage.id
        return super().create(vals_list)
