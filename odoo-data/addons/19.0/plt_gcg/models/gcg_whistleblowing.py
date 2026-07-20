# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class GCGWhistleblowing(models.Model):
    """Whistleblowing and grievance intake system.

    Allows anonymous or identified reporting of concerns.
    Case numbers are auto-generated from a sequence in the format WBS-YYYY-MM-NNN.
    """
    _name = 'gcg.whistleblowing'
    _inherit = ['mail.thread']
    _description = 'GCG Whistleblowing Case'
    _order = 'create_date desc, id desc'

    case_number = fields.Char(
        string='Case Number',
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
    )

    channel = fields.Selection(
        [
            ('web_form', 'Web Form'),
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('in_person', 'In Person'),
            ('hotline', 'Hotline'),
        ],
        string='Channel',
        tracking=True,
    )
    reporter_name = fields.Char(
        string='Reporter Name',
        tracking=False,  # Privacy-sensitive
    )
    reporter_email = fields.Char(
        string='Reporter Email',
        tracking=False,  # Privacy-sensitive
    )
    is_anonymous = fields.Boolean(
        string='Anonymous Report',
        default=False,
    )
    subject = fields.Char(
        string='Subject',
        required=True,
        tracking=True,
    )
    description = fields.Text(
        string='Description',
        required=True,
        tracking=True,
    )
    status = fields.Selection(
        [
            ('submitted', 'Submitted'),
            ('under_investigation', 'Under Investigation'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='submitted',
        tracking=True,
    )
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True,
    )
    resolution = fields.Text(
        string='Resolution',
        tracking=True,
    )
    resolution_date = fields.Datetime(
        string='Resolution Date',
        tracking=True,
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('case_number', _('New')) == _('New'):
                vals['case_number'] = self.env['ir.sequence'].next_by_code(
                    'gcg.whistleblowing.case'
                ) or _('New')
        return super().create(vals_list)

    def action_submit(self):
        self.status = 'submitted'

    def action_investigate(self):
        self.status = 'under_investigation'

    def action_resolve(self):
        self.status = 'resolved'
        self.resolution_date = fields.Datetime.now()

    def action_close(self):
        self.status = 'closed'
