# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestDisbunPrice(TransactionCase):

    def setUp(self):
        super().setUp()
        self.DisbunPrice = self.env['plasma.disbun_price']

    def test_01_create_disbun_price(self):
        """Test creating a Disbun price entry."""
        rec = self.DisbunPrice.create({
            'name': 'Harga Disbun 2025',
            'effective_from': '2025-01-01',
            'age_band_min': 0,
            'age_band_max': 5,
            'price_per_kg': 2800.0,
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.age_band_min, 0)
        self.assertEqual(rec.age_band_max, 5)
        self.assertEqual(rec.price_per_kg, 2800.0)
        self.assertEqual(rec.state, 'draft')

    def test_02_all_age_bands(self):
        """Test creating typical Disbun age bands."""
        bands = [
            (0, 3, 2700.0),
            (4, 6, 2800.0),
            (7, 9, 2900.0),
            (10, 14, 3000.0),
            (15, 25, 3100.0),
        ]
        for lo, hi, price in bands:
            rec = self.DisbunPrice.create({
                'name': f'Band {lo}-{hi}',
                'effective_from': '2025-01-01',
                'age_band_min': lo,
                'age_band_max': hi,
                'price_per_kg': price,
            })
            self.assertEqual(rec.price_per_kg, price)

    def test_03_negative_price(self):
        """Test negative price is rejected."""
        with self.assertRaises(Exception):
            self.DisbunPrice.create({
                'name': 'Bad',
                'effective_from': '2025-01-01',
                'age_band_min': 0,
                'age_band_max': 5,
                'price_per_kg': -100.0,
            })

    def test_04_date_constraint(self):
        """Test effective_to < effective_from is rejected."""
        with self.assertRaises(Exception):
            self.DisbunPrice.create({
                'name': 'Bad Date',
                'effective_from': '2025-12-31',
                'effective_to': '2025-01-01',
                'age_band_min': 0,
                'age_band_max': 5,
                'price_per_kg': 2800.0,
            })

    def test_05_age_band_constraint(self):
        """Test age_band_max < age_band_min is rejected."""
        with self.assertRaises(Exception):
            self.DisbunPrice.create({
                'name': 'Bad Band',
                'effective_from': '2025-01-01',
                'age_band_min': 10,
                'age_band_max': 5,
                'price_per_kg': 2800.0,
            })

    def test_06_approve_workflow(self):
        """Test approve and set-draft workflow."""
        rec = self.DisbunPrice.create({
            'name': 'THR Band',
            'effective_from': '2025-01-01',
            'age_band_min': 0,
            'age_band_max': 5,
            'price_per_kg': 2800.0,
        })
        rec.action_approve()
        self.assertEqual(rec.state, 'approved')
        rec.action_set_draft()
        self.assertEqual(rec.state, 'draft')

    def test_07_get_price_for_age(self):
        """Test get_price_for_age lookup."""
        rec = self.DisbunPrice.create({
            'name': 'Band 4-6',
            'effective_from': '2025-01-01',
            'age_band_min': 4,
            'age_band_max': 6,
            'price_per_kg': 2800.0,
        })
        rec.action_approve()
        price = self.DisbunPrice.get_price_for_age(
            age=5, date='2025-06-01',
        )
        self.assertEqual(price, 2800.0)

    def test_08_get_price_no_match(self):
        """Test get_price_for_age returns 0 when no match."""
        rec = self.DisbunPrice.create({
            'name': 'Band 10-14',
            'effective_from': '2025-01-01',
            'age_band_min': 10,
            'age_band_max': 14,
            'price_per_kg': 3000.0,
        })
        rec.action_approve()
        price = self.DisbunPrice.get_price_for_age(
            age=3, date='2025-06-01',
        )
        self.assertEqual(price, 0.0)

    def test_09_name_compute(self):
        """Test name auto-computed from age band."""
        rec = self.DisbunPrice.create({
            'effective_from': '2025-01-01',
            'age_band_min': 4,
            'age_band_max': 6,
            'price_per_kg': 2800.0,
        })
        self.assertIn('4', rec.name)
        self.assertIn('6', rec.name)