# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestBpjsConfig(TransactionCase):

    def setUp(self):
        super().setUp()
        self.BpjsConfig = self.env['payroll.bpjs_config']

    def test_create_bpjs_config(self):
        """Test basic BPJS config creation."""
        config = self.BpjsConfig.create({
            'name': 'BPJS Kesehatan 2025',
            'bpjs_type': 'kesehatan',
            'employer_pct': 4.0,
            'employee_pct': 1.0,
            'ceiling_amount': 12000000.0,
            'effective_from': '2025-01-01',
        })
        self.assertTrue(config.id)
        self.assertEqual(config.state, 'draft')

    def test_approve_bpjs_config(self):
        """Test approving a BPJS config record."""
        config = self.BpjsConfig.create({
            'name': 'JHT 2025',
            'bpjs_type': 'JHT',
            'employer_pct': 3.7,
            'employee_pct': 2.0,
            'effective_from': '2025-01-01',
        })
        config.action_approve()
        self.assertEqual(config.state, 'approved')

    def test_cannot_approve_twice(self):
        """Test double-approve raises."""
        config = self.BpjsConfig.create({
            'name': 'JP 2025',
            'bpjs_type': 'JP',
            'employer_pct': 2.0,
            'employee_pct': 1.0,
            'effective_from': '2025-01-01',
        })
        config.action_approve()
        with self.assertRaises(Exception):
            config.action_approve()

    def test_negative_rates(self):
        """Test negative rates are rejected."""
        with self.assertRaises(Exception):
            self.BpjsConfig.create({
                'name': 'Negative Rate',
                'bpjs_type': 'JKK',
                'employer_pct': -1.0,
                'employee_pct': 1.0,
                'effective_from': '2025-01-01',
            })

    def test_compute_contribution(self):
        """Test BPJS contribution calculation."""
        config = self.BpjsConfig.create({
            'name': 'BPJS Kesehatan',
            'bpjs_type': 'kesehatan',
            'employer_pct': 4.0,
            'employee_pct': 1.0,
            'ceiling_amount': 12000000.0,
            'effective_from': '2025-01-01',
        })
        # Below ceiling
        employer, employee = config.compute_contribution(5000000.0)
        self.assertAlmostEqual(employer, 200000.0)
        self.assertAlmostEqual(employee, 50000.0)
        # Above ceiling
        employer, employee = config.compute_contribution(15000000.0)
        self.assertAlmostEqual(employer, 480000.0)
        self.assertAlmostEqual(employee, 120000.0)

    def test_set_draft(self):
        """Test resetting to draft."""
        config = self.BpjsConfig.create({
            'name': 'Reset Test',
            'bpjs_type': 'JKM',
            'employer_pct': 0.3,
            'employee_pct': 0.0,
            'effective_from': '2025-01-01',
        })
        config.action_approve()
        config.action_set_draft()
        self.assertEqual(config.state, 'draft')

    def test_dates_constraint(self):
        """Test invalid date range."""
        with self.assertRaises(Exception):
            self.BpjsConfig.create({
                'name': 'Bad Dates',
                'bpjs_type': 'kesehatan',
                'employer_pct': 4.0,
                'employee_pct': 1.0,
                'effective_from': '2025-12-31',
                'effective_to': '2025-01-01',
            })
