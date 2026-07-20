# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestPph21Config(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Pph21Config = self.env['payroll.pph21_config']

    def test_create_pph21_config(self):
        """Test basic PPh 21 config creation."""
        config = self.Pph21Config.create({
            'ptkp_category': 'TK/0',
            'ter_category': 'TER A',
            'rate_pct': 5.0,
            'effective_from': '2025-01-01',
        })
        self.assertTrue(config.id)
        self.assertEqual(config.ptkp_category, 'TK/0')
        self.assertEqual(config.ter_category, 'TER A')
        self.assertEqual(config.rate_pct, 5.0)

    def test_rate_bounds(self):
        """Test rate is between 0 and 100."""
        with self.assertRaises(Exception):
            self.Pph21Config.create({
                'ptkp_category': 'TK/0',
                'ter_category': 'TER A',
                'rate_pct': 150.0,
                'effective_from': '2025-01-01',
            })
        with self.assertRaises(Exception):
            self.Pph21Config.create({
                'ptkp_category': 'TK/0',
                'ter_category': 'TER A',
                'rate_pct': -5.0,
                'effective_from': '2025-01-01',
            })

    def test_dates_constraint(self):
        """Test invalid date range."""
        with self.assertRaises(Exception):
            self.Pph21Config.create({
                'ptkp_category': 'K/0',
                'ter_category': 'TER B',
                'rate_pct': 10.0,
                'effective_from': '2025-12-31',
                'effective_to': '2025-01-01',
            })

    def test_required_fields(self):
        """Test required fields."""
        with self.assertRaises(Exception):
            self.Pph21Config.create({
                'rate_pct': 10.0,
                'effective_from': '2025-01-01',
            })
