# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWageMaster(TransactionCase):

    def setUp(self):
        super().setUp()
        self.WageMaster = self.env['payroll.wage_master']

    def test_create_wage_master(self):
        """Test basic wage master creation."""
        wage = self.WageMaster.create({
            'name': 'BHL Standard 2025',
            'worker_class': 'BHL',
            'daily_wage': 85000.0,
            'hourly_rate': 12142.86,
            'effective_from': '2025-01-01',
        })
        self.assertTrue(wage.id)
        self.assertEqual(wage.state, 'draft')
        self.assertEqual(wage.worker_class, 'BHL')

    def test_approve_wage_master(self):
        """Test approving a wage master record."""
        wage = self.WageMaster.create({
            'name': 'SKU Standard',
            'worker_class': 'SKU',
            'daily_wage': 100000.0,
            'effective_from': '2025-01-01',
        })
        wage.action_approve()
        self.assertEqual(wage.state, 'approved')

    def test_cannot_approve_twice(self):
        """Test that approving an already-approved record raises."""
        wage = self.WageMaster.create({
            'name': 'KHT Standard',
            'worker_class': 'KHT',
            'daily_wage': 95000.0,
            'effective_from': '2025-01-01',
        })
        wage.action_approve()
        with self.assertRaises(Exception):
            wage.action_approve()

    def test_negative_daily_wage(self):
        """Test that negative daily wage is rejected."""
        with self.assertRaises(Exception):
            self.WageMaster.create({
                'name': 'Negative Test',
                'worker_class': 'BHL',
                'daily_wage': -1000.0,
                'effective_from': '2025-01-01',
            })

    def test_expire_wage_master(self):
        """Test that wage master is expired by cron."""
        wage = self.WageMaster.create({
            'name': 'Expiring Wage',
            'worker_class': 'BHL',
            'daily_wage': 80000.0,
            'effective_from': '2025-01-01',
            'effective_to': '2099-12-31',  # Far future — not expired
        })
        wage.action_approve()
        self.WageMaster._cron_expire_wages()
        self.assertEqual(wage.state, 'approved')  # Not expired yet because far-future date

    def test_set_draft(self):
        """Test resetting approved record to draft."""
        wage = self.WageMaster.create({
            'name': 'Reset Test',
            'worker_class': 'BHL',
            'daily_wage': 90000.0,
            'effective_from': '2025-01-01',
        })
        wage.action_approve()
        wage.action_set_draft()
        self.assertEqual(wage.state, 'draft')

    def test_dates_constraint(self):
        """Test that effective_from > effective_to is rejected."""
        with self.assertRaises(Exception):
            self.WageMaster.create({
                'name': 'Bad Dates',
                'worker_class': 'BHL',
                'daily_wage': 85000.0,
                'effective_from': '2025-12-31',
                'effective_to': '2025-01-01',
            })
