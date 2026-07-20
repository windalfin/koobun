# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSalesMill(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SalesMill = cls.env['sales.mill']
        cls.partner = cls.env['res.partner'].create({
            'name': 'PT Mill Test',
        })
        cls.partner2 = cls.env['res.partner'].create({
            'name': 'PT Mill Test 2',
        })

    def test_01_create_mill(self):
        """Test creating a sales mill record."""
        mill = self.SalesMill.create({
            'partner_id': self.partner.id,
            'pricing_basis': 'market',
            'sortasi_rules': 'Max deduction 5%',
            'payment_terms': 'Net 30',
        })
        self.assertTrue(mill.id)
        self.assertEqual(mill.name, 'PT Mill Test')
        self.assertEqual(mill.pricing_basis, 'market')
        self.assertEqual(mill.is_active, True)

    def test_02_duplicate_partner_blocked(self):
        """Test that duplicate partner assignment is blocked."""
        self.SalesMill.create({
            'partner_id': self.partner.id,
            'pricing_basis': 'market',
        })
        with self.assertRaises(ValidationError):
            self.SalesMill.create({
                'partner_id': self.partner.id,
                'pricing_basis': 'contract',
            })

    def test_03_create_mill_without_partner_fails(self):
        """Test that required fields are enforced."""
        with self.assertRaises(Exception):
            self.SalesMill.create({
                'pricing_basis': 'market',
            })

    def test_04_name_related(self):
        """Test that name is derived from partner."""
        mill = self.SalesMill.create({
            'partner_id': self.partner.id,
            'pricing_basis': 'disbun',
        })
        self.assertEqual(mill.name, 'PT Mill Test')
        self.partner.name = 'PT Mill Renamed'
        self.assertEqual(mill.name, 'PT Mill Renamed')


class TestSalesTbsPrice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TbsPrice = cls.env['sales.tbs_price']

    def test_05_create_tbs_price(self):
        """Test creating a TBS price record."""
        price = self.TbsPrice.create({
            'name': 'Market Price July 2025',
            'price_type': 'market',
            'age_band_min': 3,
            'age_band_max': 8,
            'rendemen_pct': 22.5,
            'indeks_k': 0.95,
            'price_per_kg': 2850.00,
            'cp_oil_reference': 13500.00,
            'date_from': '2025-07-01',
            'date_to': '2025-07-31',
        })
        self.assertTrue(price.id)
        self.assertEqual(price.state, 'draft')

    def test_06_approve_workflow(self):
        """Test approve workflow."""
        price = self.TbsPrice.create({
            'name': 'Test Price',
            'price_type': 'market',
            'age_band_min': 3,
            'age_band_max': 8,
            'price_per_kg': 1000.00,
            'date_from': '2025-07-01',
            'date_to': '2025-07-31',
        })
        self.assertEqual(price.state, 'draft')
        price.action_approve()
        self.assertEqual(price.state, 'approved')
        price.action_expire()
        self.assertEqual(price.state, 'expired')
        price.action_draft()
        self.assertEqual(price.state, 'draft')

    def test_07_invalid_dates_raises(self):
        """Test that date_from > date_to is rejected."""
        with self.assertRaises(ValidationError):
            self.TbsPrice.create({
                'name': 'Invalid Dates',
                'price_type': 'market',
                'age_band_min': 3,
                'age_band_max': 8,
                'price_per_kg': 1000.00,
                'date_from': '2025-07-31',
                'date_to': '2025-07-01',
            })

    def test_08_invalid_age_band_raises(self):
        """Test that age_band_min > age_band_max is rejected."""
        with self.assertRaises(ValidationError):
            self.TbsPrice.create({
                'name': 'Invalid Age Band',
                'price_type': 'market',
                'age_band_min': 10,
                'age_band_max': 5,
                'price_per_kg': 1000.00,
                'date_from': '2025-07-01',
                'date_to': '2025-07-31',
            })

    def test_09_negative_price_raises(self):
        """Test that negative price_per_kg is rejected."""
        with self.assertRaises(ValidationError):
            self.TbsPrice.create({
                'name': 'Negative Price',
                'price_type': 'market',
                'age_band_min': 3,
                'age_band_max': 8,
                'price_per_kg': -100.00,
                'date_from': '2025-07-01',
                'date_to': '2025-07-31',
            })


