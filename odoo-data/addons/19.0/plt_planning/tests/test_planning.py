# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestNormaKerja(TransactionCase):

    def setUp(self):
        super().setUp()
        self.NormaKerja = self.env['plan.norma_kerja']
        self.ActivityCode = self.env['upkeep.activity_code']
        self.activity = self.ActivityCode.create({
            'name': 'Pemupukan', 'code': 'PM-TEST', 'category': 'pemupukan',
        })

    def test_01_create_norma_kerja(self):
        """Test creating a work norm."""
        norma = self.NormaKerja.create({
            'activity_code_id': self.activity.id,
            'output_per_hk': 2.5,
            'effective_from': '2025-01-01',
        })
        self.assertTrue(norma.id)
        self.assertEqual(norma.state, 'draft')
        self.assertEqual(norma.output_per_hk, 2.5)

    def test_02_invalid_date_range(self):
        """Test effective_to < effective_from is rejected."""
        with self.assertRaises(Exception):
            self.NormaKerja.create({
                'activity_code_id': self.activity.id,
                'output_per_hk': 2.0,
                'effective_from': '2025-12-31',
                'effective_to': '2025-01-01',
            })


class TestRKAP(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RKAP = cls.env['plan.rkap']
        cls.Estate = cls.env['estate.estate']
        cls.Afdeling = cls.env['estate.afdeling']
        cls.Block = cls.env['estate.block']
        cls.ActivityCode = cls.env['upkeep.activity_code']

        cls.estate = cls.Estate.create({'name': 'Test Estate', 'code': 'TE'})
        cls.afdeling = cls.Afdeling.create({
            'name': 'Afdeling A', 'code': 'A', 'estate_id': cls.estate.id,
        })
        cls.block = cls.Block.create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': cls.afdeling.id,
        })
        cls.activity = cls.ActivityCode.create({
            'name': 'Pemupukan', 'code': 'PM-RKAP', 'category': 'pemupukan',
        })

    def test_01_create_rkap(self):
        """Test creating an RKAP entry."""
        rkap = self.RKAP.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '1',
            'physical_qty': 10.0,
            'hk_planned': 5.0,
        })
        self.assertTrue(rkap.id)
        self.assertEqual(rkap.state, 'draft')
        self.assertEqual(rkap.year, 2025)

    def test_02_rkap_workflow(self):
        """Test the full state workflow."""
        rkap = self.RKAP.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '2',
            'physical_qty': 10.0,
        })
        rkap.action_propose()
        self.assertEqual(rkap.state, 'proposed')
        rkap.action_approve()
        self.assertEqual(rkap.state, 'approved')

    def test_03_total_cost_computed(self):
        """Test total cost is sum of material + labor."""
        rkap = self.RKAP.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '3',
            'physical_qty': 10.0,
            'material_cost': 500000.0,
            'labor_cost': 300000.0,
        })
        self.assertEqual(rkap.total_cost, 800000.0)


class TestRKB(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RKB = cls.env['plan.rkb']
        cls.Estate = cls.env['estate.estate']
        cls.Afdeling = cls.env['estate.afdeling']
        cls.Block = cls.env['estate.block']
        cls.ActivityCode = cls.env['upkeep.activity_code']

        cls.estate = cls.Estate.create({'name': 'Test', 'code': 'TE'})
        cls.afdeling = cls.Afdeling.create({
            'name': 'Afd. A', 'code': 'A', 'estate_id': cls.estate.id,
        })
        cls.block = cls.Block.create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': cls.afdeling.id,
        })
        cls.activity = cls.ActivityCode.create({
            'name': 'Pemupukan', 'code': 'PM-RKB', 'category': 'pemupukan',
        })

    def test_01_create_rkb(self):
        """Test creating an RKB entry."""
        rkb = self.RKB.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '1',
            'physical_qty': 10.0,
        })
        self.assertTrue(rkb.id)
        self.assertEqual(rkb.state, 'draft')

    def test_02_rkb_workflow(self):
        """Test RKB state workflow."""
        rkb = self.RKB.create({
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'year': 2025,
            'month': '2',
            'physical_qty': 10.0,
        })
        rkb.action_submit()
        self.assertEqual(rkb.state, 'submitted')
        rkb.action_approve()
        self.assertEqual(rkb.state, 'approved')


class TestRKH(TransactionCase):

    def setUp(self):
        super().setUp()
        self.RKH = self.env['plan.rkh']
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']
        self.ActivityCode = self.env['upkeep.activity_code']
        self.Employee = self.env['hr.employee']

        self.estate = self.Estate.create({'name': 'Test', 'code': 'TE'})
        self.afdeling = self.Afdeling.create({
            'name': 'Afd. A', 'code': 'A', 'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': self.afdeling.id,
        })
        self.activity = self.ActivityCode.create({
            'name': 'Pemupukan', 'code': 'PM-RKH', 'category': 'pemupukan',
        })
        self.employee = self.Employee.create({'name': 'Mandor Test'})

    def test_01_create_rkh(self):
        """Test creating a daily work order."""
        rkh = self.RKH.create({
            'date': '2025-01-15',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'target_qty': 5.0,
        })
        self.assertTrue(rkh.id)
        self.assertEqual(rkh.state, 'draft')

    def test_02_rkh_workflow(self):
        """Test RKH state flow."""
        rkh = self.RKH.create({
            'date': '2025-01-15',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'target_qty': 5.0,
        })
        rkh.action_issue()
        self.assertEqual(rkh.state, 'issued')
        rkh.action_complete()
        self.assertEqual(rkh.state, 'completed')
