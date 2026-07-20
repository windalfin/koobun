# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestBudgetActual(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BudgetActual = cls.env['plan.budget_actual']
        cls.Block = cls.env['estate.block']
        cls.Estate = cls.env['estate.estate']
        cls.Afdeling = cls.env['estate.afdeling']
        cls.Activity = cls.env['upkeep.activity_code']

        cls.estate = cls.Estate.create({'name': 'Test Estate', 'code': 'TE'})
        cls.afdeling = cls.Afdeling.create({
            'name': 'Afd A', 'code': 'A', 'estate_id': cls.estate.id,
        })
        cls.block = cls.Block.create({
            'name': 'Block B1', 'code': 'B1', 'afdeling_id': cls.afdeling.id,
        })
        cls.activity = cls.Activity.create({
            'name': 'Pemupukan', 'code': 'PM-BA', 'category': 'pemupukan',
        })

    def test_01_create_budget_actual(self):
        """Test creating a budget vs actual entry."""
        rec = self.BudgetActual.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '1',
            'budgeted_cost': 5000000.0,
            'actual_cost': 4800000.0,
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.year, 2025)
        self.assertEqual(rec.budgeted_cost, 5000000.0)
        self.assertEqual(rec.actual_cost, 4800000.0)

    def test_02_variance_compute(self):
        """Test computed variance = budgeted - actual."""
        rec = self.BudgetActual.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '2',
            'budgeted_cost': 5000000.0,
            'actual_cost': 4800000.0,
        })
        # budgeted - actual = 200000 (under budget)
        self.assertAlmostEqual(rec.variance, 200000.0)

    def test_03_variance_negative(self):
        """Test variance is negative when actual > budget."""
        rec = self.BudgetActual.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '3',
            'budgeted_cost': 3000000.0,
            'actual_cost': 3500000.0,
        })
        self.assertAlmostEqual(rec.variance, -500000.0)

    def test_04_variance_pct_compute(self):
        """Test computed variance_pct."""
        rec = self.BudgetActual.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '4',
            'budgeted_cost': 10000000.0,
            'actual_cost': 7500000.0,
        })
        # (budgeted - actual) / budgeted * 100 = 25%
        self.assertAlmostEqual(rec.variance_pct, 25.0)

    def test_05_no_budget(self):
        """Test variance with zero budget does not crash."""
        rec = self.BudgetActual.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '5',
            'budgeted_cost': 0.0,
            'actual_cost': 1000000.0,
        })
        self.assertAlmostEqual(rec.variance, -1000000.0)
        self.assertAlmostEqual(rec.variance_pct, 0.0)

    def test_06_name_compute(self):
        """Test name is auto-computed."""
        rec = self.BudgetActual.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '6',
            'budgeted_cost': 1000000.0,
        })
        self.assertIn('2025', rec.name)
        self.assertIn('B1', rec.name)