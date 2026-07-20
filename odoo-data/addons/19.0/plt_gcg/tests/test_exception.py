# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestException(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Exception = cls.env['gcg.exception']
        cls.ResUsers = cls.env['res.users']

        cls.test_user = cls.ResUsers.create({
            'name': 'Test Investigator',
            'login': 'test_investigator@example.com',
        })

    def test_01_create_exception(self):
        """Test creating a basic exception record."""
        exc = self.Exception.create({
            'name': 'Weighbridge variance detected',
            'exception_type': 'weighbridge_variance',
            'severity': 'high',
            'document_reference': 'WB-2025-001',
        })
        self.assertTrue(exc.id)
        self.assertEqual(exc.status, 'open')
        self.assertEqual(exc.severity, 'high')
        self.assertIsNotNone(exc.created_at)

    def test_02_exception_lifecycle(self):
        """Test the full exception lifecycle: open → review → resolve."""
        exc = self.Exception.create({
            'name': 'Test lifecycle',
            'exception_type': 'other',
            'severity': 'medium',
        })
        self.assertEqual(exc.status, 'open')

        exc.action_review()
        self.assertEqual(exc.status, 'in_review')

        exc.action_resolve()
        self.assertEqual(exc.status, 'resolved')

    def test_03_exception_dismiss(self):
        """Test dismissing an exception."""
        exc = self.Exception.create({
            'name': 'Dismiss test',
            'exception_type': 'other',
            'severity': 'low',
        })
        exc.action_dismiss()
        self.assertEqual(exc.status, 'dismissed')

    def test_04_severity_defaults_to_medium(self):
        """Test that severity defaults to 'medium'."""
        exc = self.Exception.create({
            'name': 'Default severity test',
            'exception_type': 'other',
        })
        self.assertEqual(exc.severity, 'medium')

    def test_05_exception_all_types(self):
        """Test that all exception types are valid."""
        valid_types = [
            'weighbridge_variance', 'restan_over24h', 'rotation_over_target',
            'hk_anomaly', 'chemical_variance', 'spb_gap', 'premi_outlier',
            'master_data_change', 'override', 'other',
        ]
        for exc_type in valid_types:
            exc = self.Exception.create({
                'name': f'Test {exc_type}',
                'exception_type': exc_type,
            })
            self.assertEqual(exc.exception_type, exc_type)

    def test_06_assignment(self):
        """Test assigning an exception to a user."""
        exc = self.Exception.create({
            'name': 'Assigned exception',
            'exception_type': 'other',
            'assigned_to': self.test_user.id,
        })
        self.assertEqual(exc.assigned_to, self.test_user)

    def test_07_document_reference(self):
        """Test linking an exception to a source document."""
        exc = self.Exception.create({
            'name': 'Referenced exception',
            'exception_type': 'spb_gap',
            'document_reference': 'SPB-2025-00042',
            'document_model': 'upkeep.spb',
            'document_id': 42,
        })
        self.assertEqual(exc.document_reference, 'SPB-2025-00042')
        self.assertEqual(exc.document_model, 'upkeep.spb')
        self.assertEqual(exc.document_id, 42)

    def test_08_resolution_note(self):
        """Test adding a resolution note."""
        exc = self.Exception.create({
            'name': 'Resolution test',
            'exception_type': 'other',
        })
        exc.action_resolve()
        exc.resolution_note = 'Investigated and found to be within tolerance.'
        self.assertIn('tolerance', exc.resolution_note)
