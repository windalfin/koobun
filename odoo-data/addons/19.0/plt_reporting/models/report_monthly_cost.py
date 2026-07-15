# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportMonthlyCost(models.Model):
    """Monthly cost per block & per kg TBS."""
    _name = 'report.monthly_cost'
    _description = 'Monthly Cost Report'
    _auto = False
    _order = 'year desc, month, block_name'

    year = fields.Integer(string='Year', readonly=True)
    month = fields.Char(string='Month', readonly=True)
    block_name = fields.Char(string='Block', readonly=True)
    total_cost = fields.Float(string='Total Cost', digits=(12, 2), readonly=True)
    total_kg = fields.Float(string='Total KG', digits=(12, 2), readonly=True)
    cost_per_kg = fields.Float(string='Cost per KG', digits=(12, 4), readonly=True)

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS report_monthly_cost;
            CREATE OR REPLACE VIEW report_monthly_cost AS (
                SELECT
                    row_number() OVER () AS id,
                    EXTRACT(YEAR FROM aal.date)::INTEGER AS year,
                    EXTRACT(MONTH FROM aal.date)::TEXT AS month,
                    eb.name AS block_name,
                    COALESCE(SUM(aal.amount), 0) AS total_cost,
                    0.0 AS total_kg,
                    0.0 AS cost_per_kg
                FROM account_analytic_line aal
                JOIN account_analytic_account aaa ON aaa.id = aal.account_id
                JOIN estate_block eb ON aaa.code = 'BLK-' || eb.code
                GROUP BY EXTRACT(YEAR FROM aal.date), EXTRACT(MONTH FROM aal.date), eb.name
            )
        """)
