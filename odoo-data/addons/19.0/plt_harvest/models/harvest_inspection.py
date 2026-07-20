# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HarvestInspection(models.Model):
    _name = 'harvest.inspection'
    _description = 'Mutu Ancak / Mutu Buah Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # ── Basic Fields ──────────────────────────────────────────
    date = fields.Date(
        string='Tanggal Inspeksi', required=True,
        default=fields.Date.context_today, tracking=True,
    )
    inspection_type = fields.Selection(
        selection=[
            ('ancak', 'Mutu Ancak'),
            ('buah', 'Mutu Buah'),
        ],
        string='Jenis Inspeksi', required=True,
        default='ancak', tracking=True,
    )
    mandor_id = fields.Many2one(
        'hr.employee', string='Mandor', required=True,
        ondelete='restrict', tracking=True,
    )
    block_id = fields.Many2one(
        'estate.block', string='Blok', required=True,
        ondelete='restrict', tracking=True,
    )
    checklist_items = fields.Text(
        string='Item Checklist', tracking=True,
        help='Daftar item yang diperiksa saat inspeksi.',
    )

    # ── Scores (individual quality components) ─────────────────
    score_buah_mentah = fields.Integer(
        string='Skor Buah Mentah', default=0, tracking=True,
    )
    score_tangkai_panjang = fields.Integer(
        string='Skor Tangkai Panjang', default=0, tracking=True,
    )
    score_brondolan = fields.Integer(
        string='Skor Brondolan Tidak Dikutip', default=0, tracking=True,
    )

    # ── Computed ──────────────────────────────────────────────
    total_score = fields.Integer(
        string='Total Skor',
        compute='_compute_total_score', store=True,
    )
    result = fields.Selection(
        selection=[
            ('pass', 'Lulus'),
            ('fail', 'Gagal'),
        ],
        string='Hasil',
        compute='_compute_result', store=True,
    )

    # ── State ─────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
        ],
        string='Status', default='draft', required=True, tracking=True,
    )

    # ── Computed Methods ──────────────────────────────────────
    @api.depends(
        'score_buah_mentah', 'score_tangkai_panjang', 'score_brondolan',
    )
    def _compute_total_score(self):
        for rec in self:
            rec.total_score = (
                rec.score_buah_mentah
                + rec.score_tangkai_panjang
                + rec.score_brondolan
            )

    @api.depends('total_score')
    def _compute_result(self):
        for rec in self:
            rec.result = 'fail' if rec.total_score > 3 else 'pass'

    # ── Actions ───────────────────────────────────────────────
    def action_post(self):
        for rec in self:
            rec.state = 'posted'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'