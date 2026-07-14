# -*- coding: utf-8 -*-
from datetime import date
from odoo.tests.common import TransactionCase


class TestPeriodClose(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Checklist = cls.env['gcg.period.close.checklist']
        cls.ChecklistItem = cls.env['gcg.period.close.item']
        cls.ResUsers = cls.env['res.users']

        cls.test_user = cls.ResUsers.create({
            'name': 'Test Verifier',
            'login': 'test_verifier@example.com',
        })

        cls.period_start = date(2025, 1, 1)
        cls.period_end = date(2025, 1, 31)

    def test_01_create_checklist_with_items(self):
        """Test creating a checklist with items."""
        checklist = self.Checklist.create({
            'name': 'January 2025 Month-End Close',
            'period_start': self.period_start,
            'period_end': self.period_end,
            'item_ids': [
                (0, 0, {
                    'sequence': 1,
                    'description': 'Verify all BPB are approved',
                    'check_type': 'manual',
                }),
                (0, 0, {
                    'sequence': 2,
                    'description': 'Verify GL balances tie to sub-ledgers',
                    'check_type': 'system',
                    'model_to_check': 'account.move.line',
                    'domain_filter': "[('date', '<=', '2025-01-31')]",
                }),
            ],
        })
        self.assertTrue(checklist.id)
        self.assertEqual(checklist.state, 'draft')
        self.assertEqual(len(checklist.item_ids), 2)
        self.assertEqual(checklist.period_start, self.period_start)
        self.assertEqual(checklist.period_end, self.period_end)

    def test_02_checklist_lifecycle(self):
        """Test checklist state transitions."""
        checklist = self.Checklist.create({
            'name': 'Lifecycle Test',
            'period_start': self.period_start,
            'period_end': self.period_end,
        })
        self.assertEqual(checklist.state, 'draft')

        checklist.action_start()
        self.assertEqual(checklist.state, 'in_progress')

        checklist.action_complete()
        self.assertEqual(checklist.state, 'completed')

        checklist.action_lock()
        self.assertEqual(checklist.state, 'locked')

    def test_03_checklist_item_verification(self):
        """Test verifying a checklist item."""
        checklist = self.Checklist.create({
            'name': 'Verification Test',
            'period_start': self.period_start,
            'period_end': self.period_end,
            'item_ids': [
                (0, 0, {
                    'sequence': 1,
                    'description': 'Check bank reconciliation',
                    'check_type': 'manual',
                }),
            ],
        })
        item = checklist.item_ids[0]
        self.assertFalse(item.is_compliant)

        item.write({
            'is_compliant': True,
            'actual_result': 'Bank rec ties out',
            'verified_by': self.test_user.id,
            'verified_at': '2025-02-01 10:00:00',
        })
        self.assertTrue(item.is_compliant)
        self.assertEqual(item.actual_result, 'Bank rec ties out')
        self.assertEqual(item.verified_by, self.test_user)

    def test_04_item_ondelete_cascade(self):
        """Test that deleting a checklist deletes its items."""
        checklist = self.Checklist.create({
            'name': 'Cascade Test',
            'period_start': self.period_start,
            'period_end': self.period_end,
            'item_ids': [
                (0, 0, {
                    'sequence': 1,
                    'description': 'Test item',
                    'check_type': 'manual',
                }),
            ],
        })
        item_id = checklist.item_ids[0].id
        checklist.unlink()

        # Item should be cascade-deleted
        item = self.ChecklistItem.search([('id', '=', item_id)])
        self.assertEqual(len(item), 0)

    def test_05_item_expected_result(self):
        """Test setting expected result on a checklist item."""
        checklist = self.Checklist.create({
            'name': 'Expected Result Test',
            'period_start': self.period_start,
            'period_end': self.period_end,
            'item_ids': [
                (0, 0, {
                    'sequence': 1,
                    'description': 'Check total harvest volume',
                    'check_type': 'system',
                    'expected_result': 'Total >= 100 tons for the period',
                }),
            ],
        })
        item = checklist.item_ids[0]
        self.assertEqual(item.expected_result, 'Total >= 100 tons for the period')

    def test_06_checklist_item_check_types(self):
        """Test that both check types are accepted."""
        for check_type in ('manual', 'system'):
            checklist = self.Checklist.create({
                'name': f'Check Type Test — {check_type}',
                'period_start': self.period_start,
                'period_end': self.period_end,
                'item_ids': [
                    (0, 0, {
                        'sequence': 1,
                        'description': f'Test {check_type}',
                        'check_type': check_type,
                    }),
                ],
            })
            self.assertEqual(checklist.item_ids[0].check_type, check_type)

    def test_07_multiple_items_sequencing(self):
        """Test that items maintain their sequence order."""
        checklist = self.Checklist.create({
            'name': 'Sequence Test',
            'period_start': self.period_start,
            'period_end': self.period_end,
            'item_ids': [
                (0, 0, {'sequence': 30, 'description': 'Third', 'check_type': 'manual'}),
                (0, 0, {'sequence': 10, 'description': 'First', 'check_type': 'manual'}),
                (0, 0, {'sequence': 20, 'description': 'Second', 'check_type': 'manual'}),
            ],
        })
        descriptions = checklist.item_ids.sorted('sequence').mapped('description')
        self.assertEqual(descriptions, ['First', 'Second', 'Third'])
