# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestK3APD(TransactionCase):
    """Test APD/PPE issue records (compliance.k3_apd)."""

    def setUp(self):
        super().setUp()
        self.APD = self.env['compliance.k3_apd']
        self.Employee = self.env['hr.employee']
        self.emp = self.Employee.create({'name': 'Pekerji APD 1'})

    def test_01_create_apd_issue(self):
        """Creating an APD issue record with required fields."""
        rec = self.APD.create({
            'employee_id': self.emp.id,
            'apd_type': 'helmet',
            'quantity_issued': 1,
            'condition': 'new',
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.apd_type, 'helmet')
        self.assertEqual(rec.quantity_issued, 1)
        self.assertEqual(rec.condition, 'new')

    def test_02_default_condition_good(self):
        """Default condition should be 'good'."""
        rec = self.APD.create({
            'employee_id': self.emp.id,
            'apd_type': 'boots',
            'quantity_issued': 2,
        })
        self.assertEqual(rec.condition, 'good')

    def test_03_notes_optional(self):
        """Notes field is optional and persists."""
        rec = self.APD.create({
            'employee_id': self.emp.id,
            'apd_type': 'gloves',
            'quantity_issued': 5,
            'condition': 'damaged',
            'notes': 'Penyerahan sarung tangan rusak',
        })
        self.assertEqual(rec.notes, 'Penyerahan sarung tangan rusak')
        self.assertEqual(rec.condition, 'damaged')