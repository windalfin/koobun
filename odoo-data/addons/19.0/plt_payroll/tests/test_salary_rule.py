# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestSalaryRule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.SalaryRule = self.env['payroll.salary_rule']

    def test_create_salary_rule(self):
        """Test creating a payroll salary rule."""
        rule = self.SalaryRule.create({
            'name': 'Daily Wage Rule',
            'code': 'DAILY_WAGE_PLT',
            'rule_type': 'daily_wage',
            'auto_compute': True,
        })
        self.assertTrue(rule.id)
        self.assertEqual(rule.rule_type, 'daily_wage')
        self.assertEqual(rule.source_model, 'plt_payroll')
        self.assertTrue(rule.auto_compute)

    def test_rule_type_source_model_mapping(self):
        """Test auto-mapping of source_model from rule_type."""
        # Premi should map to plt_harvest
        rule = self.SalaryRule.create({
            'name': 'Premi Rule',
            'code': 'PREMI_PLT',
            'rule_type': 'premi',
        })
        self.assertEqual(rule.source_model, 'plt_harvest')

        # Denda should map to plt_harvest
        rule2 = self.SalaryRule.create({
            'name': 'Denda Rule',
            'code': 'DENDA_PLT',
            'rule_type': 'denda',
        })
        self.assertEqual(rule2.source_model, 'plt_harvest')

    def test_override_source_model(self):
        """Test that explicit source_model overrides auto-mapping."""
        rule = self.SalaryRule.create({
            'name': 'Custom Rule',
            'code': 'CUSTOM',
            'rule_type': 'premi',
            'source_model': 'custom.module',
        })
        self.assertEqual(rule.source_model, 'custom.module')

    def test_rule_code_unique(self):
        """Test that rule code must be unique."""
        self.SalaryRule.create({
            'name': 'Rule 1',
            'code': 'UNIQUE_CODE',
            'rule_type': 'bpjs',
        })
        with self.assertRaises(Exception):
            self.SalaryRule.create({
                'name': 'Rule 2',
                'code': 'UNIQUE_CODE',
                'rule_type': 'pph21',
            })
