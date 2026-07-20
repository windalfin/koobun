# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestNursery(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Batch = self.env['nursery.batch']
        self.Culling = self.env['nursery.culling']
        self.Transfer = self.env['nursery.transfer']
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']

        self.estate = self.Estate.create({'name': 'Test', 'code': 'TE'})
        self.afdeling = self.Afdeling.create({
            'name': 'Afd. A', 'code': 'A', 'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': self.afdeling.id,
        })

    def test_01_create_batch(self):
        batch = self.Batch.create({
            'name': 'Batch-2025-001',
            'variety': 'DxP Simalungun',
            'source': 'PPKS Marihat',
            'quantity_received': 1000,
        })
        self.assertTrue(batch.id)
        self.assertEqual(batch.stage, 'pre_nursery')

    def test_02_advance_stage(self):
        batch = self.Batch.create({
            'name': 'Batch-2025-002',
            'variety': 'Tenera',
            'source': 'Socfindo',
            'quantity_received': 500,
        })
        batch.action_advance_stage()
        self.assertEqual(batch.stage, 'main_nursery')
        batch.action_advance_stage()
        self.assertEqual(batch.stage, 'ready_transfer')

    def test_03_create_culling(self):
        batch = self.Batch.create({
            'name': 'Batch-Cull', 'variety': 'DxP', 'source': 'PPKS',
            'quantity_received': 100,
        })
        cull = self.Culling.create({
            'batch_id': batch.id,
            'quantity': 10,
            'reason': 'abnormal_growth',
            'description': 'Stunted growth observed',
        })
        self.assertTrue(cull.id)
        self.assertEqual(cull.quantity, 10)

    def test_04_create_transfer(self):
        batch = self.Batch.create({
            'name': 'Batch-Transfer', 'variety': 'DxP', 'source': 'PPKS',
            'quantity_received': 200,
        })
        transfer = self.Transfer.create({
            'batch_id': batch.id,
            'block_id': self.block.id,
            'quantity': 150,
        })
        self.assertTrue(transfer.id)
        self.assertEqual(transfer.state, 'draft')
        transfer.action_confirm()
        self.assertEqual(transfer.state, 'confirmed')
        transfer.action_complete()
        self.assertEqual(transfer.state, 'completed')
        self.assertEqual(batch.stage, 'transferred')
