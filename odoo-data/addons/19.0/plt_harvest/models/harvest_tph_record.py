# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HarvestTPHRecord(models.Model):
    _name = 'harvest.tph_record'
    _description = 'TPH Harvest Record (Capture at TPH)'
    _inherit = ['mail.thread']
    _order = 'date desc, timestamp desc, id desc'

    # ── Basic Fields ──────────────────────────────────────────
    date = fields.Date(string='Date', required=True, tracking=True)
    tph_id = fields.Many2one(
        'estate.tph', string='TPH', required=True,
        ondelete='restrict', tracking=True,
    )
    harvester_id = fields.Many2one(
        'hr.employee', string='Harvester', required=True,
        ondelete='restrict', tracking=True,
    )
    kerani_id = fields.Many2one(
        'hr.employee', string='Kerani (Clerk)', required=True,
        ondelete='restrict', tracking=True,
    )

    # ── Harvest Quantities ────────────────────────────────────
    janjang_count = fields.Integer(
        string='Janjang Count', required=True, tracking=True,
    )
    brondolan_kg = fields.Float(
        string='Brondolan (kg)', digits=(16, 2), tracking=True,
    )
    brondolan_karung = fields.Integer(
        string='Brondolan Karung (Sacks)', tracking=True,
    )

    # ── GPS & Timestamp ───────────────────────────────────────
    gps_lat = fields.Float(
        string='GPS Latitude', digits=(16, 8), tracking=True,
    )
    gps_lon = fields.Float(
        string='GPS Longitude', digits=(16, 8), tracking=True,
    )
    timestamp = fields.Datetime(
        string='Capture Timestamp', tracking=True,
        help='Exact time the harvest was captured at TPH.',
    )

    # ── Photo ─────────────────────────────────────────────────
    photo = fields.Binary(string='Photo', attachment=True)

    # ── Computed from Weighbridge ─────────────────────────────
    BJR = fields.Float(
        string='BJR (Berat Janjang Rata-rata)',
        digits=(16, 2),
        compute='_compute_BJR', store=True,
        help='Average bunch weight computed from weighbridge data.',
    )
    total_tonnage = fields.Float(
        string='Total Tonnage', digits=(16, 2),
        compute='_compute_total_tonnage', store=True,
    )

    # ── Status ────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('verified', 'Verified'),
            ('approved', 'Approved'),
        ],
        string='State', default='draft', required=True, tracking=True,
    )

    # ── Duplicate Detection ───────────────────────────────────
    _sql_constraints = [
        (
            'unique_harvester_tph_date',
            'unique(harvester_id, tph_id, date)',
            'Duplicate harvest record detected! Same harvester, TPH, and date already exists.',
        ),
    ]

    # ── Computed Methods ──────────────────────────────────────
    @api.depends('janjang_count')
    def _compute_BJR(self):
        """BJR is computed later from weighbridge data. Default to 0."""
        for rec in self:
            rec.BJR = rec.BJR or 0.0

    @api.depends('janjang_count', 'BJR')
    def _compute_total_tonnage(self):
        for rec in self:
            if rec.janjang_count and rec.BJR:
                rec.total_tonnage = (rec.janjang_count * rec.BJR) / 1000.0
            else:
                rec.total_tonnage = 0.0

    # ── Actions ──────────────────────────────────────────────
    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_verify(self):
        self.write({'state': 'verified'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_draft(self):
        self.write({'state': 'draft'})
