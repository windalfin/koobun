# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWorkerContract(TransactionCase):

    def setUp(self):
        super().setUp()
        self.WorkerContract = self.env['payroll.worker_contract']

    def test_create_worker_contract(self):
        """Test creating a worker contract with BHL class."""
        employee = self.env['hr.employee'].create({
            'name': 'BHL Worker',
        })
        contract = self.WorkerContract.create({
            'name': 'BHL Daily Contract',
            'employee_id': employee.id,
            'worker_class': 'BHL',
            'contract_type': 'PKWT',
            'wage': 2550000.0,
            'date_start': '2025-01-01',
        })
        self.assertTrue(contract.id)
        self.assertEqual(contract.worker_class, 'BHL')
        self.assertEqual(contract.contract_type, 'PKWT')
        self.assertTrue(contract.bpjs_applicable)
        self.assertTrue(contract.pph21_applicable)

    def test_staff_must_be_pkwtt(self):
        """Test that staff with non-PKWTT raises."""
        employee = self.env['hr.employee'].create({
            'name': 'Staff Worker',
        })
        with self.assertRaises(Exception):
            self.WorkerContract.create({
                'name': 'Staff Contract',
                'employee_id': employee.id,
                'worker_class': 'staff',
                'contract_type': 'PKWT',
                'wage': 8000000.0,
                'date_start': '2025-01-01',
            })

    def test_auto_link_wage_master(self):
        """Test that wage_master_id is auto-linked on creation."""
        # Create an approved wage master
        wage_master = self.env['payroll.wage_master'].create({
            'name': 'BHL Wage 2025',
            'worker_class': 'BHL',
            'daily_wage': 85000.0,
            'effective_from': '2025-01-01',
        })
        wage_master.action_approve()

        employee = self.env['hr.employee'].create({
            'name': 'Auto Link Worker',
        })
        contract = self.WorkerContract.create({
            'name': 'Auto Link Contract',
            'employee_id': employee.id,
            'worker_class': 'BHL',
            'contract_type': 'PKWT',
            'wage': 2550000.0,
            'date_start': '2025-01-01',
        })
        self.assertEqual(contract.wage_master_id, wage_master)

    def test_bpjs_pph21_flags(self):
        """Test BPJS and PPh 21 boolean flags."""
        employee = self.env['hr.employee'].create({
            'name': 'No BPJS Worker',
        })
        contract = self.WorkerContract.create({
            'name': 'No BPJS Contract',
            'employee_id': employee.id,
            'worker_class': 'BHL',
            'contract_type': 'PKWT',
            'wage': 2550000.0,
            'date_start': '2025-01-01',
            'bpjs_applicable': False,
            'pph21_applicable': False,
        })
        self.assertFalse(contract.bpjs_applicable)
        self.assertFalse(contract.pph21_applicable)
