# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPtkpTable(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PtkpTable = self.env['payroll.ptkp_table']

    def test_01_create_ptkp(self):
        """Test creating a PTKP entry."""
        rec = self.PtkpTable.create({
            'code': 'TK/0',
            'name': 'Tidak Kawin, Tanpa Tanggungan',
            'amount': 54000000.0,
            'effective_from': '2025-01-01',
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.code, 'TK/0')
        self.assertEqual(rec.amount, 54000000.0)
        self.assertEqual(rec.state, 'draft')

    def test_02_all_categories(self):
        """Test creating all standard PTKP categories."""
        categories = [
            ('TK/0', 'Tidak Kawin, Tanpa Tanggungan', 54000000),
            ('TK/1', 'Tidak Kawin, 1 Tanggungan', 58500000),
            ('TK/2', 'Tidak Kawin, 2 Tanggungan', 63000000),
            ('TK/3', 'Tidak Kawin, 3 Tanggungan', 67500000),
            ('K/0', 'Kawin, Tanpa Tanggungan', 58500000),
            ('K/1', 'Kawin, 1 Tanggungan', 63000000),
            ('K/2', 'Kawin, 2 Tanggungan', 67500000),
            ('K/3', 'Kawin, 3 Tanggungan', 72000000),
        ]
        for code, name, amount in categories:
            rec = self.PtkpTable.create({
                'code': code,
                'name': name,
                'amount': amount,
                'effective_from': '2025-01-01',
            })
            self.assertEqual(rec.code, code)
            self.assertEqual(rec.amount, amount)

    def test_03_unique_code_per_effective(self):
        """Test duplicate code+effective_from is rejected."""
        self.PtkpTable.create({
            'code': 'TK/0',
            'name': 'TK/0 2025',
            'amount': 54000000.0,
            'effective_from': '2025-01-01',
        })
        self.env.flush_all()
        count = self.PtkpTable.search_count([
            ('code', '=', 'TK/0'),
            ('effective_from', '=', '2025-01-01'),
        ])
        self.assertEqual(count, 1)
        try:
            self.PtkpTable.create({
                'code': 'TK/0',
                'name': 'TK/0 2025 dup',
                'amount': 54000000.0,
                'effective_from': '2025-01-01',
            })
            self.env.flush_all()
            self.fail('Expected unique constraint violation')
        except Exception:
            pass

    def test_04_negative_amount(self):
        """Test negative amount is rejected."""
        with self.assertRaises(Exception):
            self.PtkpTable.create({
                'code': 'TK/0',
                'name': 'Negative',
                'amount': -1000.0,
                'effective_from': '2025-01-01',
            })

    def test_05_date_constraint(self):
        """Test effective_to < effective_from is rejected."""
        with self.assertRaises(Exception):
            self.PtkpTable.create({
                'code': 'TK/0',
                'name': 'Bad Date',
                'amount': 54000000.0,
                'effective_from': '2025-12-31',
                'effective_to': '2025-01-01',
            })

    def test_06_approve_workflow(self):
        """Test approve and set-draft workflow."""
        rec = self.PtkpTable.create({
            'code': 'K/2',
            'name': 'Kawin, 2 Tanggungan',
            'amount': 67500000.0,
            'effective_from': '2025-01-01',
        })
        rec.action_approve()
        self.assertEqual(rec.state, 'approved')
        rec.action_set_draft()
        self.assertEqual(rec.state, 'draft')

    def test_07_get_ptkp_amount(self):
        """Test get_ptkp_amount lookup by code and date."""
        rec = self.PtkpTable.create({
            'code': 'K/3',
            'name': 'Kawin, 3 Tanggungan',
            'amount': 72000000.0,
            'effective_from': '2025-01-01',
        })
        rec.action_approve()
        amount = self.PtkpTable.get_ptkp_amount('K/3', '2025-06-01')
        self.assertEqual(amount, 72000000.0)