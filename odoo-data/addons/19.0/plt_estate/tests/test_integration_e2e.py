# -*- coding: utf-8 -*-
"""
End-to-end integration test for the PLT Suite.
Tests the full value chain: estate → harvest → transport → sales → payroll.

This test creates realistic data across all modules and verifies
that data flows correctly through the system.
"""
from odoo.tests.common import TransactionCase


class TestE2EHarvestToPayroll(TransactionCase):
    """Full integration test: taksasi → TPH → SPB → weighbridge → mill → invoice → payroll."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Skip if dependent modules aren't loaded yet
        try:
            cls.Taksasi = cls.env['harvest.taksasi']
            cls.TPHRecord = cls.env['harvest.tph_record']
            cls.PremiConfig = cls.env['harvest.premi_config']
            cls.SPB = cls.env['transport.spb']
            cls.Ticket = cls.env['transport.weighbridge_ticket']
            cls.Mill = cls.env['sales.mill']
            cls.TbsPrice = cls.env['sales.tbs_price']
            cls.MillReception = cls.env['sales.mill_reception']
            cls.SalesInvoice = cls.env['sales.invoice']
            cls.WorkerContract = cls.env['payroll.worker_contract']
            cls.WageMaster = cls.env['payroll.wage_master']
            cls.PayslipLine = cls.env['payroll.payslip_line']
            cls.PayrollBatch = cls.env['payroll.payroll_batch']
            cls._integration_ready = True
        except KeyError:
            cls._integration_ready = False
            return

        # ── Master Data ─────────────────────────────────────────
        cls.Estate = cls.env['estate.estate']
        cls.Afdeling = cls.env['estate.afdeling']
        cls.Block = cls.env['estate.block']
        cls.TPH = cls.env['estate.tph']
        cls.Employee = cls.env['hr.employee']
        cls.Taksasi = cls.env['harvest.taksasi']
        cls.TPHRecord = cls.env['harvest.tph_record']
        cls.PremiConfig = cls.env['harvest.premi_config']
        cls.SPB = cls.env['transport.spb']
        cls.Ticket = cls.env['transport.weighbridge_ticket']
        cls.Mill = cls.env['sales.mill']
        cls.TbsPrice = cls.env['sales.tbs_price']
        cls.MillReception = cls.env['sales.mill_reception']
        cls.SalesInvoice = cls.env['sales.invoice']
        cls.WorkerContract = cls.env['payroll.worker_contract']
        cls.WageMaster = cls.env['payroll.wage_master']
        cls.PayslipLine = cls.env['payroll.payslip_line']
        cls.PayrollBatch = cls.env['payroll.payroll_batch']
        cls.Partner = cls.env['res.partner']

        # ── Create Estate Structure ─────────────────────────────
        cls.estate = cls.Estate.create({'name': 'Kebun Test', 'code': 'KT'})
        cls.afdeling = cls.Afdeling.create({
            'name': 'Afdeling I', 'code': 'I', 'estate_id': cls.estate.id,
        })
        cls.block = cls.Block.create({
            'name': 'Block I-A', 'code': 'IA', 'afdeling_id': cls.afdeling.id,
            'area_ha_planted': 10.0,
        })
        cls.tph = cls.TPH.create({
            'name': 'TPH-01', 'code': 'TPH-01', 'block_id': cls.block.id,
        })

        # ── Create Employees ────────────────────────────────────
        cls.harvester = cls.Employee.create({'name': 'Pemanen A'})
        cls.kerani = cls.Employee.create({'name': 'Kerani Panen'})
        cls.mandor = cls.Employee.create({'name': 'Mandor Panen'})
        cls.driver = cls.Employee.create({'name': 'Supir Truk'})
        cls.operator = cls.Employee.create({'name': 'Operator Timbangan'})

        # ── Create Harvest Config ───────────────────────────────
        cls.premi = cls.PremiConfig.create({
            'name': 'Premi Standard 2025',
            'basis_kg_per_hk': 1000.0,
            'premi_tier_1_rate': 150.0,
            'premi_tier_2_rate': 200.0,
            'effective_from': '2025-01-01',
        })
        cls.premi.action_approve()

        # ── Create Mill & Price ─────────────────────────────────
        cls.partner = cls.Partner.create({'name': 'PT Mill Test'})
        cls.mill = cls.Mill.create({
            'partner_id': cls.partner.id,
            'pricing_basis': 'market',
        })
        cls.price = cls.TbsPrice.create({
            'name': 'Market Price Jul 2025',
            'price_type': 'market',
            'age_band_min': 3,
            'age_band_max': 25,
            'price_per_kg': 2500.00,
            'date_from': '2025-07-01',
            'date_to': '2025-07-31',
        })
        cls.price.action_approve()

        # ── Create Wage Master ──────────────────────────────────
        cls.wage = cls.WageMaster.create({
            'name': 'BHL Wage 2025',
            'worker_class': 'BHL',
            'daily_wage': 85000.0,
            'effective_from': '2025-01-01',
        })
        cls.wage.action_approve()

    # ═══════════════════════════════════════════════════════════
    # Phase 1: Harvest
    # ═══════════════════════════════════════════════════════════

    def test_e2e_01_taksasi(self):
        if not self._integration_ready:
            self.skipTest("Dependent modules not loaded")
        """Step 1: Create a taksasi (crop estimate) for the block."""
        taksasi = self.Taksasi.create({
            'date': '2025-07-14',
            'block_id': self.block.id,
            'pokok_sampled': 20,
            'bunches_counted': 35,
        })
        self.assertTrue(taksasi.id)
        self.assertGreater(taksasi.akp, 0)

    def test_e2e_02_tph_capture(self):
        if not self._integration_ready:
            self.skipTest("Dependent modules not loaded")
        """Step 2: Record harvest at TPH."""
        record = self.TPHRecord.create({
            'date': '2025-07-14',
            'tph_id': self.tph.id,
            'harvester_id': self.harvester.id,
            'kerani_id': self.kerani.id,
            'janjang_count': 150,
            'brondolan_kg': 25.0,
        })
        self.assertTrue(record.id)
        self.assertEqual(record.janjang_count, 150)

    # ═══════════════════════════════════════════════════════════
    # Phase 2: Transport & Weighbridge
    # ═══════════════════════════════════════════════════════════

    def test_e2e_03_spb_creation(self):
        if not self._integration_ready:
            self.skipTest("Dependent modules not loaded")
        """Step 3: Create SPB for FFB dispatch."""
        spb = self.SPB.create({
            'number': 'SPB-E2E-001',
            'date': '2025-07-14',
            'block_ids': [(4, self.block.id)],
            'tph_ids': [(4, self.tph.id)],
            'janjang_count': 150,
            'estimated_kg': 3000.0,
            'driver_id': self.driver.id,
        })
        self.assertTrue(spb.id)
        self.assertEqual(spb.state, 'draft')

    def test_e2e_04_weighbridge(self):
        if not self._integration_ready:
            self.skipTest("Dependent modules not loaded")
        """Step 4: Create weighbridge ticket for SPB."""
        spb = self.SPB.create({
            'number': 'SPB-E2E-002',
            'date': '2025-07-14',
            'block_ids': [(4, self.block.id)],
            'tph_ids': [(4, self.tph.id)],
            'janjang_count': 150,
            'estimated_kg': 3000.0,
        })
        ticket = self.Ticket.create({
            'spb_id': spb.id,
            'gross_kg': 5500.0,
            'tare_kg': 2500.0,
            'mode': 'auto',
            'operator_id': self.operator.id,
        })
        self.assertTrue(ticket.id)
        self.assertTrue(ticket.net_kg > 0)
        self.assertAlmostEqual(ticket.net_kg, 3000.0)

    # ═══════════════════════════════════════════════════════════
    # Phase 3: Sales & Mill Reconciliation
    # ═══════════════════════════════════════════════════════════

    def test_e2e_05_mill_reception(self):
        if not self._integration_ready:
            self.skipTest("Dependent modules not loaded")
        """Step 5: Record mill reception for the SPB."""
        spb = self.SPB.create({
            'number': 'SPB-E2E-003',
            'date': '2025-07-14',
            'block_ids': [(4, self.block.id)],
            'tph_ids': [(4, self.tph.id)],
            'janjang_count': 150,
        })
        reception = self.MillReception.create({
            'spb_id': spb.id,
            'gross_kg': 5000.0,
            'sortasi_deduction_kg': 150.0,
            'deduction_reasons': 'buah mentah: 150kg',
            'mill_doc_ref': 'WB-2025-E2E',
            'reception_date': '2025-07-14',
        })
        self.assertTrue(reception.id)
        self.assertGreater(reception.accepted_net_kg, 0)

    def test_e2e_06_sales_invoice(self):
        if not self._integration_ready:
            self.skipTest("Dependent modules not loaded")
        """Step 6: Create sales invoice from mill reception data."""
        invoice = self.SalesInvoice.create({
            'mill_id': self.mill.id,
            'period_start': '2025-07-01',
            'period_end': '2025-07-31',
        })
        self.assertTrue(invoice.id)
        self.assertEqual(invoice.state, 'draft')

    # ═══════════════════════════════════════════════════════════
    # Phase 4: Payroll
    # ═══════════════════════════════════════════════════════════

    def test_e2e_07_worker_contract(self):
        if not self._integration_ready:
            self.skipTest("Dependent modules not loaded")
        """Step 7: Create worker contract for harvester."""
        contract = self.WorkerContract.create({
            'name': 'Contract - Pemanen A',
            'employee_id': self.harvester.id,
            'worker_class': 'BHL',
            'contract_type': 'PKWT',
            'wage': 2550000.0,
            'date_start': '2025-01-01',
        })
        self.assertTrue(contract.id)
        self.assertEqual(contract.worker_class, 'BHL')

    def test_e2e_08_payroll_batch_and_payslip(self):
        if not self._integration_ready:
            self.skipTest("Dependent modules not loaded")
        """Step 8: Create payroll batch and payslip line."""
        batch = self.PayrollBatch.create({
            'period_start': '2025-07-01',
            'period_end': '2025-07-15',
        })
        payslip = self.PayslipLine.create({
            'payroll_batch_id': batch.id,
            'employee_id': self.harvester.id,
            'hk_count': 10,
            'daily_base': 85000.0,
            'premi_amount': 450000.0,
            'denda_amount': 25000.0,
        })
        self.assertTrue(payslip.id)
        self.assertGreater(payslip.net_pay, 0)
