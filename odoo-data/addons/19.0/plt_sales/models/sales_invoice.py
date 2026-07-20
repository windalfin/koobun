# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesInvoice(models.Model):
    """Auto-generated invoice line aggregating multiple SPBs for a mill
    within a billing period."""
    _name = 'sales.invoice'
    _description = 'Sales Invoice Line (Mill Billing)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'period_start desc, id desc'

    # ── Core ───────────────────────────────────────────────────
    mill_id = fields.Many2one(
        'sales.mill', string='Mill / Customer', required=True,
        ondelete='restrict', tracking=True, index=True,
    )
    period_start = fields.Date(
        string='Period Start', required=True, tracking=True,
    )
    period_end = fields.Date(
        string='Period End', required=True, tracking=True,
    )
    spb_ids = fields.Many2many(
        'transport.spb', string='SPBs',
        help='SPBs included in this invoice period.',
    )
    applicable_price_id = fields.Many2one(
        'sales.tbs_price', string='Applicable Price',
        ondelete='restrict', tracking=True,
    )
    invoice_id = fields.Many2one(
        'account.move', string='Customer Invoice',
        ondelete='restrict', tracking=True,
        copy=False,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('invoiced', 'Invoiced'),
        ],
        string='State', default='draft', required=True, tracking=True,
    )

    # ── Computed ───────────────────────────────────────────────
    total_accepted_kg = fields.Float(
        string='Total Accepted (kg)', digits=(12, 2),
        compute='_compute_total_accepted_kg', store=True,
    )
    line_amount = fields.Float(
        string='Line Amount', digits=(12, 2),
        compute='_compute_line_amount', store=True,
    )

    # ── Computation Methods ────────────────────────────────────
    @api.depends('spb_ids')
    def _compute_total_accepted_kg(self):
        """Sum accepted net kg from mill reception records linked to the SPBs."""
        for rec in self:
            if rec.spb_ids:
                receptions = self.env['sales.mill_reception'].search([
                    ('spb_id', 'in', rec.spb_ids.ids),
                ])
                rec.total_accepted_kg = sum(
                    receptions.mapped('accepted_net_kg')
                )
            else:
                rec.total_accepted_kg = 0.0

    @api.depends('total_accepted_kg', 'applicable_price_id.price_per_kg')
    def _compute_line_amount(self):
        for rec in self:
            if rec.total_accepted_kg and rec.applicable_price_id:
                price = rec.applicable_price_id.price_per_kg
                rec.line_amount = rec.total_accepted_kg * price
            else:
                rec.line_amount = 0.0

    # ── Constraints ────────────────────────────────────────────
    @api.constrains('period_start', 'period_end')
    def _check_period_dates(self):
        for rec in self:
            if rec.period_start and rec.period_end \
                    and rec.period_start > rec.period_end:
                raise ValidationError(_(
                    'Period Start cannot be after Period End.'
                ))

    # ── Actions ────────────────────────────────────────────────
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_invoice(self):
        self.write({'state': 'invoiced'})

    def action_draft(self):
        self.write({'state': 'draft'})
