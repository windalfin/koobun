# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesMill(models.Model):
    """Customer master record — extends res.partner with mill-specific fields
    for TBS sales and contract management."""
    _name = 'sales.mill'
    _description = 'Sales Mill / Customer Master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        (
            'partner_uniq',
            'unique(partner_id)',
            'A partner can only be linked to one sales mill record!',
        ),
    ]

    # ── Core ───────────────────────────────────────────────────
    partner_id = fields.Many2one(
        'res.partner', string='Customer / Mill',
        required=True, ondelete='restrict', tracking=True, index=True,
    )
    name = fields.Char(
        string='Mill Name', related='partner_id.name',
        store=True, readonly=True,
    )
    pricing_basis = fields.Selection(
        selection=[
            ('market', 'Market Price'),
            ('contract', 'Contract Price'),
            ('disbun', 'Disbun (Government)'),
        ],
        string='Pricing Basis', required=True, default='market',
        tracking=True,
    )
    payment_terms = fields.Text(
        string='Payment Terms / Notes',
        tracking=True,
    )
    sortasi_rules = fields.Text(
        string='Sortasi Rules',
        help='Deduction rules and percentages applicable to this mill.',
        tracking=True,
    )
    is_active = fields.Boolean(
        string='Active', default=True, tracking=True,
    )

    # ── Helper ─────────────────────────────────────────────────
    @api.constrains('partner_id')
    def _check_partner_unique(self):
        """Ensure partner is not already linked to another sales.mill."""
        for rec in self:
            duplicate = self.search([
                ('partner_id', '=', rec.partner_id.id),
                ('id', '!=', rec.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    'Partner "%s" is already linked to sales mill "%s".',
                    rec.partner_id.display_name, duplicate.name,
                ))
