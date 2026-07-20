# -*- coding: utf-8 -*-
import datetime
from odoo.tests.common import TransactionCase


class TestSiperibunReport(TransactionCase):
    """Test 6-monthly SIPERIBUN report (plasma.siperibun_report)."""

    def setUp(self):
        super().setUp()
        self.Siperibun = self.env['plasma.siperibun_report']

    def test_01_create_draft(self):
        """Create a neutral Siperibun pack — default state is draft."""
        rec = self.Siperibun.create({
            'period_start': datetime.date(2024, 1, 1),
            'period_end': datetime.date(2024, 6, 30),
            'total_farmers': 10,
            'total_delivery_kg': 1500.0,
            'total_payment': 2500,
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.state, 'draft')
        self.assertEqual(rec.total_farmers, 10)
        self.assertEqual(rec.total_delivery_kg, 1500.0)

    def test_02_action_submit(self):
        """Submit action moves state from draft → submitted."""
        rec = self.Siperibun.create({
            'period_start': datetime.date(2024, 7, 1),
            'period_end': datetime.date(2024, 12, 31),
            'total_farmers': 5,
            'total_delivery_kg': 800.0,
            'total_payment': 1200,
        })
        rec.action_submit()
        self.assertEqual(rec.state, 'submitted')

    def test_03_cannot_resubmit(self):
        """Submitting again must raise UserError."""
        from odoo.exceptions import UserError
        rec = self.Siperibun.create({
            'period_start': datetime.date(2024, 1, 1),
            'period_end': datetime.date(2024, 6, 30),
            'total_farmers': 1,
        })
        rec.action_submit()
        with self.assertRaises(UserError):
            rec.action_submit()

    def test_04_action_draft_reset(self):
        """action_set_draft moves submitted back to draft."""
        rec = self.Siperibun.create({
            'period_start': datetime.date(2024, 7, 1),
            'period_end': datetime.date(2024, 12, 31),
        })
        rec.action_submit()
        rec.action_set_draft()
        self.assertEqual(rec.state, 'draft')