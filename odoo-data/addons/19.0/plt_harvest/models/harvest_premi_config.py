# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HarvestPremiConfig(models.Model):
    _name = 'harvest.premi_config'
    _description = 'Premi (Harvest Bonus) Configuration'
    _inherit = ['mail.thread']
    _order = 'date_from desc, id desc'

    # ── Basic Fields ──────────────────────────────────────────
    name = fields.Char(string='Name', required=True, tracking=True)
    block_class = fields.Char(string='Block Class', tracking=True)
    tahun_tanam_min = fields.Integer(string='Planting Year Min', tracking=True)
    tahun_tanam_max = fields.Integer(string='Planting Year Max', tracking=True)

    # ── Rate Fields ───────────────────────────────────────────
    basis_kg_per_hk = fields.Float(
        string='Basis (kg/HK)', digits=(16, 2), required=True, tracking=True,
        help='Base output per harvester-day for premi calculation.',
    )
    premi_tier_1_rate = fields.Float(
        string='Premi Tier 1 Rate', digits=(16, 4), tracking=True,
        help='Rate per kg above basis up to tier 1 threshold.',
    )
    premi_tier_2_rate = fields.Float(
        string='Premi Tier 2 Rate', digits=(16, 4), tracking=True,
        help='Rate per kg above tier 1 threshold.',
    )
    premi_tier_1_threshold = fields.Float(
        string='Premi Tier 1 Threshold', digits=(16, 2), tracking=True,
        help='Kg threshold dividing tier 1 and tier 2.',
    )
    brondolan_rate = fields.Float(
        string='Brondolan Rate', digits=(16, 4), tracking=True,
        help='Rate per kg for brondolan collection.',
    )
    mandor_multiplier = fields.Float(
        string='Mandor Multiplier', digits=(16, 4), tracking=True,
        default=1.0,
        help='Multiplier applied to mandor premi over harvester base.',
    )
    kerani_multiplier = fields.Float(
        string='Kerani Multiplier', digits=(16, 4), tracking=True,
        default=1.0,
        help='Multiplier applied to kerani premi over harvester base.',
    )

    # ── Effective Dates ───────────────────────────────────────
    date_from = fields.Date(string='Valid From', required=True, tracking=True)
    date_to = fields.Date(string='Valid To', tracking=True)

    # ── Status ────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
        ],
        string='State', default='draft', required=True, tracking=True,
    )

    # ── Constraints ──────────────────────────────────────────
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_to and rec.date_from and rec.date_to < rec.date_from:
                raise ValidationError(_(
                    'Valid To date must be after Valid From date.'
                ))

    @api.constrains('tahun_tanam_min', 'tahun_tanam_max')
    def _check_years(self):
        for rec in self:
            if (rec.tahun_tanam_min and rec.tahun_tanam_max
                    and rec.tahun_tanam_max < rec.tahun_tanam_min):
                raise ValidationError(_(
                    'Planting Year Max must be >= Planting Year Min.'
                ))

    # ── Actions ──────────────────────────────────────────────
    def action_approve(self):
        self.write({'state': 'approved'})

    def action_draft(self):
        self.write({'state': 'draft'})