class TestSalesMillReception(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MillReception = cls.env['sales.mill_reception']
        # Create prerequisite records
        cls.estate = cls.env['estate.estate'].create({'name': 'Test', 'code': 'TE'})
        cls.afdeling = cls.env['estate.afdeling'].create({
            'name': 'Afd. A', 'code': 'A', 'estate_id': cls.estate.id,
        })
        cls.block = cls.env['estate.block'].create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': cls.afdeling.id,
        })
        cls.tph = cls.env['estate.tph'].create({
            'name': 'TPH-01',
            'code': 'TPH-01', 'block_id': cls.block.id,
        })
        cls.spb = cls.env['transport.spb'].create({
            'number': 'SPB-TEST-001',
            'date': '2025-07-15',
            'block_ids': [(4, cls.block.id)],
            'tph_ids': [(4, cls.tph.id)],
            'janjang_count': 100,
        })

    def test_10_create_mill_reception(self):
        """Test creating a mill reception record."""
        reception = self.MillReception.create({
            'spb_id': self.spb.id,
            'gross_kg': 5000.00,
            'sortasi_deduction_kg': 150.00,
            'deduction_reasons': 'buah mentah: 100kg, tangkai panjang: 50kg',
            'mill_doc_ref': 'WB-2025-0001',
            'reception_date': '2025-07-15',
        })
        self.assertTrue(reception.id)
        self.assertAlmostEqual(reception.sortasi_deduction_pct, 3.0)
        self.assertAlmostEqual(reception.accepted_net_kg, 4850.00)

    def test_11_deduction_pct_zero_gross(self):
        """Test deduction pct is 0 when gross is 0."""
        reception = self.MillReception.create({
            'spb_id': self.spb.id,
            'gross_kg': 0.00,
            'reception_date': '2025-07-15',
        })
        self.assertEqual(reception.sortasi_deduction_pct, 0.0)
        self.assertEqual(reception.accepted_net_kg, 0.0)

    def test_12_deduction_exceeds_gross_raises(self):
        """Test that deduction > gross raises error."""
        with self.assertRaises(ValidationError):
            self.MillReception.create({
                'spb_id': self.spb.id,
                'gross_kg': 1000.00,
                'sortasi_deduction_kg': 1500.00,
                'reception_date': '2025-07-15',
            })

    def test_13_negative_gross_raises(self):
        """Test that negative gross weight is rejected."""
        with self.assertRaises(ValidationError):
            self.MillReception.create({
                'spb_id': self.spb.id,
                'gross_kg': -100.00,
                'reception_date': '2025-07-15',
            })


class TestSalesInvoice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SalesInvoice = cls.env['sales.invoice']
        cls.partner = cls.env['res.partner'].create({'name': 'PT Invoice Test'})
        cls.mill = cls.env['sales.mill'].create({
            'partner_id': cls.partner.id,
            'pricing_basis': 'market',
        })

    def test_14_create_invoice(self):
        """Test creating a sales invoice line."""
        invoice = self.SalesInvoice.create({
            'mill_id': self.mill.id,
            'period_start': '2025-07-01',
            'period_end': '2025-07-31',
        })
        self.assertTrue(invoice.id)
        self.assertEqual(invoice.state, 'draft')
        self.assertEqual(invoice.total_accepted_kg, 0.0)
        self.assertEqual(invoice.line_amount, 0.0)

    def test_15_invoice_workflow(self):
        """Test invoice workflow."""
        invoice = self.SalesInvoice.create({
            'mill_id': self.mill.id,
            'period_start': '2025-07-01',
            'period_end': '2025-07-31',
        })
        self.assertEqual(invoice.state, 'draft')
        invoice.action_confirm()
        self.assertEqual(invoice.state, 'confirmed')
        invoice.action_invoice()
        self.assertEqual(invoice.state, 'invoiced')
        invoice.action_draft()
        self.assertEqual(invoice.state, 'draft')

    def test_16_invalid_period_raises(self):
        """Test that period_start > period_end is rejected."""
        with self.assertRaises(ValidationError):
            self.SalesInvoice.create({
                'mill_id': self.mill.id,
                'period_start': '2025-07-31',
                'period_end': '2025-07-01',
            })


class TestSalesSortasiAnalysis(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SortasiAnalysis = cls.env['sales.sortasi_analysis']
        cls.partner = cls.env['res.partner'].create({'name': 'PT Sortasi'})
        cls.mill = cls.env['sales.mill'].create({
            'partner_id': cls.partner.id,
            'pricing_basis': 'market',
        })
        cls.estate = cls.env['estate.estate'].create({'name': 'Test', 'code': 'TE'})
        cls.afdeling = cls.env['estate.afdeling'].create({
            'name': 'Afd. A', 'code': 'A', 'estate_id': cls.estate.id,
        })
        cls.block = cls.env['estate.block'].create({
            'name': 'Block A1', 'code': 'A1', 'afdeling_id': cls.afdeling.id,
        })

    def test_17_create_sortasi_analysis(self):
        """Test creating a sortasi analysis record."""
        analysis = self.SortasiAnalysis.create({
            'mill_id': self.mill.id,
            'period_start': '2025-07-01',
            'period_end': '2025-07-31',
            'deduction_reason': 'buah mentah',
            'total_deduction_kg': 350.00,
            'frequency_count': 12,
            'trend_pct': 28.5,
        })
        self.assertTrue(analysis.id)
        self.assertEqual(analysis.deduction_reason, 'buah mentah')
        self.assertEqual(analysis.total_deduction_kg, 350.00)
        self.assertEqual(analysis.frequency_count, 12)
        self.assertEqual(analysis.trend_pct, 28.5)

    def test_18_sortasi_analysis_with_block_and_mandor(self):
        """Test creating a sortasi analysis with block and mandor drill-down."""
        employee = self.env['hr.employee'].create({'name': 'Mandor Test'})
        analysis = self.SortasiAnalysis.create({
            'mill_id': self.mill.id,
            'period_start': '2025-07-01',
            'period_end': '2025-07-31',
            'block_id': self.block.id,
            'mandor_id': employee.id,
            'deduction_reason': 'tangkai panjang',
            'total_deduction_kg': 200.00,
            'frequency_count': 5,
            'trend_pct': 15.0,
        })
        self.assertTrue(analysis.id)
        self.assertEqual(analysis.mandor_id, employee)
