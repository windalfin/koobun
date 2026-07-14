# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportMonthlyYield(models.Model):
    """Monthly yield per hectare per block vs RKAP."""
    _name = 'report.monthly_yield'
    _description = 'Monthly Yield Report'
    _auto = False
    _order = 'year desc, month, block_name'

    year = fields.Integer(string='Year', readonly=True)
    month = fields.Char(string='Month', readonly=True)
    block_name = fields.Char(string='Block', readonly=True)
    area_ha = fields.Float(string='Area (Ha)', digits=(12, 2), readonly=True)
    total_kg = fields.Float(string='Total KG', digits=(12, 2), readonly=True)
    yield_kg_per_ha = fields.Float(string='Yield (KG/Ha)', digits=(12, 2), readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_monthly_yield AS (
                SELECT
                    row_number() OVER () AS id,
                    EXTRACT(YEAR FROM hr.date)::INTEGER AS year,
                    EXTRACT(MONTH FROM hr.date)::TEXT AS month,
                    eb.name AS block_name,
                    eb.area_ha_planted AS area_ha,
                    COALESCE(SUM(COALESCE(wt.net_kg, 0)), 0) AS total_kg,
                    CASE WHEN eb.area_ha_planted > 0
                         THEN COALESCE(SUM(COALESCE(wt.net_kg, 0)), 0) / eb.area_ha_planted
                         ELSE 0 END AS yield_kg_per_ha
                FROM harvest_tph_record hr
                JOIN estate_tph et ON et.id = hr.tph_id
                JOIN estate_block eb ON eb.id = et.block_id
                LEFT JOIN transport_weighbridge_ticket wt ON wt.spb_id IS NOT NULL
                GROUP BY year, month, eb.name, eb.area_ha_planted
            )
        """)
