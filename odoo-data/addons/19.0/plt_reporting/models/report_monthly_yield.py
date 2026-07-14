# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportMonthlyYield(models.Model):
    """Monthly yield per hectare per block vs RKAP."""
    _name = 'report.monthly_yield'
    _description = 'Monthly Yield Report'
    _auto = False
    _order = 'year desc, month, block_id'

    year = fields.Integer(string='Year', readonly=True)
    month = fields.Selection([
        ('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'),
        ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Aug'),
        ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec'),
    ], string='Month', readonly=True)
    block_id = fields.Many2one('estate.block', string='Block', readonly=True)
    afdeling_id = fields.Many2one('estate.afdeling', string='Afdeling', readonly=True)
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
                    hr.block_id,
                    eb.afdeling_id,
                    eb.area_ha_planted AS area_ha,
                    COALESCE(SUM(wt.net_kg), 0) AS total_kg,
                    CASE WHEN eb.area_ha_planted > 0
                         THEN COALESCE(SUM(wt.net_kg), 0) / eb.area_ha_planted
                         ELSE 0 END AS yield_kg_per_ha
                FROM harvest_tph_record hr
                JOIN estate_block eb ON eb.id = hr.block_id
                LEFT JOIN transport_weighbridge_ticket wt ON wt.harvest_tph_id = hr.id
                GROUP BY year, month, hr.block_id, eb.afdeling_id, eb.area_ha_planted
            )
        """)
