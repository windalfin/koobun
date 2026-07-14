# -*- coding: utf-8 -*-
from odoo import models, fields, _


class UpkeepActivityCode(models.Model):
    """Standard activity catalog for upkeep operations."""
    _name = 'upkeep.activity_code'
    _description = 'Upkeep Activity Code'
    _order = 'code'

    name = fields.Char(
        string='Activity Name',
        required=True,
        translate=True,
        tracking=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
        tracking=True,
    )
    category = fields.Selection(
        selection=[
            ('pemupukan', 'Pemupukan (Fertilizing)'),
            ('semprot', 'Semprot (Spraying)'),
            ('tunasan', 'Tunasan (Pruning)'),
            ('kastrasi', 'Kastrasi (Castration)'),
            ('rawat_jalan', 'Rawat Jalan (Path Maintenance)'),
            ('pnd_treatment', 'P&D Treatment'),
            ('lainnya', 'Lainnya (Other)'),
        ],
        string='Category',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    description = fields.Text(
        string='Description',
    )

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Activity code must be unique!'),
    ]
