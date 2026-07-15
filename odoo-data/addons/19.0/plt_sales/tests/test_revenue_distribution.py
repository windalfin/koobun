# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestSalesRevenueDistribution(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RevenueDist = cls.env['sales.revenue_distribution']

        # Estate / afdeling / block
        cls.estate = cls.env['estate.estate'].create({
            'name': 'Test Estate', 'code': 'TED',
        })
        cls.afdeling = cls.env['estate.afdeling'].create({
            'name': 'Test Afdeling', 'code': 'AFD',
            'estate_id': cls.estate.id,
        })
        cls.block = cls.env['estate.block'].create({
            'name': 'Block A1', 'code': 'A1D',
            'afdeling_id': cls.afdeling.id,
            'area_ha_total': 10.0, 'area_ha_planted': 9.0,
        })
        cls.block2 = cls.env['estate.block'].create({
            'name': 'Block A2', 'code': 'A2D',
            'afdeling_id': cls.afdeling.id,
            'area_ha_total': 12.0, 'area_ha_planted': 8.0,
        })

    def test_create_revenue_distribution(self):
        """Test basic revenue distribution creation."""
        dist = self.RevenueDist.create({
            'block_id': self.block.id,
            'weight_kg': 5000.0,
            'revenue_amount': 14250000.0,
        })
        self.assertTrue(dist.id)
        self.assertEqual(dist.weight_kg, 5000.0)
        self.assertEqual(dist.revenue_amount, 14250000.0)
        self.assertEqual(dist.state, 'draft')

    def test_revenue_distribution_with_invoice(self):
        """Test revenue distribution linked to sales.invoice."""
        partner = self.env['res.partner'].create({'name': 'PT Mill Dist'})
        mill = self.env['sales.mill'].create({
            'partner_id': partner.id,
            'pricing_basis': 'market',
        })
        invoice = self.env['sales.invoice'].create({
            'mill_id': mill.id,
            'period_start': '2025-07-01',
            'period_end': '2025-07-31',
        })
        dist = self.RevenueDist.create({
            'invoice_id': invoice.id,
            'block_id': self.block.id,
            'weight_kg': 3000.0,
            'revenue_amount': 8550000.0,
        })
        self.assertEqual(dist.invoice_id, invoice)

    def test_revenue_distribution_workflow(self):
        """Test draft → posted workflow."""
        dist = self.RevenueDist.create({
            'block_id': self.block.id,
            'weight_kg': 2000.0,
            'revenue_amount': 5700000.0,
        })
        self.assertEqual(dist.state, 'draft')
        dist.action_post()
        self.assertEqual(dist.state, 'posted')

    def test_revenue_distribution_multi_create(self):
        """Test batch creation of revenue distributions."""
        dists = self.RevenueDist.create([
            {
                'block_id': self.block.id,
                'weight_kg': 4000.0,
                'revenue_amount': 11400000.0,
            },
            {
                'block_id': self.block2.id,
                'weight_kg': 6000.0,
                'revenue_amount': 17100000.0,
            },
        ])
        self.assertEqual(len(dists), 2)
        self.assertEqual(dists[0].weight_kg, 4000.0)
        self.assertEqual(dists[1].weight_kg, 6000.0)

    def test_auto_distribute_pro_rata(self):
        """Test auto-distribute revenue pro-rata by block weights."""
        partner = self.env['res.partner'].create({'name': 'PT Mill ProRata'})
        mill = self.env['sales.mill'].create({
            'partner_id': partner.id,
            'pricing_basis': 'market',
        })
        invoice = self.env['sales.invoice'].create({
            'mill_id': mill.id,
            'period_start': '2025-07-01',
            'period_end': '2025-07-31',
        })
        # Total revenue = 10,000,000
        # Block A: 3000 kg, Block B: 7000 kg → total = 10000 kg
        # A gets 30%, B gets 70%
        lines = self.RevenueDist.create([
            {'block_id': self.block.id, 'weight_kg': 3000.0},
            {'block_id': self.block2.id, 'weight_kg': 7000.0},
        ])
        lines.write({'invoice_id': invoice.id})
        invoice.write({'line_amount': 10000000.0})

        # Manually trigger distribution
        lines.action_compute_revenue()

        # 30% of 10,000,000 = 3,000,000
        self.assertAlmostEqual(lines[0].revenue_amount, 3000000.0, places=2)
        # 70% of 10,000,000 = 7,000,000
        self.assertAlmostEqual(lines[1].revenue_amount, 7000000.0, places=2)