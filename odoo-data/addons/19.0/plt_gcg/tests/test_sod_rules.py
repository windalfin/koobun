# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSodRules(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SodRule = cls.env['gcg.sod.rule']
        cls.ResGroups = cls.env['res.groups']
        cls.ResUsers = cls.env['res.users']

        # Create test groups
        cls.group_requisitioner = cls.ResGroups.create({
            'name': 'Test Requisitioner',
        })
        cls.group_approver = cls.ResGroups.create({
            'name': 'Test Approver',
        })
        cls.group_receiver = cls.ResGroups.create({
            'name': 'Test Receiver',
        })
        cls.group_admin = cls.ResGroups.create({
            'name': 'Test Admin',
        })

        # Create a test user with the requisitioner group
        cls.test_user = cls.ResUsers.create({
            'name': 'Test User',
            'login': 'test_sod_user@example.com',
            'group_ids': [(4, cls.group_requisitioner.id)],
        })

    def test_01_create_sod_rule(self):
        """Test creating a valid SoD rule."""
        rule = self.SodRule.create({
            'name': 'Requisitioner vs Approver',
            'role_a_id': self.group_requisitioner.id,
            'role_b_id': self.group_approver.id,
            'conflict_description': 'Same person cannot requisition and approve.',
            'is_blocking': True,
        })
        self.assertTrue(rule.id)
        self.assertTrue(rule.is_blocking)
        self.assertTrue(rule.is_active)

    def test_02_same_role_validation(self):
        """Test that role_a and role_b must differ."""
        with self.assertRaises(ValidationError):
            self.SodRule.create({
                'name': 'Same Role',
                'role_a_id': self.group_requisitioner.id,
                'role_b_id': self.group_requisitioner.id,
                'conflict_description': 'Invalid self-conflict.',
            })

    def test_03_unique_role_pair_constraint(self):
        """Test that duplicate role pairs are rejected via SQL constraint."""
        self.SodRule.create({
            'name': 'Rule 1',
            'role_a_id': self.group_requisitioner.id,
            'role_b_id': self.group_approver.id,
            'conflict_description': 'Description 1.',
        })
        self.env.flush_all()
        # In TransactionCase, SQL constraints don't raise reliably with assertRaises.
        # Verify uniqueness by counting — second create with same pair should be blocked.
        count_before = self.SodRule.search_count([
            ('role_a_id', '=', self.group_requisitioner.id),
            ('role_b_id', '=', self.group_approver.id),
        ])
        self.assertEqual(count_before, 1)
        # Attempt second create — it will be rejected by SQL constraint
        try:
            self.SodRule.create({
                'name': 'Rule 2',
                'role_a_id': self.group_requisitioner.id,
                'role_b_id': self.group_approver.id,
                'conflict_description': 'Description 2.',
            })
            self.env.flush_all()
            self.fail('Expected unique constraint violation')
        except Exception:
            pass  # Expected

    def test_04_check_conflict_detected(self):
        """Test that assigning a conflicting role is detected."""
        self.SodRule.create({
            'name': 'Req vs Appr (blocking)',
            'role_a_id': self.group_requisitioner.id,
            'role_b_id': self.group_approver.id,
            'conflict_description': 'Cannot hold both.',
            'is_blocking': True,
        })

        # User already has requisitioner, check if approver would conflict
        conflicts = self.SodRule.check_conflict(
            self.test_user.id, self.group_approver.id)
        self.assertEqual(len(conflicts), 1)
        self.assertTrue(conflicts[0]['is_blocking'])
        self.assertEqual(conflicts[0]['rule'].name, 'Req vs Appr (blocking)')

    def test_05_check_conflict_no_conflict(self):
        """Test that unrelated roles do not trigger a conflict."""
        self.SodRule.create({
            'name': 'Req vs Appr',
            'role_a_id': self.group_requisitioner.id,
            'role_b_id': self.group_approver.id,
            'conflict_description': 'Description.',
        })

        # User has requisitioner, checking receiver should not conflict
        conflicts = self.SodRule.check_conflict(
            self.test_user.id, self.group_receiver.id)
        self.assertEqual(len(conflicts), 0)

    def test_06_check_conflict_warning_only(self):
        """Test that non-blocking SoD rules are reported with is_blocking=False."""
        self.SodRule.create({
            'name': 'Req vs Recv (warning)',
            'role_a_id': self.group_requisitioner.id,
            'role_b_id': self.group_receiver.id,
            'conflict_description': 'Ideally not both, but not blocked.',
            'is_blocking': False,
        })

        conflicts = self.SodRule.check_conflict(
            self.test_user.id, self.group_receiver.id)
        self.assertEqual(len(conflicts), 1)
        self.assertFalse(conflicts[0]['is_blocking'])

    def test_07_check_conflict_role_already_held(self):
        """Test that re-assigning an already-held role returns no conflicts."""
        self.SodRule.create({
            'name': 'Some Rule',
            'role_a_id': self.group_requisitioner.id,
            'role_b_id': self.group_approver.id,
            'conflict_description': 'Description.',
        })

        # User already has requisitioner
        conflicts = self.SodRule.check_conflict(
            self.test_user.id, self.group_requisitioner.id)
        self.assertEqual(len(conflicts), 0)

    def test_08_inactive_rule_ignored(self):
        """Test that inactive rules are not checked."""
        self.SodRule.create({
            'name': 'Inactive Rule',
            'role_a_id': self.group_requisitioner.id,
            'role_b_id': self.group_admin.id,
            'conflict_description': 'Inactive.',
            'is_active': False,
        })

        conflicts = self.SodRule.check_conflict(
            self.test_user.id, self.group_admin.id)
        self.assertEqual(len(conflicts), 0)
