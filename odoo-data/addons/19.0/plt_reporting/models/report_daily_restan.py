# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportDailyRestan(models.Model):
    """Daily restan (uncollected FFB) report."""
    _name = 'report.daily_restan'
    _description = 'Daily Restan Report'
    _auto = False
    _order = 'date desc, block_id'

    date = fields.Date(string='Date', readonly=True)
    block_id = fields.Many2one('estate.block', string='Block', readonly=True)
    tph_id = fields.Many2one('estate.tph', string='TPH', readonly=True)
    janjang_count = fields.Integer(string='Janjang Count', readonly=True)
    estimated_kg = fields.Float(string='Estimated KG', digits=(12, 2), readonly=True)
    age_hours = fields.Float(string='Age (Hours)', digits=(12, 2), readonly=True)
    escalated = fields.Boolean(string='Escalated', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_daily_restan AS (
                SELECT
                    row_number() OVER () AS id,
                    r.date,
                    r.block_id,
                    r.tph_id,
                    r.janjang_count,
                    r.estimated_kg,
                    r.age_hours,
                    r.escalated
                FROM transport_restan r
            )
        """)
