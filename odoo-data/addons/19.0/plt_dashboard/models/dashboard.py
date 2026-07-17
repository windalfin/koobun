# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PLTDashboard(models.Model):
    """Lightweight dashboard model used as an anchor for menu actions.

    It carries *no* persistent rows of its own (``_auto = False``) and
    only serves as a reference point so that the web-client can open the
    board views from a menu item.
    """
    _name = 'plt.dashboard'
    _description = 'PLT Dashboard'
    _auto = False

    name = fields.Char(string='Name')

    # ---- Estate stats --------------------------------------------------
    estate_block_count = fields.Integer(
        string='Total Blocks',
        compute='_compute_estate_stats',
    )
    estate_total_ha = fields.Float(
        string='Total Hectares',
        digits=(16, 4),
        compute='_compute_estate_stats',
    )
    estate_active_count = fields.Integer(
        string='Active Blocks',
        compute='_compute_estate_stats',
    )

    # ---- Harvest stats -------------------------------------------------
    harvest_record_count = fields.Integer(
        string='Harvest Records',
        compute='_compute_harvest_stats',
    )
    harvest_total_kg = fields.Float(
        string='Total KG Produced',
        compute='_compute_harvest_stats',
    )

    # ---- Transport stats -----------------------------------------------
    transport_spb_count = fields.Integer(
        string='SPB Records',
        compute='_compute_transport_stats',
    )

    # ---- Sales stats ---------------------------------------------------
    sales_order_count = fields.Integer(
        string='Sales Orders',
        compute='_compute_sales_stats',
    )

    # ---- Payroll stats -------------------------------------------------
    payroll_contract_count = fields.Integer(
        string='Worker Contracts',
        compute='_compute_payroll_stats',
    )
    payroll_batch_count = fields.Integer(
        string='Payroll Batches',
        compute='_compute_payroll_stats',
    )

    # ---- Upkeep stats --------------------------------------------------
    upkeep_workorder_count = fields.Integer(
        string='Work Orders (BPB)',
        compute='_compute_upkeep_stats',
    )

    # ---- Planning stats ------------------------------------------------
    planning_rkap_count = fields.Integer(
        string='RKAP Records',
        compute='_compute_planning_stats',
    )

    # ---- Plasma stats --------------------------------------------------
    plasma_farmer_count = fields.Integer(
        string='Plasma Farmers',
        compute='_compute_plasma_stats',
    )
    plasma_koperasi_count = fields.Integer(
        string='Plasma Koperasi',
        compute='_compute_plasma_stats',
    )

    # ---- Compliance stats ----------------------------------------------
    compliance_ispo_count = fields.Integer(
        string='ISPO Evidence',
        compute='_compute_compliance_stats',
    )
    compliance_k3_count = fields.Integer(
        string='K3 Incidents',
        compute='_compute_compliance_stats',
    )

    # ---- Nursery stats -------------------------------------------------
    nursery_batch_count = fields.Integer(
        string='Nursery Batches',
        compute='_compute_nursery_stats',
    )

    # ---- GCG stats -----------------------------------------------------
    gcg_audit_count = fields.Integer(
        string='Audit Logs',
        compute='_compute_gcg_stats',
    )

    # ---- Compute methods -----------------------------------------------
    @api.depends()
    def _compute_estate_stats(self):
        Block = self.env['estate.block'].sudo()
        count = Block.search_count([])
        active = Block.search_count([('active', '=', True)])
        total_ha = sum(Block.sudo().search([]).mapped('area_ha_total'))
        for rec in self:
            rec.estate_block_count = count
            rec.estate_active_count = active
            rec.estate_total_ha = total_ha

    @api.depends()
    def _compute_harvest_stats(self):
        TPH = self.env['harvest.tph_record'].sudo()
        count = TPH.search_count([])
        total_kg = sum(TPH.sudo().search([]).mapped('total_tonnage')) * 1000.0
        for rec in self:
            rec.harvest_record_count = count
            rec.harvest_total_kg = total_kg

    @api.depends()
    def _compute_transport_stats(self):
        SPB = self.env['transport.spb'].sudo()
        for rec in self:
            rec.transport_spb_count = SPB.search_count([])

    @api.depends()
    def _compute_sales_stats(self):
        Rec = self.env['sales.mill_reception'].sudo()
        for rec in self:
            rec.sales_order_count = Rec.search_count([])

    @api.depends()
    def _compute_payroll_stats(self):
        Contract = self.env['payroll.worker_contract'].sudo()
        Batch = self.env['payroll.payroll_batch'].sudo()
        for rec in self:
            rec.payroll_contract_count = Contract.search_count([])
            rec.payroll_batch_count = Batch.search_count([])

    @api.depends()
    def _compute_upkeep_stats(self):
        BPB = self.env['upkeep.bpb'].sudo()
        for rec in self:
            rec.upkeep_workorder_count = BPB.search_count([])

    @api.depends()
    def _compute_planning_stats(self):
        RKAP = self.env['plan.rkap'].sudo()
        for rec in self:
            rec.planning_rkap_count = RKAP.search_count([])

    @api.depends()
    def _compute_plasma_stats(self):
        Farmer = self.env['plasma.farmer'].sudo()
        Koperasi = self.env['plasma.koperasi'].sudo()
        for rec in self:
            rec.plasma_farmer_count = Farmer.search_count([])
            rec.plasma_koperasi_count = Koperasi.search_count([])

    @api.depends()
    def _compute_compliance_stats(self):
        ISPO = self.env['compliance.ispo_evidence'].sudo()
        K3 = self.env['compliance.k3_incident'].sudo()
        for rec in self:
            rec.compliance_ispo_count = ISPO.search_count([])
            rec.compliance_k3_count = K3.search_count([])

    @api.depends()
    def _compute_nursery_stats(self):
        Batch = self.env['nursery.batch'].sudo()
        for rec in self:
            rec.nursery_batch_count = Batch.search_count([])

    @api.depends()
    def _compute_gcg_stats(self):
        Log = self.env['gcg.audit.log'].sudo()
        for rec in self:
            rec.gcg_audit_count = Log.search_count([])

    @api.model_create_multi
    def create(self, vals_list):
        return self.env['plt.dashboard']
