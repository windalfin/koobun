# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PayrollSalaryRule(models.Model):
    _name = 'payroll.salary_rule'
    _description = 'Salary Rule (Standalone)'
    _inherit = ['mail.thread']

    name = fields.Char(string='Rule Name', required=True, tracking=True)
    code = fields.Char(string='Rule Code', required=True, tracking=True)
    rule_type = fields.Selection(
        selection=[
            ('daily_wage', 'Daily Wage'),
            ('premi', 'Premi (Harvest Premium)'),
            ('denda', 'Denda (Penalty)'),
            ('THR', 'THR (Religious Holiday Allowance)'),
            ('natura', 'Natura (In-Kind)'),
            ('bpjs', 'BPJS'),
            ('pph21', 'PPh 21'),
        ],
        string='Rule Type',
        tracking=True,
    )
    auto_compute = fields.Boolean(
        string='Auto Compute',
        default=True,
        tracking=True,
        help='If enabled, this rule is automatically included in payroll computation.',
    )
    source_model = fields.Char(
        string='Source Model',
        tracking=True,
        help='Technical name of the source model providing data for this rule.',
    )
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)
    note = fields.Text(string='Description')

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Rule code must be unique!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('rule_type') and not vals.get('source_model'):
                mapping = {
                    'premi': 'plt_harvest',
                    'denda': 'plt_harvest',
                    'daily_wage': 'plt_payroll',
                    'THR': 'plt_payroll',
                    'natura': 'plt_payroll',
                    'bpjs': 'plt_payroll',
                    'pph21': 'plt_payroll',
                }
                if vals['rule_type'] in mapping:
                    vals['source_model'] = mapping[vals['rule_type']]
        return super().create(vals_list)
