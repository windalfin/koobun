# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestWhistleblowing(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Whistleblowing = cls.env['gcg.whistleblowing']
        cls.IrSequence = cls.env['ir.sequence']
        cls.IrAttachment = cls.env['ir.attachment']
        cls.ResUsers = cls.env['res.users']

        # Create test user
        cls.test_user = cls.ResUsers.create({
            'name': 'Test Investigator',
            'login': 'test_wb_investigator@example.com',
        })

        # Ensure a sequence exists for case numbers
        existing_seq = cls.IrSequence.search([
            ('code', '=', 'gcg.whistleblowing.case'),
        ], limit=1)
        if not existing_seq:
            cls.IrSequence.create({
                'name': 'Whistleblowing Case',
                'code': 'gcg.whistleblowing.case',
                'prefix': 'WBS-%(year)s-%(month)s-',
                'padding': 3,
                'number_next': 1,
                'number_increment': 1,
            })

    def test_01_create_basic_case(self):
        """Test creating a basic whistleblowing case."""
        case = self.Whistleblowing.create({
            'subject': 'Suspected procurement irregularity',
            'description': 'Detailed description of the concern.',
            'channel': 'web_form',
            'reporter_name': 'John Doe',
            'reporter_email': 'john@example.com',
        })
        self.assertTrue(case.id)
        self.assertEqual(case.status, 'submitted')
        self.assertNotEqual(case.case_number, 'New')
        self.assertTrue(case.case_number.startswith('WBS-'))

    def test_02_anonymous_case(self):
        """Test creating an anonymous whistleblowing case."""
        case = self.Whistleblowing.create({
            'subject': 'Anonymous report',
            'description': 'Anonymous description.',
            'is_anonymous': True,
            'channel': 'web_form',
        })
        self.assertTrue(case.is_anonymous)
        self.assertFalse(case.reporter_name)
        self.assertFalse(case.reporter_email)

    def test_03_case_lifecycle(self):
        """Test the full case lifecycle."""
        case = self.Whistleblowing.create({
            'subject': 'Lifecycle test',
            'description': 'Testing lifecycle.',
            'channel': 'hotline',
        })
        self.assertEqual(case.status, 'submitted')

        case.action_investigate()
        self.assertEqual(case.status, 'under_investigation')

        case.action_resolve()
        self.assertEqual(case.status, 'resolved')
        self.assertIsNotNone(case.resolution_date)

        case.action_close()
        self.assertEqual(case.status, 'closed')

    def test_04_assignment(self):
        """Test assigning a case to an investigator."""
        case = self.Whistleblowing.create({
            'subject': 'Assignment test',
            'description': 'Testing assignment.',
            'assigned_to': self.test_user.id,
        })
        self.assertEqual(case.assigned_to, self.test_user)

    def test_05_case_number_format(self):
        """Test that case numbers follow the expected format."""
        case = self.Whistleblowing.create({
            'subject': 'Format test',
            'description': 'Testing case number format.',
        })
        case_number = case.case_number
        # Expected format: WBS-YYYY-MM-NNN
        self.assertTrue(case_number.startswith('WBS-'))
        parts = case_number.split('-')
        self.assertEqual(len(parts), 4)  # WBS, YYYY, MM, NNN
        self.assertEqual(len(parts[0]), 3)  # WBS
        self.assertEqual(len(parts[1]), 4)  # year
        self.assertEqual(len(parts[2]), 2)  # month

    def test_06_resolution_fields(self):
        """Test resolution note and date."""
        case = self.Whistleblowing.create({
            'subject': 'Resolution test',
            'description': 'Testing resolution.',
        })
        case.action_investigate()
        case.resolution = 'Investigated thoroughly, no misconduct found.'
        case.action_resolve()
        self.assertTrue(case.resolution)
        self.assertIsNotNone(case.resolution_date)

    def test_07_all_channels(self):
        """Test that all channel options are accepted."""
        channels = ['web_form', 'email', 'sms', 'in_person', 'hotline']
        for channel in channels:
            case = self.Whistleblowing.create({
                'subject': f'Channel test — {channel}',
                'description': 'Testing channel.',
                'channel': channel,
            })
            self.assertEqual(case.channel, channel)
