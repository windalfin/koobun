# -*- coding: utf-8 -*-
from odoo import models, fields


class EstateTPH(models.Model):
    _name = 'estate.tph'
    _description = 'TPH (Tempat Pengumpulan Hasil)'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    block_id = fields.Many2one(
        'estate.block', string='Block', required=True,
        ondelete='restrict',
    )
    gps_lat = fields.Float(string='GPS Latitude', digits=(16, 8))
    gps_lon = fields.Float(string='GPS Longitude', digits=(16, 8))

    _sql_constraints = [
        (
            'code_block_unique',
            'unique(code, block_id)',
            'TPH code must be unique per block!',
        ),
    ]
