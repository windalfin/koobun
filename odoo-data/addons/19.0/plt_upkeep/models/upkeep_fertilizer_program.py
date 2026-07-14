# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class UpkeepFertilizerProgram(models.Model):
    """Fertilizer recommendation per block, per round, per year."""
    _name = 'upkeep.fertilizer_program'
    _description = 'Fertilizer Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year, round, block_id'

    block_id = fields.Many2one(
        'estate.block',
        string='Block',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    fertilizer_type = fields.Char(
        string='Fertilizer Type',
        required=True,
        tracking=True,
    )
    dose_per_tree_kg = fields.Float(
        string='Dose per Tree (KG)',
        required=True,
        digits=(12, 4),
        tracking=True,
    )
    round = fields.Integer(
        string='Round',
        required=True,
        default=1,
        tracking=True,
    )
    year = fields.Integer(
        string='Year',
        required=True,
        default=lambda self: fields.Date.context_today(self).year,
        tracking=True,
    )
    total_kg = fields.Float(
        string='Total KG',
        digits=(12, 2),
        compute='_compute_total_kg',
        store=True,
        tracking=True,
    )
    realization_kg = fields.Float(
        string='Realization (KG)',
        digits=(12, 2),
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('realized', 'Realized'),
            ('cancelled', 'Cancelled'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.depends('dose_per_tree_kg', 'block_id')
    def _compute_total_kg(self):
        for rec in self:
            # Total is dose * tree count from block census
            # Fallback to 0 if no census data available
            rec.total_kg = rec.dose_per_tree_kg * 0  # placeholder — real calc needs census
