# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestPlasmaFarmer(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Farmer = self.env['plasma.farmer']
        self.Koperasi = self.env['plasma.koperasi']

    def test_01_create_farmer(self):
        farmer = self.Farmer.create({
            'name': 'Petani 1', 'nik': '1234567890', 'stdb': 'STDB-001',
        })
        self.assertTrue(farmer.id)
        self.assertEqual(farmer.name, 'Petani 1')

    def test_02_create_koperasi(self):
        kop = self.Koperasi.create({'name': 'Kop Test', 'code': 'KOP-01'})
        self.assertTrue(kop.id)

    def test_03_farmer_in_koperasi(self):
        kop = self.Koperasi.create({'name': 'Kop A', 'code': 'KOP-A'})
        farmer = self.Farmer.create({
            'name': 'Petani 2', 'nik': '9876543210', 'koperasi_id': kop.id,
        })
        self.assertEqual(farmer.koperasi_id, kop)
