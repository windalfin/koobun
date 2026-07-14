# -*- coding: utf-8 -*-
from odoo import models, fields


class ComplianceISPOEvidence(models.Model):
    """ISPO evidence register structured by 7 principles."""
    _name = 'compliance.ispo_evidence'
    _description = 'ISPO Evidence Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'principle, criterion'

    principle = fields.Selection([
        ('1', 'Principle 1: Legality'),
        ('2', 'Principle 2: Management'),
        ('3', 'Principle 3: Conservation'),
        ('4', 'Principle 4: Social'),
        ('5', 'Principle 5: Economy'),
        ('6', 'Principle 6: Employment'),
        ('7', 'Principle 7: Continuous Improvement'),
    ], string='ISPO Principle', required=True, tracking=True)
    criterion = fields.Char(string='Criterion', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    evidence_doc = fields.Binary(string='Evidence Document', tracking=True)
    evidence_filename = fields.Char(string='Filename')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('uploaded', 'Uploaded'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending', required=True, tracking=True)
    verified_by_id = fields.Many2one('hr.employee', string='Verified By')
    verification_date = fields.Date(string='Verification Date')
    notes = fields.Text(string='Notes')
