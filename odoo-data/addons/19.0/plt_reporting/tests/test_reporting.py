# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestReporting(TransactionCase):

    def test_01_report_models_exist(self):
        """Verify all report models are registered."""
        models = [
            'report.daily_production',
            'report.monthly_yield',
            'report.daily_restan',
            'report.monthly_cost',
        ]
        for model_name in models:
            model = self.env.get(model_name)
            self.assertIsNotNone(model, f'Model {model_name} not found')
