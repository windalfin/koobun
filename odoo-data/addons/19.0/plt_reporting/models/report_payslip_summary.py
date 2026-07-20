# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportPayslipSummary(models.Model):
    """Monthly payroll summary — per employee per year/month."""
    _name = 'report.payslip_summary'
    _description = 'Ringkasan Penggajian Bulanan'
    _auto = False
    _order = 'year desc, month'

    year = fields.Integer(string='Tahun', readonly=True)
    month = fields.Char(string='Bulan', readonly=True)
    employee_name = fields.Char(string='Pekerja', readonly=True)
    total_hk = fields.Integer(string='Total HK', readonly=True)
    gross_pay = fields.Float(string='Gaji Kotor', digits=(16, 2), readonly=True)
    total_deductions = fields.Float(
        string='Total Potongan', digits=(16, 2), readonly=True)
    net_pay = fields.Float(
        string='Gaji Bersih', digits=(16, 2), readonly=True)

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS report_payslip_summary;
            CREATE OR REPLACE VIEW report_payslip_summary AS (
                SELECT
                    row_number() OVER () AS id,
                    EXTRACT(YEAR FROM pb.period_start)::INTEGER AS year,
                    EXTRACT(MONTH FROM pb.period_start)::TEXT    AS month,
                    he.name                                       AS employee_name,
                    COALESCE(SUM(pl.hk_count), 0)               AS total_hk,
                    COALESCE(SUM(pl.daily_base * pl.hk_count
                        + pl.premi_amount), 0)                   AS gross_pay,
                    COALESCE(SUM(pl.denda_amount
                        + pl.pph21_amount
                        + pl.tht_amount), 0)                     AS total_deductions,
                    COALESCE(SUM(pl.net_pay), 0)                 AS net_pay
                FROM payroll_payslip_line pl
                JOIN payroll_payroll_batch pb ON pb.id = pl.payroll_batch_id
                JOIN hr_employee he            ON he.id = pl.employee_id
                GROUP BY
                    EXTRACT(YEAR FROM pb.period_start),
                    EXTRACT(MONTH FROM pb.period_start),
                    he.name
            )
        """)