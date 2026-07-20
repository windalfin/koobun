# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class UpkeepPDCensus(models.Model):
    """Pest & Disease monitoring census per block."""
    _name = 'upkeep.pd_census'
    _description = 'Pest & Disease Census'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, block_id'

    block_id = fields.Many2one(
        'estate.block',
        string='Block',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    pest_type = fields.Selection(
        selection=[
            ('ganoderma', 'Ganoderma'),
            ('tikus', 'Tikus (Rats)'),
            ('oryctes', 'Oryctes (Rhinoceros Beetle)'),
            ('ulat_api', 'Ulat Api (Fire Caterpillar)'),
            ('other', 'Other'),
        ],
        string='Pest Type',
        required=True,
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    sample_count = fields.Integer(
        string='Sample Count',
        required=True,
        default=100,
        tracking=True,
        help='Number of trees sampled.',
    )
    infected_count = fields.Integer(
        string='Infected Count',
        default=0,
        tracking=True,
    )
    severity = fields.Selection(
        selection=[
            ('low', 'Low (Rendah)'),
            ('medium', 'Medium (Sedang)'),
            ('high', 'High (Tinggi)'),
            ('critical', 'Critical (Kritis)'),
        ],
        string='Severity',
        required=True,
        default='low',
        tracking=True,
    )
    treatment_recommended = fields.Text(
        string='Treatment Recommended',
        tracking=True,
    )
    photos = fields.Binary(
        string='Photos',
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.constrains('severity')
    def _check_severity(self):
        valid = dict(self._fields['severity'].selection)
        for rec in self:
            if rec.severity not in valid:
                raise ValidationError(_(
                    'Invalid severity level: %s', rec.severity
                ))
