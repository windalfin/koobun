# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportMonthlyCost(models.Model):
    """Monthly cost per block & per kg TBS."""
    _name = 'report.monthly_cost'
    _description = 'Monthly Cost Report'
    _auto = False
    _order = 'year desc, month, block_id'

    year = fields.Integer(string='Year', readonly=True)
    month = fields.Selection([
        ('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'),
        ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Aug'),
        ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec'),
    ], string='Month', readonly=True)
    block_id = fields.Many2one('estate.block', string='Block', readonly=True)
    total_cost = fields.Monetary(string='Total Cost', readonly=True)
    total_kg = fields.Float(string='Total KG', digits=(12, 2), readonly=True)
    cost_per_kg = fields.Float(string='Cost per KG', digits=(12, 4), readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_monthly_cost AS (
                SELECT
                    row_number() OVER () AS id,
                    aaa.date_year AS year,
                    aaa.date_month::TEXT AS month,
                    eb.id AS block_id,
                    COALESCE(SUM(aal.balance), 0) AS total_cost,
                    COALESCE(my.total_kg, 0) AS total_kg,
                    CASE WHEN my.total_kg > 0
                         THEN COALESCE(SUM(aal.balance), 0) / my.total_kg
                         ELSE 0 END AS cost_per_kg,
                    aaa.currency_id
                FROM account_analytic_account aaa
                JOIN account_analytic_line aal ON aal.account_id = aaa.id
                JOIN estate_block eb ON aaa.code = 'BLK-' || eb.code
                LEFT JOIN report_monthly_yield my ON my.block_id = eb.id
                    AND my.year = aaa.date_year
                    AND my.month::TEXT = aaa.date_month::TEXT
                GROUP BY aaa.date_year, aaa.date_month, eb.id, my.total_kg, aaa.currency_id
            )
        """)
