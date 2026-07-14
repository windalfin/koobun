# -*- coding: utf-8 -*-
import json
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PayrollPayslipLine(models.Model):
    _name = 'payroll.payslip_line'
    _description = 'Payslip Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'payroll_batch_id, employee_id'

    # ── References ──────────────────────────────────────────
    payroll_batch_id = fields.Many2one(
        'payroll.payroll_batch',
        string='Payroll Batch',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True,
    )

    # ── HK from BKM (PLT-04) ────────────────────────────────
    hk_count = fields.Integer(
        string='HK Count',
        default=0,
        tracking=True,
        help='Number of working days (Hari Kerja) from BKM (PLT-04).',
    )

    # ── Daily Base Wage ─────────────────────────────────────
    daily_base = fields.Float(
        string='Daily Base Wage',
        digits=(16, 2),
        tracking=True,
    )

    # ── Premi / Denda from PLT-05 ───────────────────────────
    premi_amount = fields.Float(
        string='Premi Amount',
        digits=(16, 2),
        tracking=True,
        help='Harvest premium amount from PLT-05.',
    )
    denda_amount = fields.Float(
        string='Denda Amount',
        digits=(16, 2),
        tracking=True,
        help='Penalty amount from PLT-05.',
    )

    # ── BPJS Amounts (JSON) ─────────────────────────────────
    bpjs_amounts = fields.Json(
        string='BPJS Amounts',
        tracking=True,
        help='JSON dict of BPJS type → {employer, employee} amounts.',
    )

    # ── PPh 21 Amount ───────────────────────────────────────
    pph21_amount = fields.Float(
        string='PPh 21 Amount',
        digits=(16, 2),
        tracking=True,
    )

    # ── THT (JHT) Amount ────────────────────────────────────
    tht_amount = fields.Float(
        string='THT Amount',
        digits=(16, 2),
        tracking=True,
        help='Old-age savings deducted from pay (JHT employee portion).',
    )

    # ── Net Pay (computed) ──────────────────────────────────
    net_pay = fields.Float(
        string='Net Pay',
        digits=(16, 2),
        compute='_compute_net_pay',
        store=True,
    )

    # ── Compute Net Pay ─────────────────────────────────────
    @api.depends('daily_base', 'hk_count', 'premi_amount', 'denda_amount',
                 'pph21_amount', 'tht_amount', 'bpjs_amounts')
    def _compute_net_pay(self):
        for line in self:
            gross = (line.daily_base * line.hk_count) + line.premi_amount
            deductions = line.denda_amount + line.pph21_amount + \
                line.tht_amount
            if line.bpjs_amounts:
                try:
                    bpjs = line.bpjs_amounts if isinstance(
                        line.bpjs_amounts, dict
                    ) else json.loads(line.bpjs_amounts)
                    for v in bpjs.values():
                        deductions += v.get('employee', 0.0)
                except (json.JSONDecodeError, TypeError) as exc:
                    _logger.warning(
                        'Invalid BPJS JSON for payslip line %s: %s',
                        line.id, exc,
                    )
            line.net_pay = gross - deductions

    # ── Constraints ─────────────────────────────────────────
    @api.constrains('hk_count', 'daily_base')
    def _check_positive(self):
        for line in self:
            if line.hk_count < 0:
                raise ValidationError(_('HK count cannot be negative.'))
            if line.daily_base < 0:
                raise ValidationError(_('Daily base wage cannot be negative.'))

    # ── SQL Constraints ─────────────────────────────────────
    _sql_constraints = [
        (
            'payslip_line_employee_batch_unique',
            'unique(employee_id, payroll_batch_id)',
            'Employee already has a payslip line in this batch!',
        ),
    ]

    # ── Create ──────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
