# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ReportDailyProduction(models.Model):
    """Daily production report per block/mandor/harvester."""
    _name = 'report.daily_production'
    _description = 'Daily Production Report'
    _auto = False  # SQL View
    _order = 'date desc, block_id'

    date = fields.Date(string='Date', readonly=True)
    block_id = fields.Many2one('estate.block', string='Block', readonly=True)
    afdeling_id = fields.Many2one('estate.afdeling', string='Afdeling', readonly=True)
    harvester_id = fields.Many2one('hr.employee', string='Harvester', readonly=True)
    janjang_count = fields.Integer(string='Janjang Count', readonly=True)
    brondolan_kg = fields.Float(string='Brondolan KG', digits=(12, 2), readonly=True)
    total_kg = fields.Float(string='Total KG', digits=(12, 2), readonly=True)
    bjr = fields.Float(string='BJR (KG/Janjang)', digits=(12, 2), readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_daily_production AS (
                SELECT
                    row_number() OVER () AS id,
                    hr.date AS date,
                    hr.block_id,
                    eb.afdeling_id,
                    hr.harvester_id,
                    hr.janjang_count,
                    hr.brondolan_kg,
                    COALESCE(wt.net_kg, hr.janjang_count * 0) AS total_kg,
                    CASE WHEN hr.janjang_count > 0
                         THEN COALESCE(wt.net_kg, 0) / hr.janjang_count
                         ELSE 0 END AS bjr
                FROM harvest_tph_record hr
                LEFT JOIN estate_block eb ON eb.id = hr.block_id
                LEFT JOIN transport_weighbridge_ticket wt ON wt.harvest_tph_id = hr.id
            )
        """)
