# -*- coding: utf-8 -*-
from odoo import models, fields


class EstateAfdeling(models.Model):
    _name = 'estate.afdeling'
    _description = 'Afdeling'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    estate_id = fields.Many2one(
        'estate.estate', string='Estate', required=True,
        ondelete='restrict', tracking=True,
    )
    manager_id = fields.Many2one(
        'hr.employee', string='Manager', tracking=True,
    )
    active = fields.Boolean(string='Active', default=True, tracking=True)

    _sql_constraints = [
        (
            'code_estate_unique',
            'unique(code, estate_id)',
            'Afdeling code must be unique per estate!',
        ),
    ]
