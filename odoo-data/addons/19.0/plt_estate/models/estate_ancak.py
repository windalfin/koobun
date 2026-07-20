# -*- coding: utf-8 -*-
from odoo import models, fields


class EstateAncak(models.Model):
    _name = 'estate.ancak'
    _description = 'Ancak (Sub-block)'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    block_id = fields.Many2one(
        'estate.block', string='Block', required=True,
        ondelete='restrict',
    )
    area_ha = fields.Float(string='Area (ha)', digits=(16, 4))

    _sql_constraints = [
        (
            'code_block_unique',
            'unique(code, block_id)',
            'Ancak code must be unique per block!',
        ),
    ]
