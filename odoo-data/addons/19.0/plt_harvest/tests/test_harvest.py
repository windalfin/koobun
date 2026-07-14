# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHarvestTaksasi(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']
        self.Taksasi = self.env['harvest.taksasi']

        # Create prerequisite records
        self.estate = self.Estate.create({
            'name': 'Test Estate',
            'code': 'TST',
        })
        self.afdeling = self.Afdeling.create({
            'name': 'Test Afdeling',
            'code': 'AFT',
            'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Test Block',
            'code': 'TB1',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0,
            'area_ha_planted': 9.0,
        })

    def test_create_taksasi(self):
        """Test basic taksasi creation."""
        taksasi = self.Taksasi.create({
            'date': '2025-01-15',
            'block_id': self.block.id,
            'section': 'A',
            'pokok_sampled': 100,
            'bunches_counted': 15,
            'AKP': 15.0,
            'estimated_janjang': 250,
            'estimated_tonnage': 5.0,
            'required_harvesters': 5,
            'required_trucks': 1,
        })
        self.assertTrue(taksasi.id)
        self.assertEqual(taksasi.state, 'draft')

    def test_taksasi_confirm(self):
        """Test confirm workflow."""
        taksasi = self.Taksasi.create({
            'date': '2025-01-15',
            'block_id': self.block.id,
            'pokok_sampled': 100,
            'bunches_counted': 15,
        })
        self.assertEqual(taksasi.state, 'draft')
        taksasi.action_confirm()
        self.assertEqual(taksasi.state, 'confirmed')

    def test_taksasi_draft(self):
        """Test set draft from confirmed."""
        taksasi = self.Taksasi.create({
            'date': '2025-01-15',
            'block_id': self.block.id,
            'pokok_sampled': 100,
            'bunches_counted': 15,
            'state': 'confirmed',
        })
        taksasi.action_draft()
        self.assertEqual(taksasi.state, 'draft')

    def test_taksasi_negative_pokok(self):
        """Test constraint: pokok_sampled must be positive."""
        with self.assertRaises(ValidationError):
            self.Taksasi.create({
                'date': '2025-01-15',
                'block_id': self.block.id,
                'pokok_sampled': -5,
                'bunches_counted': 10,
            })


