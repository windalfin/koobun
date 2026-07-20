# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAuthorityMatrix(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AuthorityMatrix = cls.env['gcg.authority.matrix']
        cls.ResGroups = cls.env['res.groups']
        cls.ResCurrency = cls.env.ref('base.USD')

        # Create test groups
        cls.group_mgr = cls.ResGroups.create({
            'name': 'Test Manager',
        })
        cls.group_dir = cls.ResGroups.create({
            'name': 'Test Director',
        })

    def test_01_create_basic_authority_row(self):
        """Test creating a basic authority matrix row."""
        row = self.AuthorityMatrix.create({
            'name': 'BPB < 5M IDR — Asisten',
            'document_model': 'upkeep.bpb',
            'document_type_name': 'Bukti Permintaan Barang',
            'min_value': 0,
            'max_value': 5000000,
            'approver_role_id': self.group_mgr.id,
        })
        self.assertTrue(row.id)
        self.assertEqual(row.document_model, 'upkeep.bpb')
        self.assertTrue(row.is_active)
        self.assertEqual(row.version, 1)

    def test_02_value_range_validation(self):
        """Test that min_value must be <= max_value."""
        with self.assertRaises(ValidationError):
            self.AuthorityMatrix.create({
                'name': 'Invalid Range',
                'document_model': 'upkeep.bpb',
                'min_value': 10000000,
                'max_value': 5000000,
                'approver_role_id': self.group_mgr.id,
            })

    def test_03_distinct_approver_roles(self):
        """Test that primary and secondary approver roles must differ."""
        with self.assertRaises(ValidationError):
            self.AuthorityMatrix.create({
                'name': 'Same Approver',
                'document_model': 'upkeep.bpb',
                'min_value': 0,
                'max_value': 5000000,
                'approver_role_id': self.group_mgr.id,
                'approver_role_2_id': self.group_mgr.id,
            })

    def test_04_get_approvers_for_value_matching(self):
        """Test get_approvers_for_value returns correct matching rows."""
        self.AuthorityMatrix.create({
            'name': 'Low Band — Mgr',
            'document_model': 'upkeep.bpb',
            'min_value': 0,
            'max_value': 5000000,
            'approver_role_id': self.group_mgr.id,
            'sequence': 1,
        })
        self.AuthorityMatrix.create({
            'name': 'High Band — Dir',
            'document_model': 'upkeep.bpb',
            'min_value': 5000001,
            'max_value': 50000000,
            'approver_role_id': self.group_dir.id,
            'sequence': 2,
        })

        # Low value should match first row only
        low_matches = self.AuthorityMatrix.get_approvers_for_value(
            'upkeep.bpb', 3000000)
        self.assertEqual(len(low_matches), 1)
        self.assertEqual(low_matches.name, 'Low Band — Mgr')

        # High value should match second row only
        high_matches = self.AuthorityMatrix.get_approvers_for_value(
            'upkeep.bpb', 10000000)
        self.assertEqual(len(high_matches), 1)
        self.assertEqual(high_matches.name, 'High Band — Dir')

    def test_05_get_approvers_for_value_no_match(self):
        """Test get_approvers_for_value returns empty when no rows."""
        matches = self.AuthorityMatrix.get_approvers_for_value(
            'nonexistent.model', 5000000)
        self.assertEqual(len(matches), 0)

    def test_06_get_approvers_for_value_inactive_filter(self):
        """Test that inactive rows are excluded."""
        row = self.AuthorityMatrix.create({
            'name': 'Inactive Row',
            'document_model': 'upkeep.bpb',
            'min_value': 0,
            'max_value': 5000000,
            'approver_role_id': self.group_mgr.id,
            'is_active': False,
        })
        matches = self.AuthorityMatrix.get_approvers_for_value(
            'upkeep.bpb', 3000000)
        self.assertEqual(len(matches), 0)

    def test_07_authority_matrix_no_value_bands(self):
        """Test that rows without value bounds match any amount."""
        self.AuthorityMatrix.create({
            'name': 'No Bounds',
            'document_model': 'upkeep.bpb',
            'approver_role_id': self.group_mgr.id,
        })
        matches = self.AuthorityMatrix.get_approvers_for_value(
            'upkeep.bpb', 500000000)
        self.assertEqual(len(matches), 1)
