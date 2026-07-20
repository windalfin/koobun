# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestCensus(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Census = self.env['estate.census']
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']

        self.estate = self.Estate.create({
            'name': 'Census Estate',
            'code': 'CEN',
        })
        self.afdeling = self.Afdeling.create({
            'name': 'Census Afdeling',
            'code': 'CAF',
            'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Census Block',
            'code': 'CB1',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0,
            'area_ha_planted': 9.0,
        })

    def test_create_census(self):
        """Test basic census creation."""
        census = self.Census.create({
            'date': '2024-06-01',
            'block_id': self.block.id,
            'productive_count': 1200,
            'unproductive_count': 50,
            'dead_count': 10,
            'vacant_points': 5,
            'sisipan_count': 20,
        })
        self.assertTrue(census.id)
        self.assertEqual(census.total_pokok, 1285)
        self.assertFalse(census.previous_census_id)

    def test_census_total_computation(self):
        """Test that total_pokok is correctly computed as sum of all counts."""
        census = self.Census.create({
            'date': '2024-06-01',
            'block_id': self.block.id,
            'productive_count': 100,
            'unproductive_count': 20,
            'dead_count': 5,
            'vacant_points': 3,
            'sisipan_count': 2,
        })
        self.assertEqual(census.total_pokok, 130)

    def test_previous_census_computation(self):
        """Test that previous_census_id points to earlier census of same block."""
        c1 = self.Census.create({
            'date': '2024-01-01',
            'block_id': self.block.id,
            'productive_count': 1000,
            'unproductive_count': 40,
            'dead_count': 8,
            'vacant_points': 4,
            'sisipan_count': 15,
        })
        c2 = self.Census.create({
            'date': '2024-07-01',
            'block_id': self.block.id,
            'productive_count': 1100,
            'unproductive_count': 35,
            'dead_count': 12,
            'vacant_points': 6,
            'sisipan_count': 10,
        })
        self.assertEqual(c2.previous_census_id, c1)
        self.assertFalse(c1.previous_census_id)

    def test_variance_computation(self):
        """Test that variance fields show differences from previous census."""
        c1 = self.Census.create({
            'date': '2024-01-01',
            'block_id': self.block.id,
            'productive_count': 1000,
            'unproductive_count': 40,
            'dead_count': 8,
            'vacant_points': 4,
            'sisipan_count': 15,
        })
        c2 = self.Census.create({
            'date': '2024-07-01',
            'block_id': self.block.id,
            'productive_count': 1100,
            'unproductive_count': 30,
            'dead_count': 12,
            'vacant_points': 10,
            'sisipan_count': 5,
        })
        self.assertEqual(c2.var_productive, 100)
        self.assertEqual(c2.var_unproductive, -10)
        self.assertEqual(c2.var_dead, 4)
        self.assertEqual(c2.var_vacant, 6)
        self.assertEqual(c2.var_sisipan, -10)
        # Total: c2 total - c1 total
        c1_total = 1000 + 40 + 8 + 4 + 15  # 1067
        c2_total = 1100 + 30 + 12 + 10 + 5  # 1157
        self.assertEqual(c2.var_total, c2_total - c1_total)

    def test_unique_date_per_block(self):
        """Test that only one census per block per day is allowed."""
        self.Census.create({
            'date': '2024-06-01',
            'block_id': self.block.id,
            'productive_count': 100,
        })
        self.env.flush_all()
        count = self.Census.search_count([
            ('date', '=', '2024-06-01'),
            ('block_id', '=', self.block.id),
        ])
        self.assertEqual(count, 1)
