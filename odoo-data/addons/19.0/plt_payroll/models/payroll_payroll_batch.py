# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PayrollPayrollBatch(models.Model):
    _name = 'payroll.payroll_batch'
    _description = 'Payroll Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'period_start desc, id desc'

    # ── Date Range ──────────────────────────────────────────
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

    # ── References ──────────────────────────────────────────
    afdeling_id = fields.Many2one(
        'estate.afdeling',
        string='Afdeling',
        tracking=True,
    )
    worker_ids = fields.Many2many(
        'hr.employee',
        'payroll_batch_worker_rel',
        'batch_id',
        'employee_id',
        string='Workers',
        tracking=True,
    )

    # ── State ───────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('calculated', 'Calculated'),
            ('verified', 'Verified'),
            ('approved', 'Approved'),
            ('posted', 'Posted'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
    )

    # ── Totals ──────────────────────────────────────────────
    total_gross = fields.Float(
        string='Total Gross',
        digits=(16, 2),
        compute='_compute_totals',
        store=True,
    )
    total_deductions = fields.Float(
        string='Total Deductions',
        digits=(16, 2),
        compute='_compute_totals',
        store=True,
    )
    total_net = fields.Float(
        string='Total Net Pay',
        digits=(16, 2),
        compute='_compute_totals',
        store=True,
    )

    # ── Payslip Lines ───────────────────────────────────────
    payslip_line_ids = fields.One2many(
        'payroll.payslip_line',
        'payroll_batch_id',
        string='Payslip Lines',
        readonly=True,
    )

    # ── Constraints ─────────────────────────────────────────
    @api.constrains('period_start', 'period_end')
    def _check_period(self):
        for rec in self:
            if rec.period_start > rec.period_end:
                raise UserError(_(
                    'Period Start cannot be after Period End.'
                ))

    # ── Actions ─────────────────────────────────────────────
    def action_calculate(self):
        """Calculate payroll for all workers in this batch."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_(
                'Only draft batches can be calculated.'
            ))
        self.payslip_line_ids.unlink()
        lines_vals = []
        for worker in self.worker_ids:
            lines_vals.append({
                'payroll_batch_id': self.id,
                'employee_id': worker.id,
                'hk_count': 0,  # To be filled from BKM
                'daily_base': 0.0,
            })
        if lines_vals:
            self.env['payroll.payslip_line'].create(lines_vals)
        self.state = 'calculated'

    def action_verify(self):
        self.ensure_one()
        if self.state != 'calculated':
            raise UserError(_('Batch must be calculated first.'))
        self.state = 'verified'

    def action_approve(self):
        self.ensure_one()
        if self.state != 'verified':
            raise UserError(_('Batch must be verified first.'))
        self.state = 'approved'

    def action_post(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_('Batch must be approved first.'))
        self.state = 'posted'

    def action_set_draft(self):
        self.ensure_one()
        if self.state == 'posted':
            raise UserError(_('Cannot reset a posted batch to draft.'))
        self.state = 'draft'

    # ── Compute Totals ──────────────────────────────────────
    @api.depends('payslip_line_ids.net_pay')
    def _compute_totals(self):
        for batch in self:
            lines = batch.payslip_line_ids
            gross = sum(lines.mapped('daily_base') or [0.0]) * \
                sum(lines.mapped('hk_count') or [0])
            deductions = sum(lines.mapped('pph21_amount') or [0.0]) + \
                sum(lines.mapped('denda_amount') or [0.0])
            # Add BPJS employee portion
            for line in lines:
                if line.bpjs_amounts:
                    for v in line.bpjs_amounts.values():
                        deductions += v.get('employee', 0.0)
            batch.total_gross = gross
            batch.total_deductions = deductions
            batch.total_net = gross - deductions

    # ── Create ──────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
