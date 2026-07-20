# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestLandDocument(TransactionCase):

    def setUp(self):
        super().setUp()
        self.LandDoc = self.env['estate.land.document']

    def test_create_land_document(self):
        """Test basic land document creation."""
        doc = self.LandDoc.create({
            'name': 'HGU Test',
            'document_type': 'hgu',
            'number': 'HGU-001/2024',
            'holder_name': 'PT Kebun Test',
            'area_ha': 500.0,
            'issue_date': '2024-01-01',
            'expiry_date': '2054-01-01',
        })
        self.assertTrue(doc.id)
        self.assertEqual(doc.state, 'active')
        self.assertGreater(doc.days_to_expiry, 0)

    def test_expiry_alert_computation(self):
        """Test that expiry alerts are correctly computed."""
        today = date.today()

        # Far future: no alert
        doc_far = self.LandDoc.create({
            'name': 'Far Future',
            'document_type': 'hgu',
            'number': 'FAR-001',
            'holder_name': 'PT Kebun',
            'expiry_date': today + timedelta(days=365),
        })
        self.assertEqual(doc_far.expiry_alert, 'none')

        # 90 days: alert
        doc_90 = self.LandDoc.create({
            'name': '90 Days',
            'document_type': 'hgu',
            'number': '90D-001',
            'holder_name': 'PT Kebun',
            'expiry_date': today + timedelta(days=85),
        })
        self.assertEqual(doc_90.expiry_alert, '90days')

        # 60 days: alert
        doc_60 = self.LandDoc.create({
            'name': '60 Days',
            'document_type': 'hgu',
            'number': '60D-001',
            'holder_name': 'PT Kebun',
            'expiry_date': today + timedelta(days=50),
        })
        self.assertEqual(doc_60.expiry_alert, '60days')

        # 30 days: alert
        doc_30 = self.LandDoc.create({
            'name': '30 Days',
            'document_type': 'hgu',
            'number': '30D-001',
            'holder_name': 'PT Kebun',
            'expiry_date': today + timedelta(days=20),
        })
        self.assertEqual(doc_30.expiry_alert, '30days')

        # Expired
        doc_expired = self.LandDoc.create({
            'name': 'Expired',
            'document_type': 'hgu',
            'number': 'EXP-001',
            'holder_name': 'PT Kebun',
            'expiry_date': today - timedelta(days=1),
        })
        self.assertEqual(doc_expired.expiry_alert, 'expired')

    def test_days_to_expiry(self):
        """Test days_to_expiry computation."""
        today = date.today()
        doc = self.LandDoc.create({
            'name': 'Days Test',
            'document_type': 'hgu',
            'number': 'DAY-001',
            'holder_name': 'PT Kebun',
            'expiry_date': today + timedelta(days=100),
        })
        self.assertAlmostEqual(doc.days_to_expiry, 100, delta=1)

    def test_days_to_expiry_no_date(self):
        """Test days_to_expiry when no expiry date set."""
        doc = self.LandDoc.create({
            'name': 'No Expiry',
            'document_type': 'hgu',
            'number': 'NEX-001',
            'holder_name': 'PT Kebun',
        })
        self.assertEqual(doc.days_to_expiry, 999)

    def test_name_required(self):
        """Test that name is required."""
        with self.assertRaises(Exception):
            self.LandDoc.create({
                'document_type': 'hgu',
                'number': 'NOR-001',
                'holder_name': 'PT Kebun',
            })

    def test_document_type_required(self):
        """Test that document_type is required."""
        with self.assertRaises(Exception):
            self.LandDoc.create({
                'name': 'No Type',
                'number': 'NTY-001',
                'holder_name': 'PT Kebun',
            })

    def test_holder_name_consistency_warning(self):
        """Test that holder name inconsistency triggers validation error."""
        self.LandDoc.create({
            'name': 'Doc 1',
            'document_type': 'hgu',
            'number': 'HGU-001',
            'holder_name': 'PT Kebun Jaya',
            'area_ha': 100.0,
        })
        # Same document_type but slightly different holder name
        # "PT Kebun Jaya" vs "PT. Kebun Jaya" — similar enough to trigger
        with self.assertRaises(ValidationError):
            self.LandDoc.create({
                'name': 'Doc 2',
                'document_type': 'hgu',
                'number': 'HGU-002',
                'holder_name': 'PT. Kebun Jaya',
                'area_ha': 200.0,
            })

    def test_state_default_active(self):
        """Test default state is active."""
        doc = self.LandDoc.create({
            'name': 'State Test',
            'document_type': 'shm',
            'number': 'SHM-001',
            'holder_name': 'PT Kebun',
        })
        self.assertEqual(doc.state, 'active')
