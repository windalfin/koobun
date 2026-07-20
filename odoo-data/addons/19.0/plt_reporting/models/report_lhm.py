# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportLHM(models.Model):
    """Laporan Harian Mandor — daily summary per mandor.

    Aggregates upkeep (BKM) and harvest (TPH record) per mandor/block/date
    so the mandor has a single daily summary row.
    """
    _name = 'report.lhm'
    _description = 'Laporan Harian Mandor (LHM)'
    _auto = False
    _order = 'date desc'

    date = fields.Date(string='Tanggal', readonly=True)
    mandor_name = fields.Char(string='Mandor', readonly=True)
    block_name = fields.Char(string='Blok', readonly=True)
    activity = fields.Char(string='Aktivitas', readonly=True)
    worker_count = fields.Integer(string='Jumlah Pekerja', readonly=True)
    total_kg = fields.Float(string='Total (kg)', digits=(12, 2), readonly=True)

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS report_lhm;
            CREATE OR REPLACE VIEW report_lhm AS (
                SELECT
                    row_number() OVER () AS id,
                    b.date,
                    COALESCE(he.name, '') AS mandor_name,
                    COALESCE(eb.name, '') AS block_name,
                    COALESCE(ac.name->>'en_US', ac.name::text, '') AS activity,
                    COALESCE(b.worker_count, 0) AS worker_count,
                    COALESCE(SUM(COALESCE(hr.brondolan_kg, 0)), 0) AS total_kg
                FROM upkeep_bkm b
                LEFT JOIN hr_employee he ON he.id = b.mandor_id
                LEFT JOIN estate_block eb ON eb.id = b.block_id
                LEFT JOIN upkeep_activity_code ac ON ac.id = b.activity_code_id
                LEFT JOIN harvest_tph_record hr
                    ON hr.date = b.date
                    AND hr.harvester_id = b.mandor_id
                GROUP BY
                    b.date, he.name, eb.name, ac.name, b.worker_count
            )
        """)
