# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestHarvestPremiStatement(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PremiStatement = self.env['harvest.premi_statement']

    def _get_or_skip_employee(self):
        employee = self.env['hr.employee'].search([], limit=1)
        if not employee:
            self.skipTest('No hr.employee found')
        return employee

    def test_create_premi_statement(self):
        """Test basic premi statement creation."""
        employee = self._get_or_skip_employee()
        stmt = self.PremiStatement.create({
            'date': '2025-01-15',
            'harvester_id': employee.id,
            'premi_amount': 150000.0,
            'denda_amount': 25000.0,
        })
        self.assertTrue(stmt.id)
        self.assertEqual(stmt.state, 'draft')
        self.assertEqual(stmt.premi_amount, 150000.0)
        self.assertEqual(stmt.denda_amount, 25000.0)

    def test_net_premi_computed(self):
        """Test that net_premi = premi_amount - denda_amount."""
        employee = self._get_or_skip_employee()
        stmt = self.PremiStatement.create({
            'date': '2025-01-15',
            'harvester_id': employee.id,
            'premi_amount': 200000.0,
            'denda_amount': 50000.0,
        })
        self.assertEqual(stmt.net_premi, 150000.0)

    def test_net_premi_no_denda(self):
        """Test net_premi when no denda."""
        employee = self._get_or_skip_employee()
        stmt = self.PremiStatement.create({
            'date': '2025-01-15',
            'harvester_id': employee.id,
            'premi_amount': 100000.0,
            'denda_amount': 0.0,
        })
        self.assertEqual(stmt.net_premi, 100000.0)

    def test_premi_statement_workflow(self):
        """Test draft → posted workflow."""
        employee = self._get_or_skip_employee()
        stmt = self.PremiStatement.create({
            'date': '2025-01-15',
            'harvester_id': employee.id,
            'premi_amount': 175000.0,
            'denda_amount': 10000.0,
        })
        self.assertEqual(stmt.state, 'draft')
        stmt.action_post()
        self.assertEqual(stmt.state, 'posted')

    def test_premi_statement_set_draft(self):
        """Test resetting posted statement back to draft."""
        employee = self._get_or_skip_employee()
        stmt = self.PremiStatement.create({
            'date': '2025-01-15',
            'harvester_id': employee.id,
            'premi_amount': 120000.0,
            'denda_amount': 5000.0,
            'state': 'posted',
        })
        stmt.action_draft()
        self.assertEqual(stmt.state, 'draft')

    def test_premi_statement_multi_create(self):
        """Test batch creation of premi statements."""
        employee = self._get_or_skip_employee()
        statements = self.PremiStatement.create([
            {
                'date': '2025-01-14',
                'harvester_id': employee.id,
                'premi_amount': 100000.0,
                'denda_amount': 0.0,
            },
            {
                'date': '2025-01-15',
                'harvester_id': employee.id,
                'premi_amount': 110000.0,
                'denda_amount': 5000.0,
            },
        ])
        self.assertEqual(len(statements), 2)
        self.assertEqual(statements[0].net_premi, 100000.0)
        self.assertEqual(statements[1].net_premi, 105000.0)