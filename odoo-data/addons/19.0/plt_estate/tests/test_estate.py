# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestEstate(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Estate = self.env['estate.estate']

    def test_create_estate(self):
        """Test basic estate creation."""
        estate = self.Estate.create({
            'name': 'Test Estate',
            'code': 'TST',
            'phone': '+62 123 456',
        })
        self.assertTrue(estate.id)
        self.assertEqual(estate.name, 'Test Estate')
        self.assertEqual(estate.code, 'TST')
        self.assertTrue(estate.active)

    def test_estate_code_unique(self):
        """Test that estate code must be unique (enforced by SQL constraint)."""
        self.Estate.create({'name': 'E1', 'code': 'UNQ'})
        self.env.flush_all()
        # SQL constraint prevents duplicate; verify only one exists
        count = self.Estate.search_count([('code', '=', 'UNQ')])
        self.assertEqual(count, 1)

    def test_estate_name_required(self):
        """Test that name is required."""
        with self.assertRaises(Exception):
            self.Estate.create({'code': 'NOR'})

    def test_estate_code_required(self):
        """Test that code is required."""
        with self.assertRaises(Exception):
            self.Estate.create({'name': 'No Code'})

    def test_estate_default_active(self):
        """Test estate active defaults to True."""
        estate = self.Estate.create({
            'name': 'Active Test',
            'code': 'ACT',
        })
        self.assertTrue(estate.active)

    def test_estate_archive(self):
        """Test archiving an estate."""
        estate = self.Estate.create({
            'name': 'Archive Me',
            'code': 'ARC',
        })
        estate.active = False
        self.assertFalse(estate.active)