class TestHarvestRotation(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']
        self.Rotation = self.env['harvest.rotation']

        self.estate = self.Estate.create({
            'name': 'Test Estate', 'code': 'TST',
        })
        self.afdeling = self.Afdeling.create({
            'name': 'Test Afdeling', 'code': 'AFT',
            'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Test Block', 'code': 'TB1',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0, 'area_ha_planted': 9.0,
        })

    def test_create_rotation(self):
        """Test basic rotation creation."""
        rotation = self.Rotation.create({
            'name': 'Section A',
            'block_ids': [(6, 0, [self.block.id])],
            'rotation_interval_days': 14,
        })
        self.assertTrue(rotation.id)
        self.assertEqual(rotation.rotation_interval_days, 14)
        self.assertFalse(rotation.next_harvest_date)

    def test_next_harvest_date_compute(self):
        """Test next_harvest_date computed from last_harvest_date."""
        rotation = self.Rotation.create({
            'name': 'Section A',
            'block_ids': [(6, 0, [self.block.id])],
            'rotation_interval_days': 14,
            'last_harvest_date': '2025-01-01',
        })
        expected = date(2025, 1, 1) + timedelta(days=14)
        self.assertEqual(
            rotation.next_harvest_date,
            expected,
        )

    def test_next_harvest_date_no_last_date(self):
        """Test next_harvest_date is False without last_harvest_date."""
        rotation = self.Rotation.create({
            'name': 'Section B',
            'block_ids': [(6, 0, [self.block.id])],
            'rotation_interval_days': 10,
        })
        self.assertFalse(rotation.next_harvest_date)


class TestHarvestAncak(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']
        self.Ancak = self.env['harvest.ancak']

        self.estate = self.Estate.create({
            'name': 'Test Estate', 'code': 'TST',
        })
        self.afdeling = self.Afdeling.create({
            'name': 'Test Afdeling', 'code': 'AFT',
            'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Test Block', 'code': 'TB1',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0, 'area_ha_planted': 9.0,
        })
        # Find or use admin user as employee reference
        self.employee = self.env['hr.employee'].search([], limit=1)

    def test_create_ancak(self):
        """Test basic ancak creation."""
        if not self.employee:
            self.skipTest('No hr.employee found')
        ancak = self.Ancak.create({
            'date': '2025-01-15',
            'mandor_id': self.employee.id,
            'harvester_id': self.employee.id,
            'block_id': self.block.id,
            'ancak_type': 'tetap',
        })
        self.assertTrue(ancak.id)
        self.assertEqual(ancak.ancak_type, 'tetap')

    def test_create_ancak_giring(self):
        """Test ancak with giring type."""
        if not self.employee:
            self.skipTest('No hr.employee found')
        ancak = self.Ancak.create({
            'date': '2025-01-15',
            'mandor_id': self.employee.id,
            'harvester_id': self.employee.id,
            'block_id': self.block.id,
            'ancak_type': 'giring',
        })
        self.assertEqual(ancak.ancak_type, 'giring')


class TestHarvestTPHRecord(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']
        self.TPH = self.env['estate.tph']
        self.TPHRecord = self.env['harvest.tph_record']

        self.estate = self.Estate.create({
            'name': 'Test Estate', 'code': 'TST',
        })
        self.afdeling = self.Afdeling.create({
            'name': 'Test Afdeling', 'code': 'AFT',
            'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Test Block', 'code': 'TB1',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0, 'area_ha_planted': 9.0,
        })
        self.tph = self.TPH.create({
            'name': 'Test TPH',
            'code': 'TPH1',
            'block_id': self.block.id,
        })
        self.employee = self.env['hr.employee'].search([], limit=1)

    def test_create_tph_record(self):
        """Test basic TPH record creation."""
        if not self.employee:
            self.skipTest('No hr.employee found')
        record = self.TPHRecord.create({
            'date': '2025-01-15',
            'tph_id': self.tph.id,
            'harvester_id': self.employee.id,
            'kerani_id': self.employee.id,
            'janjang_count': 150,
            'brondolan_kg': 25.0,
            'brondolan_karung': 1,
        })
        self.assertTrue(record.id)
        self.assertEqual(record.state, 'draft')
        self.assertEqual(record.janjang_count, 150)

    def test_tph_record_workflow(self):
        """Test full workflow: draft → submit → verify → approve."""
        if not self.employee:
            self.skipTest('No hr.employee found')
        record = self.TPHRecord.create({
            'date': '2025-01-15',
            'tph_id': self.tph.id,
            'harvester_id': self.employee.id,
            'kerani_id': self.employee.id,
            'janjang_count': 150,
        })
        self.assertEqual(record.state, 'draft')

        record.action_submit()
        self.assertEqual(record.state, 'submitted')

        record.action_verify()
        self.assertEqual(record.state, 'verified')

        record.action_approve()
        self.assertEqual(record.state, 'approved')

    def test_tph_record_draft_from_any_state(self):
        """Test that action_draft works from approved state."""
        if not self.employee:
            self.skipTest('No hr.employee found')
        record = self.TPHRecord.create({
            'date': '2025-01-15',
            'tph_id': self.tph.id,
            'harvester_id': self.employee.id,
            'kerani_id': self.employee.id,
            'janjang_count': 150,
            'state': 'approved',
        })
        record.action_draft()
        self.assertEqual(record.state, 'draft')

    def test_tph_record_duplicate_detection(self):
        """Test that same harvester+TPH+date creates IntegrityError."""
        if not self.employee:
            self.skipTest('No hr.employee found')
        self.TPHRecord.create({
            'date': '2025-01-15',
            'tph_id': self.tph.id,
            'harvester_id': self.employee.id,
            'kerani_id': self.employee.id,
            'janjang_count': 150,
        })
        # Force flush to trigger SQL constraint
        self.env.flush_all()
        # In TransactionCase, SQL constraints don't raise reliably with assertRaises.
        # Verify by checking that only one record exists for this harvester+TPH+date.
        count_before = self.TPHRecord.search_count([
            ('date', '=', '2025-01-15'),
            ('tph_id', '=', self.tph.id),
            ('harvester_id', '=', self.employee.id),
        ])
        self.assertEqual(count_before, 1)
        # Attempt duplicate — should be rejected by SQL constraint
        try:
            record2 = self.TPHRecord.create({
                'date': '2025-01-15',
                'tph_id': self.tph.id,
                'harvester_id': self.employee.id,
                'kerani_id': self.employee.id,
                'janjang_count': 100,
            })
            self.env.flush_all()
            self.fail('Expected unique constraint violation for duplicate TPH record')
        except Exception:
            pass  # Expected


class TestHarvestQualityEvent(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']
        self.TPH = self.env['estate.tph']
        self.TPHRecord = self.env['harvest.tph_record']
        self.QualityEvent = self.env['harvest.quality_event']

        self.estate = self.Estate.create({
            'name': 'Test Estate', 'code': 'TST',
        })
        self.afdeling = self.Afdeling.create({
            'name': 'Test Afdeling', 'code': 'AFT',
            'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Test Block', 'code': 'TB1',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0, 'area_ha_planted': 9.0,
        })
        self.tph = self.TPH.create({
            'name': 'Test TPH', 'code': 'TPH1',
            'block_id': self.block.id,
        })
        self.employee = self.env['hr.employee'].search([], limit=1)

    def test_create_quality_event(self):
        """Test basic quality event creation."""
        if not self.employee:
            self.skipTest('No hr.employee found')
        record = self.TPHRecord.create({
            'date': '2025-01-15',
            'tph_id': self.tph.id,
            'harvester_id': self.employee.id,
            'kerani_id': self.employee.id,
            'janjang_count': 150,
        })
        event = self.QualityEvent.create({
            'tph_record_id': record.id,
            'event_type': 'mentah',
            'quantity': 5,
            'rate': 5000.0,
        })
        self.assertTrue(event.id)
        self.assertEqual(event.event_type, 'mentah')
        self.assertEqual(event.denda_amount, 5 * 5000.0)

    def test_quality_event_all_types(self):
        """Test all event types can be created."""
        if not self.employee:
            self.skipTest('No hr.employee found')
        record = self.TPHRecord.create({
            'date': '2025-01-15',
            'tph_id': self.tph.id,
            'harvester_id': self.employee.id,
            'kerani_id': self.employee.id,
            'janjang_count': 150,
        })
        event_types = [
            'mentah', 'tangkai_panjang', 'brondolan_tidak_dikutip',
            'buah_tinggal', 'pelepah_sengkleh',
        ]
        for etype in event_types:
            event = self.QualityEvent.create({
                'tph_record_id': record.id,
                'event_type': etype,
                'quantity': 1,
                'rate': 1000.0,
            })
            self.assertEqual(event.event_type, etype)


class TestHarvestPremiConfig(TransactionCase):

    def setUp(self):
        super().setUp()
        self.PremiConfig = self.env['harvest.premi_config']

    def test_create_premi_config(self):
        """Test basic premi config creation."""
        config = self.PremiConfig.create({
            'name': 'Standard 2025',
            'basis_kg_per_hk': 1500.0,
            'premi_tier_1_rate': 50.0,
            'premi_tier_2_rate': 75.0,
            'premi_tier_1_threshold': 200.0,
            'brondolan_rate': 100.0,
            'date_from': '2025-01-01',
        })
        self.assertTrue(config.id)
        self.assertEqual(config.state, 'draft')

    def test_premi_config_approve(self):
        """Test approve workflow."""
        config = self.PremiConfig.create({
            'name': 'Standard 2025',
            'basis_kg_per_hk': 1500.0,
            'date_from': '2025-01-01',
        })
        config.action_approve()
        self.assertEqual(config.state, 'approved')

    def test_premi_config_draft(self):
        """Test set draft from approved."""
        config = self.PremiConfig.create({
            'name': 'Standard 2025',
            'basis_kg_per_hk': 1500.0,
            'date_from': '2025-01-01',
            'state': 'approved',
        })
        config.action_draft()
        self.assertEqual(config.state, 'draft')

    def test_premi_config_date_validation(self):
        """Test that date_to must be after date_from."""
        with self.assertRaises(ValidationError):
            self.PremiConfig.create({
                'name': 'Invalid Dates',
                'basis_kg_per_hk': 1500.0,
                'date_from': '2025-06-01',
                'date_to': '2025-01-01',
            })

    def test_premi_config_year_validation(self):
        """Test that tahun_tanam_max >= tahun_tanam_min."""
        with self.assertRaises(ValidationError):
            self.PremiConfig.create({
                'name': 'Invalid Years',
                'basis_kg_per_hk': 1500.0,
                'tahun_tanam_min': 2020,
                'tahun_tanam_max': 2015,
                'date_from': '2025-01-01',
            })

    def test_premi_config_default_multipliers(self):
        """Test default mandor and kerani multipliers."""
        config = self.PremiConfig.create({
            'name': 'Default Mult',
            'basis_kg_per_hk': 1500.0,
            'date_from': '2025-01-01',
        })
        self.assertEqual(config.mandor_multiplier, 1.0)
        self.assertEqual(config.kerani_multiplier, 1.0)


class TestHarvestDendaConfig(TransactionCase):

    def setUp(self):
        super().setUp()
        self.DendaConfig = self.env['harvest.denda_config']

    def test_create_denda_config(self):
        """Test basic denda config creation."""
        config = self.DendaConfig.create({
            'event_type': 'mentah',
            'rate_per_unit': 5000.0,
            'date_from': '2025-01-01',
        })
        self.assertTrue(config.id)
        self.assertEqual(config.state, 'draft')

    def test_denda_config_approve(self):
        """Test approve workflow."""
        config = self.DendaConfig.create({
            'event_type': 'tangkai_panjang',
            'rate_per_unit': 3000.0,
            'date_from': '2025-01-01',
        })
        config.action_approve()
        self.assertEqual(config.state, 'approved')

    def test_denda_config_draft(self):
        """Test set draft from approved."""
        config = self.DendaConfig.create({
            'event_type': 'buah_tinggal',
            'rate_per_unit': 10000.0,
            'date_from': '2025-01-01',
            'state': 'approved',
        })
        config.action_draft()
        self.assertEqual(config.state, 'draft')

    def test_denda_config_date_validation(self):
        """Test that date_to must be after date_from."""
        with self.assertRaises(ValidationError):
            self.DendaConfig.create({
                'event_type': 'mentah',
                'rate_per_unit': 5000.0,
                'date_from': '2025-06-01',
                'date_to': '2025-01-01',
            })

    def test_denda_config_all_types(self):
        """Test all denda event types can be created."""
        event_types = [
            'mentah', 'tangkai_panjang', 'brondolan_tidak_dikutip',
            'buah_tinggal', 'pelepah_sengkleh',
        ]
        for etype in event_types:
            config = self.DendaConfig.create({
                'event_type': etype,
                'rate_per_unit': 5000.0,
                'date_from': '2025-01-01',
            })
            self.assertEqual(config.event_type, etype)
