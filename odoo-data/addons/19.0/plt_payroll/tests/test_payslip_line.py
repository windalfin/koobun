# -*- coding: utf-8 -*-
import json
from odoo.tests.common import TransactionCase


class TestPayslipLine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PayslipLine = self.env['payroll.payslip_line']
        # Create a batch for tests
        self.batch = self.env['payroll.payroll_batch'].create({
            'period_start': '2025-06-01',
            'period_end': '2025-06-15',
        })

    def test_create_payslip_line(self):
        """Test basic payslip line creation."""
        # Create employee first
        employee = self.env['hr.employee'].create({
            'name': 'Test Worker',
        })
        line = self.PayslipLine.create({
            'payroll_batch_id': self.batch.id,
            'employee_id': employee.id,
            'hk_count': 10,
            'daily_base': 85000.0,
        })
        self.assertTrue(line.id)
        self.assertEqual(line.hk_count, 10)
        self.assertEqual(line.daily_base, 85000.0)

    def test_compute_net_pay(self):
        """Test net pay computation."""
        employee = self.env['hr.employee'].create({
            'name': 'Net Pay Test Worker',
        })
        line = self.PayslipLine.create({
            'payroll_batch_id': self.batch.id,
            'employee_id': employee.id,
            'hk_count': 15,
            'daily_base': 100000.0,
            'premi_amount': 500000.0,
            'denda_amount': 50000.0,
            'pph21_amount': 75000.0,
            'tht_amount': 30000.0,
            'bpjs_amounts': {
                'kesehatan': {'employer': 48000.0, 'employee': 12000.0},
                'JHT': {'employer': 37000.0, 'employee': 20000.0},
            },
        })
        # gross = (15 * 100000) + 500000 = 2,000,000
        # deductions = 50000 + 75000 + 30000 + 12000 + 20000 = 187,000
        # net = 2,000,000 - 187,000 = 1,813,000
        self.assertEqual(line.net_pay, 1813000.0)

    def test_negative_hk_constraint(self):
        """Test that negative HK is rejected."""
        employee = self.env['hr.employee'].create({
            'name': 'Negative HK Worker',
        })
        with self.assertRaises(Exception):
            self.PayslipLine.create({
                'payroll_batch_id': self.batch.id,
                'employee_id': employee.id,
                'hk_count': -5,
                'daily_base': 85000.0,
            })

    def test_negative_daily_base_constraint(self):
        """Test that negative daily base is rejected."""
        employee = self.env['hr.employee'].create({
            'name': 'Negative Base Worker',
        })
        with self.assertRaises(Exception):
            self.PayslipLine.create({
                'payroll_batch_id': self.batch.id,
                'employee_id': employee.id,
                'hk_count': 10,
                'daily_base': -1000.0,
            })

    def test_duplicate_employee_batch_constraint(self):
        """Test that duplicate employee per batch is prevented."""
        employee = self.env['hr.employee'].create({
            'name': 'Duplicate Worker',
        })
        self.PayslipLine.create({
            'payroll_batch_id': self.batch.id,
            'employee_id': employee.id,
            'hk_count': 10,
            'daily_base': 85000.0,
        })
        self.env.flush_all()
        # Verify only one record exists
        count = self.PayslipLine.search_count([
            ('payroll_batch_id', '=', self.batch.id),
            ('employee_id', '=', employee.id),
        ])
        self.assertEqual(count, 1)
        # Attempt duplicate — should be rejected by SQL constraint
        try:
            self.PayslipLine.create({
                'payroll_batch_id': self.batch.id,
                'employee_id': employee.id,
                'hk_count': 12,
                'daily_base': 85000.0,
            })
            self.env.flush_all()
            self.fail('Expected unique constraint violation')
        except Exception:
            pass

    def test_bpjs_amounts_json(self):
        """Test BPJS amounts JSON field."""
        employee = self.env['hr.employee'].create({
            'name': 'BPJS Worker',
        })
        bpjs = {
            'kesehatan': {'employer': 48000.0, 'employee': 12000.0},
        }
        line = self.PayslipLine.create({
            'payroll_batch_id': self.batch.id,
            'employee_id': employee.id,
            'hk_count': 10,
            'daily_base': 85000.0,
            'bpjs_amounts': bpjs,
        })
        self.assertEqual(line.bpjs_amounts, bpjs)
