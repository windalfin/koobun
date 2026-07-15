# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestHarvestInspection(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Inspection = self.env['harvest.inspection']
        self.Block = self.env['estate.block']

        # Estate / afdeling / block
        self.estate = self.env['estate.estate'].create({
            'name': 'Test Estate', 'code': 'TST',
        })
        self.afdeling = self.env['estate.afdeling'].create({
            'name': 'Test Afdeling', 'code': 'AFT',
            'estate_id': self.estate.id,
        })
        self.block = self.Block.create({
            'name': 'Test Block', 'code': 'TB1',
            'afdeling_id': self.afdeling.id,
            'area_ha_total': 10.0, 'area_ha_planted': 9.0,
        })
        self.employee = self.env['hr.employee'].search([], limit=1)

    def _skip_if_no_employee(self):
        if not self.employee:
            self.skipTest('No hr.employee found')

    def test_create_inspection_ancak(self):
        """Test basic mutu ancak inspection creation."""
        self._skip_if_no_employee()
        insp = self.Inspection.create({
            'date': '2025-01-15',
            'inspection_type': 'ancak',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'checklist_items': 'Buah mentah, tangkai panjang, brondolan tidak dikutip',
            'score_buah_mentah': 2,
            'score_tangkai_panjang': 1,
            'score_brondolan': 0,
        })
        self.assertTrue(insp.id)
        self.assertEqual(insp.inspection_type, 'ancak')
        self.assertEqual(insp.state, 'draft')
        self.assertEqual(insp.total_score, 3)

    def test_create_inspection_buah(self):
        """Test mutu buah inspection creation."""
        self._skip_if_no_employee()
        insp = self.Inspection.create({
            'date': '2025-01-15',
            'inspection_type': 'buah',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'checklist_items': 'Sortasi, kadar minyak, kadar air',
            'score_buah_mentah': 3,
            'score_tangkai_panjang': 2,
        })
        self.assertEqual(insp.inspection_type, 'buah')
        self.assertEqual(insp.total_score, 5)

    def test_inspection_workflow(self):
        """Test inspection draft → posted workflow."""
        self._skip_if_no_employee()
        insp = self.Inspection.create({
            'date': '2025-01-15',
            'inspection_type': 'ancak',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'checklist_items': 'Check',
            'score_buah_mentah': 1,
        })
        self.assertEqual(insp.state, 'draft')
        insp.action_post()
        self.assertEqual(insp.state, 'posted')

    def test_inspection_total_score_computed(self):
        """Test that total_score is sum of individual scores."""
        self._skip_if_no_employee()
        insp = self.Inspection.create({
            'date': '2025-01-15',
            'inspection_type': 'ancak',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'checklist_items': 'Check',
            'score_buah_mentah': 3,
            'score_tangkai_panjang': 2,
            'score_brondolan': 1,
        })
        self.assertEqual(insp.total_score, 6)

    def test_inspection_result_auto(self):
        """Test that result is computed from total_score."""
        self._skip_if_no_employee()
        insp_good = self.Inspection.create({
            'date': '2025-01-15',
            'inspection_type': 'ancak',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'checklist_items': 'Check',
            'score_buah_mentah': 0,
        })
        self.assertEqual(insp_good.result, 'pass')

        insp_bad = self.Inspection.create({
            'date': '2025-01-15',
            'inspection_type': 'ancak',
            'mandor_id': self.employee.id,
            'block_id': self.block.id,
            'checklist_items': 'Check',
            'score_buah_mentah': 5,
        })
        self.assertEqual(insp_bad.result, 'fail')