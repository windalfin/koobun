# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestSPBGapDetection(TransactionCase):

    def setUp(self):
        super().setUp()
        self.SPB = self.env['transport.spb']

    def test_check_spb_gap_no_previous(self):
        """Test _check_spb_gap when no previous SPB exists — no gap."""
        spb = self.SPB.create({
            'number': 'SPB-GAP-001',
            'date': '2026-07-14',
        })
        # No previous SPB, should not log any exception
        result = spb._check_spb_gap()
        self.assertFalse(result)  # No gap detected

    def test_check_spb_gap_consecutive(self):
        """Test _check_spb_gap with consecutive SPBs — no gap."""
        spb1 = self.SPB.create({
            'number': 'SPB-CONSEC-001',
            'date': '2026-07-14',
        })
        spb2 = self.SPB.create({
            'number': 'SPB-CONSEC-002',
            'date': '2026-07-14',
        })
        # Previous SPB exists, no gap
        result = spb2._check_spb_gap()
        self.assertFalse(result)

    def test_check_spb_gap_detected(self):
        """Test that gap is detected and logged when SPB-002 has no SPB-001."""
        # Create SPB-001 and SPB-003, skip SPB-002
        self.SPB.create({
            'number': 'SPB-SKP-001',
            'date': '2026-07-14',
        })
        spb3 = self.SPB.create({
            'number': 'SPB-SKP-003',
            'date': '2026-07-14',
        })
        # _check_spb_gap should detect that 002 is missing
        result = spb3._check_spb_gap()
        self.assertTrue(result)  # Gap detected

    def test_check_spb_gap_consecutive_sequence(self):
        """Test gap detection with numeric suffixes."""
        spb1 = self.SPB.create({
            'number': 'SPB-SEQ-001',
            'date': '2026-07-14',
        })
        spb2 = self.SPB.create({
            'number': 'SPB-SEQ-002',
            'date': '2026-07-14',
        })
        spb3 = self.SPB.create({
            'number': 'SPB-SEQ-003',
            'date': '2026-07-14',
        })
        # No gap between 001 → 002 → 003
        result = spb3._check_spb_gap()
        self.assertFalse(result)

    def test_check_spb_gap_log_message(self):
        """Test that gap detection logs a message on the SPB."""
        self.SPB.create({
            'number': 'SPB-LOG-001',
            'date': '2026-07-14',
        })
        spb3 = self.SPB.create({
            'number': 'SPB-LOG-003',
            'date': '2026-07-14',
        })
        spb3._check_spb_gap()
        # A log message should have been posted
        messages = spb3.message_ids.filtered(
            lambda m: 'gap' in m.body.lower() or 'missing' in m.body.lower()
        )
        self.assertTrue(messages, 'Expected gap log message on SPB')