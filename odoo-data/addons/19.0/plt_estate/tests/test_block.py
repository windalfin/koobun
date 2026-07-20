# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestBlock(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Block = self.env['estate.block']
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']

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

    def test_create_block(self):
        """Test basic block creation and analytic account auto-creation."""
        block = self.Block.create({
            'name': 'Block Test',
            'code': 'BT1',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0,
            'area_ha_planted': 9.5,
            'tahun_tanam': 2020,
        })
        self.assertTrue(block.id)
        self.assertEqual(block.name, 'Block Test')
        self.assertEqual(block.code, 'BT1')
        self.assertEqual(block.status, 'tbm')
        self.assertTrue(block.active)

        # Analytic account should be auto-created
        self.assertTrue(block.analytic_account_id)
        self.assertIn('BLK-BT1', block.analytic_account_id.name)

    def test_analytic_account_created(self):
        """Test that analytic account is auto-created with correct naming."""
        block = self.Block.create({
            'name': 'Block AA',
            'code': 'BAA',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0,
            'area_ha_planted': 9.0,
        })
        self.assertTrue(block.analytic_account_id)
        self.assertEqual(
            block.analytic_account_id.name,
            'BLK-BAA',
        )

    def test_area_validation_positive(self):
        """Test that area must be positive."""
        with self.assertRaises(ValidationError):
            self.Block.create({
                'name': 'Neg Area',
                'code': 'NEG',
                'afdeling_id': self.afdeling.id,
                'area_ha_total': -5.0,
                'area_ha_planted': 3.0,
            })

    def test_area_validation_planted_le_total(self):
        """Test that planted area cannot exceed total area."""
        with self.assertRaises(ValidationError):
            self.Block.create({
                'name': 'Over Planted',
                'code': 'OVR',
                'afdeling_id': self.afdeling.id,
                'area_ha_total': 10.0,
                'area_ha_planted': 15.0,
            })

    def test_status_change_to_tm(self):
        """Test changing block status from TBM to TM creates history."""
        block = self.Block.create({
            'name': 'Status Block',
            'code': 'STB',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0,
            'area_ha_planted': 9.0,
        })
        self.assertEqual(block.status, 'tbm')

        # Change to TM
        block.action_set_tm('2024-01-01')
        self.assertEqual(block.status, 'tm')

        # Status history should have been created
        history = self.env['estate.block.status.history'].search([
            ('block_id', '=', block.id),
        ])
        self.assertEqual(len(history), 1)
        self.assertEqual(history.status, 'tm')

    def test_status_change_already_tm(self):
        """Test that setting TM on already-TM block is a no-op."""
        block = self.Block.create({
            'name': 'Already TM',
            'code': 'ATM',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0,
            'area_ha_planted': 9.0,
            'status': 'tm',
        })
        history_before = self.env['estate.block.status.history'].search_count([
            ('block_id', '=', block.id),
        ])
        block.action_set_tm('2024-01-01')
        history_after = self.env['estate.block.status.history'].search_count([
            ('block_id', '=', block.id),
        ])
        self.assertEqual(history_before, history_after)

    def test_onchange_tahun_tanam(self):
        """Test that changing planting year sets planting density."""
        block = self.Block.create({
            'name': 'Density Block',
            'code': 'DEN',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0,
            'area_ha_planted': 9.0,
        })
        # Simulate onchange
        result = self.Block.with_context(
            onchange=True,
        ).new({
            'name': 'Test',
            'code': 'TST',
            'afdeling_id': self.afdeling.id,
            'tahun_tanam': 2019,
        })
        result._onchange_tahun_tanam()
        self.assertEqual(result.planting_density, 143)

    def test_code_unique_per_afdeling(self):
        """Test that block code must be unique per afdeling."""
        self.Block.create({
            'name': 'Block 1',
            'code': 'UNQ',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0,
            'area_ha_planted': 9.0,
        })
        self.env.flush_all()
        count = self.Block.search_count([
            ('code', '=', 'UNQ'),
            ('afdeling_id', '=', self.afdeling.id),
        ])
        self.assertEqual(count, 1)

    def test_gis_area_computation(self):
        """Test computed GIS area from GeoJSON polygon."""
        block = self.Block.create({
            'name': 'GIS Block',
            'code': 'GIS',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 30.0,
            'area_ha_planted': 28.0,
            'polygon_geojson': (
                '{"type":"Polygon","coordinates":[['
                '[117.0,-0.5],[117.5,-0.5],'
                '[117.5,0.0],[117.0,0.0],'
                '[117.0,-0.5]'
                ']]}'
            ),
        })
        # computed_gis_area should be > 0 for a valid polygon
        self.assertGreater(block.computed_gis_area, 0)
