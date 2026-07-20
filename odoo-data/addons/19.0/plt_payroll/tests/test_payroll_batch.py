# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestPayrollBatch(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PayrollBatch = self.env['payroll.payroll_batch']

    def test_create_payroll_batch(self):
        """Test basic payroll batch creation."""
        batch = self.PayrollBatch.create({
            'period_start': '2025-06-01',
            'period_end': '2025-06-15',
        })
        self.assertTrue(batch.id)
        self.assertEqual(batch.state, 'draft')

    def test_state_flow(self):
        """Test the full state flow."""
        batch = self.PayrollBatch.create({
            'period_start': '2025-06-01',
            'period_end': '2025-06-15',
        })
        batch.action_calculate()
        self.assertEqual(batch.state, 'calculated')
        batch.action_verify()
        self.assertEqual(batch.state, 'verified')
        batch.action_approve()
        self.assertEqual(batch.state, 'approved')
        batch.action_post()
        self.assertEqual(batch.state, 'posted')

    def test_cannot_calculate_non_draft(self):
        """Test that only draft can be calculated."""
        batch = self.PayrollBatch.create({
            'period_start': '2025-06-01',
            'period_end': '2025-06-15',
        })
        batch.action_calculate()
        with self.assertRaises(Exception):
            batch.action_calculate()

    def test_cannot_verify_non_calculated(self):
        """Test that only calculated can be verified."""
        batch = self.PayrollBatch.create({
            'period_start': '2025-06-01',
            'period_end': '2025-06-15',
        })
        with self.assertRaises(Exception):
            batch.action_verify()

    def test_cannot_approve_non_verified(self):
        """Test that only verified can be approved."""
        batch = self.PayrollBatch.create({
            'period_start': '2025-06-01',
            'period_end': '2025-06-15',
        })
        with self.assertRaises(Exception):
            batch.action_approve()

    def test_cannot_post_non_approved(self):
        """Test that only approved can be posted."""
        batch = self.PayrollBatch.create({
            'period_start': '2025-06-01',
            'period_end': '2025-06-15',
        })
        with self.assertRaises(Exception):
            batch.action_post()

    def test_cannot_set_draft_posted(self):
        """Test that posted batch cannot be reset."""
        batch = self.PayrollBatch.create({
            'period_start': '2025-06-01',
            'period_end': '2025-06-15',
        })
        batch.action_calculate()
        batch.action_verify()
        batch.action_approve()
        batch.action_post()
        with self.assertRaises(Exception):
            batch.action_set_draft()

    def test_period_constraint(self):
        """Test period start/end constraint."""
        with self.assertRaises(Exception):
            self.PayrollBatch.create({
                'period_start': '2025-06-15',
                'period_end': '2025-06-01',
            })
