# -*- coding: utf-8 -*-
from odoo import models, fields


class ComplianceK3Incident(models.Model):
    """K3 incident/accident log with APD issue records."""
    _name = 'compliance.k3_incident'
    _description = 'K3 Incident Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'incident_date desc'

    incident_date = fields.Date(string='Date', required=True, default=fields.Date.context_today, tracking=True)
    incident_type = fields.Selection([
        ('accident', 'Accident (Kecelakaan)'),
        ('near_miss', 'Near Miss (Hampir Celaka)'),
        ('apd_issue', 'APD Issue'),
        ('environmental', 'Environmental'),
    ], string='Type', required=True, tracking=True)
    location = fields.Char(string='Location', tracking=True)
    block_id = fields.Many2one('estate.block', string='Block', ondelete='restrict', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Involved Employee', tracking=True)
    description = fields.Text(string='Description', required=True, tracking=True)
    severity = fields.Selection([
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('fatal', 'Fatal'),
    ], string='Severity', tracking=True)
    corrective_action = fields.Text(string='Corrective Action', tracking=True)
    status = fields.Selection([
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], string='Status', default='reported', required=True, tracking=True)
    notes = fields.Text(string='Notes')
