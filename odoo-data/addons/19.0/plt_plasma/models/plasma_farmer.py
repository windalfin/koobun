# -*- coding: utf-8 -*-
from odoo import models, fields


class PlasmaFarmer(models.Model):
    """Plasma farmer registry."""
    _name = 'plasma.farmer'
    _description = 'Plasma Farmer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Name', required=True, tracking=True)
    nik = fields.Char(string='NIK', tracking=True, index=True)
    stdb = fields.Char(string='STDB Number', tracking=True)
    land_area_ha = fields.Float(string='Land Area (Ha)', digits=(12, 2), tracking=True)
    plot_geojson = fields.Text(string='Plot GeoJSON', tracking=True)
    bank_account = fields.Char(string='Bank Account', tracking=True)
    bank_name = fields.Char(string='Bank Name', tracking=True)
    koperasi_id = fields.Many2one('plasma.koperasi', string='Koperasi', tracking=True)
    join_date = fields.Date(string='Join Date', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_nik', 'UNIQUE(nik)', 'NIK must be unique!'),
    ]
