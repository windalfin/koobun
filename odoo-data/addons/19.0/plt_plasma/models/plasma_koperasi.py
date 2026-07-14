# -*- coding: utf-8 -*-
from odoo import models, fields


class PlasmaKoperasi(models.Model):
    """Cooperative registry."""
    _name = 'plasma.koperasi'
    _description = 'Plasma Koperasi (Cooperative)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True, index=True)
    address = fields.Text(string='Address', tracking=True)
    contact_person = fields.Char(string='Contact Person', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    farmer_ids = fields.One2many('plasma.farmer', 'koperasi_id', string='Farmers')
    farmer_count = fields.Integer(string='Farmer Count', compute='_compute_farmer_count', store=True)

    @api.depends('farmer_ids')
    def _compute_farmer_count(self):
        for rec in self:
            rec.farmer_count = len(rec.farmer_ids)

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Koperasi code must be unique!'),
    ]
