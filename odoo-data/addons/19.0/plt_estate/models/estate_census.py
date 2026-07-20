# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EstateCensus(models.Model):
    _name = 'estate.census'
    _description = 'Palm Census (Sensus Pokok)'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    date = fields.Date(string='Census Date', required=True, tracking=True)
    block_id = fields.Many2one(
        'estate.block', string='Block', required=True,
        ondelete='restrict', tracking=True,
    )
    productive_count = fields.Integer(
        string='Productive', default=0, tracking=True,
    )
    unproductive_count = fields.Integer(
        string='Unproductive', default=0, tracking=True,
    )
    dead_count = fields.Integer(
        string='Dead', default=0, tracking=True,
    )
    vacant_points = fields.Integer(
        string='Vacant Points', default=0, tracking=True,
    )
    sisipan_count = fields.Integer(
        string='Sisipan (Interplant)', default=0, tracking=True,
    )
    notes = fields.Text(string='Notes', tracking=True)

    # ── Computed: Total ───────────────────────────────────────
    total_pokok = fields.Integer(
        string='Total Pokok',
        compute='_compute_total_pokok', store=True,
    )

    # ── Computed: Previous census ─────────────────────────────
    previous_census_id = fields.Many2one(
        'estate.census', string='Previous Census',
        compute='_compute_previous_census', store=True,
    )

    # ── Variance fields (computed vs previous census) ─────────
    var_productive = fields.Integer(
        string='Δ Productive', compute='_compute_variance', store=False,
    )
    var_unproductive = fields.Integer(
        string='Δ Unproductive', compute='_compute_variance', store=False,
    )
    var_dead = fields.Integer(
        string='Δ Dead', compute='_compute_variance', store=False,
    )
    var_vacant = fields.Integer(
        string='Δ Vacant', compute='_compute_variance', store=False,
    )
    var_sisipan = fields.Integer(
        string='Δ Sisipan', compute='_compute_variance', store=False,
    )
    var_total = fields.Integer(
        string='Δ Total', compute='_compute_variance', store=False,
    )

    _sql_constraints = [
        (
            'date_block_unique',
            'unique(date, block_id)',
            'Only one census per block per day is allowed!',
        ),
    ]

    # ── Computed methods ──────────────────────────────────────
    @api.depends(
        'productive_count', 'unproductive_count', 'dead_count',
        'vacant_points', 'sisipan_count',
    )
    def _compute_total_pokok(self):
        for rec in self:
            rec.total_pokok = (
                rec.productive_count + rec.unproductive_count
                + rec.dead_count + rec.vacant_points
                + rec.sisipan_count
            )

    @api.depends('date', 'block_id')
    def _compute_previous_census(self):
        for rec in self:
            if rec.date and rec.block_id:
                previous = self.search([
                    ('block_id', '=', rec.block_id.id),
                    ('date', '<', rec.date),
                    ('id', '!=', rec.id),
                ], order='date desc', limit=1)
                rec.previous_census_id = previous.id if previous else False
            else:
                rec.previous_census_id = False

    def _compute_variance(self):
        for rec in self:
            prev = rec.previous_census_id
            if prev:
                rec.var_productive = (
                    rec.productive_count - prev.productive_count
                )
                rec.var_unproductive = (
                    rec.unproductive_count - prev.unproductive_count
                )
                rec.var_dead = rec.dead_count - prev.dead_count
                rec.var_vacant = rec.vacant_points - prev.vacant_points
                rec.var_sisipan = rec.sisipan_count - prev.sisipan_count
                rec.var_total = rec.total_pokok - prev.total_pokok
            else:
                rec.var_productive = 0
                rec.var_unproductive = 0
                rec.var_dead = 0
                rec.var_vacant = 0
                rec.var_sisipan = 0
                rec.var_total = 0
