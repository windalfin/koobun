# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportDailyProduction(models.Model):
    """Daily production report per block/mandor/harvester."""
    _name = 'report.daily_production'
    _description = 'Daily Production Report'
    _auto = False
    _order = 'date desc'

    date = fields.Date(string='Date', readonly=True)
    block_name = fields.Char(string='Block', readonly=True)
    harvester_name = fields.Char(string='Harvester', readonly=True)
    janjang_count = fields.Integer(string='Janjang Count', readonly=True)
    brondolan_kg = fields.Float(string='Brondolan KG', digits=(12, 2), readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_daily_production AS (
                SELECT
                    row_number() OVER () AS id,
                    hr.date,
                    eb.name AS block_name,
                    he.name AS harvester_name,
                    hr.janjang_count,
                    hr.brondolan_kg
                FROM harvest_tph_record hr
                LEFT JOIN estate_tph et ON et.id = hr.tph_id
                LEFT JOIN estate_block eb ON eb.id = et.block_id
                LEFT JOIN hr_employee he ON he.id = hr.harvester_id
            )
        """)


class ReportDailyRestan(models.Model):
    """Daily restan (uncollected FFB) report."""
    _name = 'report.daily_restan'
    _description = 'Daily Restan Report'
    _auto = False
    _order = 'date desc'

    date = fields.Date(string='Date', readonly=True)
    block_name = fields.Char(string='Block', readonly=True)
    tph_code = fields.Char(string='TPH', readonly=True)
    janjang_count = fields.Integer(string='Janjang Count', readonly=True)
    estimated_kg = fields.Float(string='Estimated KG', digits=(12, 2), readonly=True)
    escalated = fields.Boolean(string='Escalated', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_daily_restan AS (
                SELECT
                    row_number() OVER () AS id,
                    tr.date,
                    eb.name AS block_name,
                    et.code AS tph_code,
                    tr.janjang_count,
                    tr.estimated_kg,
                    tr.escalated
                FROM transport_restan tr
                LEFT JOIN estate_tph et ON et.id = tr.tph_id
                LEFT JOIN estate_block eb ON eb.id = tr.block_id
            )
        """)


class ReportMonthlyYield(models.Model):
    """Monthly yield per hectare per block."""
    _name = 'report.monthly_yield'
    _description = 'Monthly Yield Report'
    _auto = False
    _order = 'year desc, month'

    year = fields.Integer(string='Year', readonly=True)
    month = fields.Char(string='Month', readonly=True)
    block_name = fields.Char(string='Block', readonly=True)
    area_ha = fields.Float(string='Area (Ha)', digits=(12, 2), readonly=True)
    janjang_total = fields.Integer(string='Total Janjang', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_monthly_yield AS (
                SELECT
                    row_number() OVER () AS id,
                    EXTRACT(YEAR FROM hr.date)::INTEGER AS year,
                    EXTRACT(MONTH FROM hr.date)::TEXT AS month,
                    eb.name AS block_name,
                    eb.area_ha_planted AS area_ha,
                    COALESCE(SUM(hr.janjang_count), 0) AS janjang_total
                FROM harvest_tph_record hr
                JOIN estate_tph et ON et.id = hr.tph_id
                JOIN estate_block eb ON eb.id = et.block_id
                GROUP BY year, month, eb.name, eb.area_ha_planted
            )
        """)


class ReportMonthlyCost(models.Model):
    """Monthly cost per block."""
    _name = 'report.monthly_cost'
    _description = 'Monthly Cost Report'
    _auto = False
    _order = 'year desc, month'

    year = fields.Integer(string='Year', readonly=True)
    month = fields.Char(string='Month', readonly=True)
    block_name = fields.Char(string='Block', readonly=True)
    total_cost = fields.Float(string='Total Cost', digits=(12, 2), readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_monthly_cost AS (
                SELECT
                    row_number() OVER () AS id,
                    EXTRACT(YEAR FROM aal.date)::INTEGER AS year,
                    EXTRACT(MONTH FROM aal.date)::TEXT AS month,
                    eb.name AS block_name,
                    COALESCE(SUM(aal.amount), 0) AS total_cost
                FROM account_analytic_line aal
                JOIN account_analytic_account aaa ON aaa.id = aal.account_id
                JOIN estate_block eb ON aaa.code = 'BLK-' || eb.code
                GROUP BY year, month, eb.name
            )
        """)
