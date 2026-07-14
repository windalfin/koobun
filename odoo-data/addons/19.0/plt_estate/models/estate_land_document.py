# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EstateLandDocument(models.Model):
    _name = 'estate.land.document'
    _description = 'Land Document'
    _inherit = ['mail.thread']
    _order = 'expiry_date asc, id desc'

    name = fields.Char(string='Name', required=True, tracking=True)
    document_type = fields.Selection(
        selection=[
            ('shm', 'SHM (Sertifikat Hak Milik)'),
            ('hgu', 'HGU (Hak Guna Usaha)'),
            ('stdb', 'STDB'),
            ('iup', 'IUP (Izin Usaha Perkebunan)'),
            ('izin_lingkungan', 'Izin Lingkungan'),
            ('lainnya', 'Lainnya'),
        ],
        string='Document Type', required=True, tracking=True,
    )
    number = fields.Char(string='Document Number', required=True, tracking=True)
    holder_name = fields.Char(string='Holder Name', required=True, tracking=True)
    area_ha = fields.Float(string='Area (ha)', digits=(16, 4), tracking=True)
    location = fields.Char(string='Location', tracking=True)
    issue_date = fields.Date(string='Issue Date', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    block_ids = fields.Many2many(
        'estate.block', string='Related Blocks',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Attachments',
    )
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('archived', 'Archived'),
        ],
        string='State', default='active', tracking=True,
    )

    # ── Computed: Days to expiry ──────────────────────────────
    days_to_expiry = fields.Integer(
        string='Days to Expiry',
        compute='_compute_days_to_expiry', store=True,
    )

    # ── Expiry alert flags ────────────────────────────────────
    expiry_alert = fields.Selection(
        selection=[
            ('none', 'None'),
            ('90days', '≤ 90 days'),
            ('60days', '≤ 60 days'),
            ('30days', '≤ 30 days'),
            ('expired', 'Expired'),
        ],
        string='Expiry Alert',
        compute='_compute_expiry_alert', store=True,
    )

    @api.depends('expiry_date', 'state')
    def _compute_days_to_expiry(self):
        today = date.today()
        for doc in self:
            if doc.expiry_date:
                doc.days_to_expiry = (doc.expiry_date - today).days
            else:
                doc.days_to_expiry = 999

    @api.depends('days_to_expiry', 'state')
    def _compute_expiry_alert(self):
        for doc in self:
            if doc.state == 'archived':
                doc.expiry_alert = 'none'
            elif doc.state == 'expired':
                doc.expiry_alert = 'expired'
            elif doc.days_to_expiry <= 0:
                doc.expiry_alert = 'expired'
            elif doc.days_to_expiry <= 30:
                doc.expiry_alert = '30days'
            elif doc.days_to_expiry <= 60:
                doc.expiry_alert = '60days'
            elif doc.days_to_expiry <= 90:
                doc.expiry_alert = '90days'
            else:
                doc.expiry_alert = 'none'

    # ── Constraints ───────────────────────────────────────────
    @api.constrains('holder_name')
    def _check_holder_name_consistency(self):
        """Warn if holder_name mismatches other docs with same holder.

        Since Odoo constrains cannot raise warnings (only errors), we use
        a loose check: if two active documents for the same holder have
        different spellings of holder_name, we raise a validation error.
        """
        for doc in self:
            if doc.holder_name and doc.document_type:
                mismatched = self.search([
                    ('id', '!=', doc.id),
                    ('document_type', '=', doc.document_type),
                    ('state', '!=', 'archived'),
                ])
                for other in mismatched:
                    if (other.holder_name
                            and other.holder_name.strip().lower()
                            != doc.holder_name.strip().lower()
                            and self._has_similar_holder(
                                doc.holder_name, other.holder_name,
                            )):
                        raise ValidationError(_(
                            'Holder name inconsistency detected.\n'
                            'Document "%s" has holder "%s", '
                            'but document "%s" has holder "%s".\n'
                            'Please verify the holder name.',
                            doc.name, doc.holder_name,
                            other.name, other.holder_name,
                        ))

    def _has_similar_holder(self, name1, name2):
        """Check if two holder names look like they refer to the same entity
        but are spelled differently."""
        # Very simple: check if one contains the other or vice versa
        n1 = name1.strip().lower()
        n2 = name2.strip().lower()
        if n1 == n2:
            return False
        # Fuzzy: shared word count > 50%
        words1 = set(n1.split())
        words2 = set(n2.split())
        if not words1 or not words2:
            return False
        common = words1 & words2
        return len(common) / min(len(words1), len(words2)) > 0.5
