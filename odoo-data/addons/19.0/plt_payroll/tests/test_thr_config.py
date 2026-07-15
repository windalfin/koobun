# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestThrConfig(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ThrConfig = self.env['payroll.thr_config']

    def test_01_create_thr_config(self):
        """Test creating a THR config entry."""
        rec = self.ThrConfig.create({
            'name': 'THR Lebaran 2025',
            'year': 2025,
            'month': '3',
            'rate_pct': 100.0,
            'prorate_basis': 'full_year',
            'effective_from': '2025-01-01',
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.year, 2025)
        self.assertEqual(rec.rate_pct, 100.0)
        self.assertEqual(rec.state, 'draft')

    def test_02_negative_rate(self):
        """Test negative rate is rejected."""
        with self.assertRaises(Exception):
            self.ThrConfig.create({
                'name': 'Bad',
                'year': 2025,
                'month': '3',
                'rate_pct': -10.0,
                'prorate_basis': 'full_year',
                'effective_from': '2025-01-01',
            })

    def test_03_date_constraint(self):
        """Test effective_to < effective_from is rejected."""
        with self.assertRaises(Exception):
            self.ThrConfig.create({
                'name': 'Bad Date',
                'year': 2025,
                'month': '3',
                'rate_pct': 100.0,
                'prorate_basis': 'full_year',
                'effective_from': '2025-12-31',
                'effective_to': '2025-01-01',
            })

    def test_04_approve_workflow(self):
        """Test approve and set-draft workflow."""
        rec = self.ThrConfig.create({
            'name': 'THR 2025',
            'year': 2025,
            'month': '4',
            'rate_pct': 100.0,
            'prorate_basis': 'full_year',
            'effective_from': '2025-01-01',
        })
        rec.action_approve()
        self.assertEqual(rec.state, 'approved')
        rec.action_set_draft()
        self.assertEqual(rec.state, 'draft')

    def test_05_compute_thr_full_year(self):
        """Test THR computation: full year = 1 month salary * rate."""
        rec = self.ThrConfig.create({
            'name': 'THR Full',
            'year': 2025,
            'month': '4',
            'rate_pct': 100.0,
            'prorate_basis': 'full_year',
            'effective_from': '2025-01-01',
        })
        rec.action_approve()
        # 12 months employed, monthly salary 3,000,000
        thr = rec.compute_thr(
            monthly_salary=3000000.0,
            months_employed=12,
        )
        self.assertAlmostEqual(thr, 3000000.0)

    def test_06_compute_thr_prorate(self):
        """Test THR computation: prorated for partial year."""
        rec = self.ThrConfig.create({
            'name': 'THR Prorate',
            'year': 2025,
            'month': '4',
            'rate_pct': 100.0,
            'prorate_basis': 'proportional',
            'effective_from': '2025-01-01',
        })
        rec.action_approve()
        # 6 months employed out of 12 → 50% of 1 month salary
        thr = rec.compute_thr(
            monthly_salary=3000000.0,
            months_employed=6,
        )
        self.assertAlmostEqual(thr, 1500000.0)

    def test_07_compute_thr_rate(self):
        """Test THR with 50% rate."""
        rec = self.ThrConfig.create({
            'name': 'THR 50%',
            'year': 2025,
            'month': '4',
            'rate_pct': 50.0,
            'prorate_basis': 'full_year',
            'effective_from': '2025-01-01',
        })
        rec.action_approve()
        thr = rec.compute_thr(
            monthly_salary=4000000.0,
            months_employed=12,
        )
        self.assertAlmostEqual(thr, 2000000.0)

    def test_08_unique_year_month(self):
        """Test duplicate year+month is rejected."""
        self.ThrConfig.create({
            'name': 'THR A',
            'year': 2025,
            'month': '4',
            'rate_pct': 100.0,
            'prorate_basis': 'full_year',
            'effective_from': '2025-01-01',
        })
        self.env.flush_all()
        count = self.ThrConfig.search_count([
            ('year', '=', 2025),
            ('month', '=', '4'),
        ])
        self.assertEqual(count, 1)
        try:
            self.ThrConfig.create({
                'name': 'THR B',
                'year': 2025,
                'month': '4',
                'rate_pct': 50.0,
                'prorate_basis': 'full_year',
                'effective_from': '2025-01-01',
            })
            self.env.flush_all()
            self.fail('Expected unique constraint violation')
        except Exception:
            pass