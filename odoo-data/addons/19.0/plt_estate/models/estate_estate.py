# -*- coding: utf-8 -*-
from odoo import models, fields


class EstateEstate(models.Model):
    _name = 'estate.estate'
    _description = 'Estate'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    active = fields.Boolean(string='Active', default=True, tracking=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Estate code must be unique!'),
    ]
