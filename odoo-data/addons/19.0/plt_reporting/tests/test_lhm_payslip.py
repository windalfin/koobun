# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestReportLHM(TransactionCase):
    """Test Laporan Harian Mandor (report.lhm) SQL view model."""

    def test_01_lhm_model_exists(self):
        """Verify that report.lhm model is registered in env."""
        model = self.env.get('report.lhm')
        self.assertIsNotNone(model, 'Model report.lhm not found')


class TestReportPayslipSummary(TransactionCase):
    """Test monthly payroll summary (report.payslip_summary) SQL view model."""

    def test_01_payslip_summary_exists(self):
        """Verify that report.payslip_summary model is registered in env."""
        model = self.env.get('report.payslip_summary')
        self.assertIsNotNone(model, 'Model report.payslip_summary not found')