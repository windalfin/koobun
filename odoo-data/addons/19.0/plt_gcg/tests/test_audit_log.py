# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestAuditLog(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AuditLog = cls.env['gcg.audit.log']

    def test_01_create_audit_log_entry(self):
        """Test creating an audit log entry."""
        entry = self.AuditLog.create({
            'model_name': 'res.partner',
            'record_id': 1,
            'record_name': 'Test Partner',
            'field_name': 'name',
            'old_value': 'Old Name',
            'new_value': 'New Name',
            'transaction_type': 'write',
        })
        self.assertTrue(entry.id)
        self.assertEqual(entry.model_name, 'res.partner')
        self.assertEqual(entry.field_name, 'name')
        self.assertEqual(entry.old_value, 'Old Name')
        self.assertEqual(entry.new_value, 'New Name')
        self.assertEqual(entry.transaction_type, 'write')
        self.assertIsNotNone(entry.changed_at)
        self.assertEqual(entry.changed_by, self.env.user)

    def test_02_log_change_convenience_method(self):
        """Test the log_change convenience method."""
        entry = self.AuditLog.log_change(
            model_name='res.partner',
            record_id=2,
            field_name='email',
            old_value='old@test.com',
            new_value='new@test.com',
            record_name='Partner 2',
            transaction_type='write',
        )
        self.assertTrue(entry.id)
        self.assertEqual(entry.model_name, 'res.partner')
        self.assertEqual(entry.field_name, 'email')

    def test_03_write_blocked_on_existing_record(self):
        """Test that modifying an existing audit log record is forbidden."""
        entry = self.AuditLog.create({
            'model_name': 'res.partner',
            'record_id': 1,
            'field_name': 'name',
            'old_value': 'Old',
            'new_value': 'New',
            'transaction_type': 'write',
        })
        with self.assertRaises(Exception):
            entry.write({'old_value': 'Tampered'})

    def test_04_unlink_blocked_on_existing_record(self):
        """Test that deleting an existing audit log record is forbidden."""
        entry = self.AuditLog.create({
            'model_name': 'res.partner',
            'record_id': 1,
            'field_name': 'name',
            'old_value': 'Old',
            'new_value': 'New',
            'transaction_type': 'write',
        })
        with self.assertRaises(Exception):
            entry.unlink()

    def test_05_noop_write_and_unlink(self):
        """Test that write and unlink on empty recordsets succeed."""
        empty = self.AuditLog.browse()
        self.assertTrue(empty.write({}))  # no-op
        self.assertTrue(empty.unlink())  # no-op

    def test_06_model_name_indexed(self):
        """Test that model_name field has index."""
        field = self.AuditLog._fields.get('model_name')
        self.assertIsNotNone(field)
        self.assertTrue(field.index, "model_name should be indexed")

    def test_07_changed_by_defaults_to_current_user(self):
        """Test that changed_by defaults to the current user."""
        entry = self.AuditLog.create({
            'model_name': 'res.partner',
            'record_id': 1,
            'field_name': 'name',
            'old_value': 'Old',
            'new_value': 'New',
            'transaction_type': 'write',
        })
        self.assertEqual(entry.changed_by, self.env.user)
