# -*- coding: utf-8 -*-
from odoo import models, fields, api


class GCGException(models.Model):
    """Exception & red-flag registry for SPI/internal audit.

    Tracks anomalies detected by system controls or raised manually that
    need investigation and resolution.
    """
    _name = 'gcg.exception'
    _inherit = ['mail.thread']
    _description = 'GCG Exception'
    _order = 'create_date desc, id desc'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    exception_type = fields.Selection(
        [
            ('weighbridge_variance', 'Weighbridge Variance'),
            ('restan_over24h', 'Restan > 24h'),
            ('rotation_over_target', 'Rotation Over Target'),
            ('hk_anomaly', 'HK Anomaly'),
            ('chemical_variance', 'Chemical Variance'),
            ('spb_gap', 'SPB Gap'),
            ('premi_outlier', 'Premi Outlier'),
            ('master_data_change', 'Master Data Change'),
            ('override', 'Override'),
            ('other', 'Other'),
        ],
        string='Exception Type',
        required=True,
        tracking=True,
    )
    document_reference = fields.Char(
        string='Document Reference',
        tracking=True,
    )
    document_model = fields.Char(
        string='Document Model',
        tracking=True,
    )
    document_id = fields.Integer(
        string='Document ID',
        tracking=True,
    )
    severity = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Severity',
        default='medium',
        required=True,
        tracking=True,
    )
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True,
    )
    status = fields.Selection(
        [
            ('open', 'Open'),
            ('in_review', 'In Review'),
            ('resolved', 'Resolved'),
            ('dismissed', 'Dismissed'),
        ],
        string='Status',
        default='open',
        required=True,
        tracking=True,
    )
    resolution_note = fields.Text(
        string='Resolution Note',
        tracking=True,
    )
    created_at = fields.Datetime(
        string='Created At',
        default=fields.Datetime.now,
        readonly=True,
    )

    def action_open(self):
        self.status = 'open'

    def action_review(self):
        self.status = 'in_review'

    def action_resolve(self):
        self.status = 'resolved'

    def action_dismiss(self):
        self.status = 'dismissed'
