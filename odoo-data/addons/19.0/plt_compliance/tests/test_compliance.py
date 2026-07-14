# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestCompliance(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ISPO = self.env['compliance.ispo_evidence']
        self.EUDR = self.env['compliance.eudr_export']
        self.K3 = self.env['compliance.k3_incident']
        self.Env = self.env['compliance.environmental']
        self.Estate = self.env['estate.estate']
        self.Afdeling = self.env['estate.afdeling']
        self.Block = self.env['estate.block']

        self.estate = self.Estate.create({'name': 'Test', 'code': 'TE'})
        self.afdeling = self.Afdeling.create({'name': 'Afd. A', 'code': 'A', 'estate_id': self.estate.id})
        self.block = self.Block.create({'name': 'Block A1', 'code': 'A1', 'afdeling_id': self.afdeling.id})

    def test_01_create_ispo_evidence(self):
        ev = self.ISPO.create({
            'principle': '1',
            'criterion': '1.1',
            'description': 'HGU document',
        })
        self.assertTrue(ev.id)
        self.assertEqual(ev.status, 'pending')

    def test_02_create_eudr_export(self):
        exp = self.EUDR.create({
            'block_id': self.block.id,
            'geojson_data': '{"type":"Polygon","coordinates":[]}',
        })
        self.assertTrue(exp.id)
        self.assertEqual(exp.status, 'draft')

    def test_03_create_k3_incident(self):
        inc = self.K3.create({
            'incident_type': 'accident',
            'description': 'Slip on wet path',
            'severity': 'minor',
        })
        self.assertTrue(inc.id)
        self.assertEqual(inc.status, 'reported')

    def test_04_create_environmental(self):
        rec = self.Env.create({
            'record_type': 'fire_watch',
            'description': 'No fires detected this week',
        })
        self.assertTrue(rec.id)
        self.assertEqual(rec.status, 'recorded')
