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
            CREATE OR REPLACE VIEW report_monthly_cost AS (
                SELECT
                    row_number() OVER () AS id,
                    COALESCE(aaa.date_year, EXTRACT(YEAR FROM NOW())::INTEGER) AS year,
                    COALESCE(aaa.date_month::TEXT, EXTRACT(MONTH FROM NOW())::TEXT) AS month,
                    eb.name AS block_name,
                    COALESCE(SUM(aal.balance), 0) AS total_cost,
                    0.0 AS total_kg,
                    0.0 AS cost_per_kg
                FROM account_analytic_account aaa
                JOIN account_analytic_line aal ON aal.account_id = aaa.id
                JOIN estate_block eb ON aaa.code = 'BLK-' || eb.code
                GROUP BY aaa.date_year, aaa.date_month, eb.name
            )
        """)
