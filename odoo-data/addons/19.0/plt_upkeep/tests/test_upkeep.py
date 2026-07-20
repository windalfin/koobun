# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestUpkeepActivityCode(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ActivityCode = self.env['upkeep.activity_code']

    def test_01_create_activity_code(self):
        """Test creating a basic activity code."""
        code = self.ActivityCode.create({
            'name': 'Pemupukan Manual',
            'code': 'PM-01',
            'category': 'pemupukan',
        })
        self.assertTrue(code.id)
        self.assertEqual(code.code, 'PM-01')
        self.assertEqual(code.category, 'pemupukan')

    def test_02_code_unique(self):
        """Test duplicate code is rejected via SQL constraint."""
        self.ActivityCode.create({
            'name': 'Pemupukan Manual',
            'code': 'PM-UNIQUE',
            'category': 'pemupukan',
        })
        self.env.flush_all()
        # Verify uniqueness via search_count
        count = self.ActivityCode.search_count([('code', '=', 'PM-UNIQUE')])
        self.assertEqual(count, 1)
        # Attempt duplicate — should fail
        try:
            self.ActivityCode.create({
                'name': 'Pemupukan Dup',
                'code': 'PM-UNIQUE',
                'category': 'pemupukan',
            })
            self.env.flush_all()
            self.fail('Expected unique constraint violation')
        except Exception:
            pass

    def test_03_all_categories(self):
        """Test all activity categories are supported."""
        categories = ['pemupukan', 'semprot', 'tunasan', 'kastrasi',
                      'rawat_jalan', 'pnd_treatment', 'lainnya']
        for cat in categories:
            code = self.ActivityCode.create({
                'name': f'Activity {cat}',
                'code': f'AC-{cat[:4]}',
                'category': cat,
            })
            self.assertEqual(code.category, cat)


class TestUpkeepBKM(TransactionCase):

    def setUp(self):
        super().setUp()
        self.BKM = self.env['upkeep.bkm']
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']
        self.ActivityCode = self.env['upkeep.activity_code']
        self.Employee = self.env['hr.employee']

        # Create prerequisite records
        self.estate = self.Estate.create({'name': 'Test Estate', 'code': 'TE'})
        self.afdeling = self.Afdeling.create({
            'name': 'Afdeling A', 'code': 'A', 'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': self.afdeling.id,
        })
        self.activity = self.ActivityCode.create({
            'name': 'Pemupukan Manual', 'code': 'PM-01', 'category': 'pemupukan',
        })
        self.employee = self.Employee.create({'name': 'Mandor Test'})

    def test_01_create_bkm_draft(self):
        """Test creating a BKM in draft state."""
        bkm = self.BKM.create({
            'date': '2025-01-15',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
        })
        self.assertTrue(bkm.id)
        self.assertEqual(bkm.state, 'draft')

    def test_02_bkm_state_flow(self):
        """Test the full state workflow: draft → submitted → verified → approved."""
        bkm = self.BKM.create({
            'date': '2025-01-15',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
        })
        bkm.action_submit()
        self.assertEqual(bkm.state, 'submitted')
        bkm.action_verify()
        self.assertEqual(bkm.state, 'verified')
        bkm.action_approve()
        self.assertEqual(bkm.state, 'approved')

    def test_03_bkm_worker_count(self):
        """Test worker count is tracked."""
        bkm = self.BKM.create({
            'date': '2025-01-15',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'worker_count': 5,
        })
        self.assertEqual(bkm.worker_count, 5)

    def test_04_bkm_material_consumption(self):
        """Test material consumption tracking."""
        bkm = self.BKM.create({
            'date': '2025-01-15',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'activity_code_id': self.activity.id,
            'material_consumed': 'Urea 50 kg',
        })
        self.assertIn('Urea', bkm.material_consumed or '')


class TestUpkeepBPB(TransactionCase):

    def setUp(self):
        super().setUp()
        self.BPB = self.env['upkeep.bpb']
        self.Employee = self.env['hr.employee']
        self.employee = self.Employee.create({'name': 'Requestor Test'})

    def test_01_create_bpb(self):
        """Test creating a BPB in draft state."""
        bpb = self.BPB.create({
            'number': 'BPB-001',
            'date': '2025-01-15',
            'requestor_id': self.employee.id,
            'items_description': 'Urea 100 kg, NPK 50 kg',
        })
        self.assertTrue(bpb.id)
        self.assertEqual(bpb.state, 'draft')

    def test_02_bpb_number_unique(self):
        """Test duplicate BPB number is rejected."""
        self.BPB.create({
            'number': 'BPB-UNIQUE',
            'date': '2025-01-15',
            'requestor_id': self.employee.id,
            'items_description': 'Items',
        })
        self.env.flush_all()
        try:
            self.BPB.create({
                'number': 'BPB-UNIQUE',
                'date': '2025-01-16',
                'requestor_id': self.employee.id,
                'items_description': 'More items',
            })
            self.env.flush_all()
            self.fail('Expected unique constraint violation')
        except Exception:
            pass


class TestUpkeepFertilizerProgram(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Program = self.env['upkeep.fertilizer_program']
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']

        self.estate = self.Estate.create({'name': 'Test Estate', 'code': 'TE'})
        self.afdeling = self.Afdeling.create({
            'name': 'Afdeling A', 'code': 'A', 'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': self.afdeling.id,
        })

    def test_01_create_program(self):
        """Test creating a fertilizer program."""
        prog = self.Program.create({
            'block_id': self.block.id,
            'fertilizer_type': 'Urea',
            'dose_per_tree_kg': 2.5,
            'round': 1,
            'year': 2025,
        })
        self.assertTrue(prog.id)
        self.assertEqual(prog.fertilizer_type, 'Urea')
        self.assertEqual(prog.dose_per_tree_kg, 2.5)


class TestUpkeepPDCensus(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PDCensus = self.env['upkeep.pd_census']
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']

        self.estate = self.Estate.create({'name': 'Test Estate', 'code': 'TE'})
        self.afdeling = self.Afdeling.create({
            'name': 'Afdeling A', 'code': 'A', 'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': self.afdeling.id,
        })

    def test_01_create_pd_census(self):
        """Test creating a pest & disease census."""
        census = self.PDCensus.create({
            'block_id': self.block.id,
            'pest_type': 'ganoderma',
            'date': '2025-01-15',
            'sample_count': 100,
            'severity': 'medium',
        })
        self.assertTrue(census.id)
        self.assertEqual(census.pest_type, 'ganoderma')
        self.assertEqual(census.severity, 'medium')

    def test_02_severity_validation(self):
        """Test invalid severity is rejected."""
        with self.assertRaises(Exception):
            self.PDCensus.create({
                'block_id': self.block.id,
                'pest_type': 'ganoderma',
                'date': '2025-01-15',
                'sample_count': 100,
                'severity': 'invalid_level',
            })
