# -*- coding: utf-8 -*-
from odoo import models, fields


class ComplianceEUDRExport(models.Model):
    """EUDR data pack per block: geolocation + production period."""
    _name = 'compliance.eudr_export'
    _description = 'EUDR Export Pack'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'export_date desc'

    export_date = fields.Date(string='Export Date', default=fields.Date.context_today, required=True, tracking=True)
    block_id = fields.Many2one('estate.block', string='Block', required=True, ondelete='restrict', tracking=True)
    geojson_data = fields.Text(string='GeoJSON Data', tracking=True)
    production_start = fields.Date(string='Production Start', tracking=True)
    production_end = fields.Date(string='Production End', tracking=True)
    total_kg = fields.Float(string='Total KG Produced', digits=(12, 2), tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('submitted', 'Submitted'),
    ], string='Status', default='draft', required=True, tracking=True)
    notes = fields.Text(string='Notes')
