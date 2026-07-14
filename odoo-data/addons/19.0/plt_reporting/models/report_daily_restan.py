# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportDailyRestan(models.Model):
    """Daily restan (uncollected FFB) report."""
    _name = 'report.daily_restan'
    _description = 'Daily Restan Report'
    _auto = False
    _order = 'date desc, block_name'

    date = fields.Date(string='Date', readonly=True)
    block_name = fields.Char(string='Block', readonly=True)
    tph_code = fields.Char(string='TPH', readonly=True)
    janjang_count = fields.Integer(string='Janjang Count', readonly=True)
    estimated_kg = fields.Float(string='Estimated KG', digits=(12, 2), readonly=True)
    age_hours = fields.Float(string='Age (Hours)', digits=(12, 2), readonly=True)
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
                    tr.age_hours,
                    tr.escalated
                FROM transport_restan tr
                LEFT JOIN estate_tph et ON et.id = tr.tph_id
                LEFT JOIN estate_block eb ON eb.id = tr.block_id
            )
        """)
