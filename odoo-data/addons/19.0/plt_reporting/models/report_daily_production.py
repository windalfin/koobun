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
            DROP VIEW IF EXISTS report_daily_production;
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
