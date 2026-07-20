# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesMillReception(models.Model):
    """Mill reception record — captures the mill's weighbridge and sortasi
    results for a given SPB (Surat Pengantar Buah)."""
    _name = 'sales.mill_reception'
    _description = 'Mill Reception (Weighbridge & Sortasi)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reception_date desc, id desc'

    # ── Core ───────────────────────────────────────────────────
    spb_id = fields.Many2one(
        'transport.spb', string='SPB Reference',
        required=True, ondelete='restrict', tracking=True, index=True,
    )
    gross_kg = fields.Float(
        string='Gross Weight (kg)', digits=(12, 2), required=True,
        tracking=True,
    )
    sortasi_deduction_kg = fields.Float(
        string='Sortasi Deduction (kg)', digits=(12, 2), default=0.0,
        tracking=True,
    )
    deduction_reasons = fields.Text(
        string='Deduction Reasons',
        help='Detailed breakdown of sortasi deductions.',
        tracking=True,
    )
    mill_doc_ref = fields.Char(
        string='Mill Document Reference',
        help='Reference number from the mill weighbridge ticket.',
        tracking=True,
    )
    reception_date = fields.Date(
        string='Reception Date', required=True, default=fields.Date.context_today,
        tracking=True,
    )

    # ── Computed ───────────────────────────────────────────────
    sortasi_deduction_pct = fields.Float(
        string='Deduction (%)', digits=(5, 2),
        compute='_compute_deduction_pct', store=True,
    )
    accepted_net_kg = fields.Float(
        string='Accepted Net (kg)', digits=(12, 2),
        compute='_compute_accepted_net_kg', store=True,
    )

    # ── Computation Methods ────────────────────────────────────
    @api.depends('gross_kg', 'sortasi_deduction_kg')
    def _compute_deduction_pct(self):
        for rec in self:
            if rec.gross_kg and rec.gross_kg > 0:
                rec.sortasi_deduction_pct = (
                    rec.sortasi_deduction_kg / rec.gross_kg * 100.0
                )
            else:
                rec.sortasi_deduction_pct = 0.0

    @api.depends('gross_kg', 'sortasi_deduction_kg')
    def _compute_accepted_net_kg(self):
        for rec in self:
            rec.accepted_net_kg = max(
                0.0, (rec.gross_kg or 0.0) - (rec.sortasi_deduction_kg or 0.0)
            )

    # ── Constraints ────────────────────────────────────────────
    @api.constrains('gross_kg')
    def _check_gross_positive(self):
        for rec in self:
            if rec.gross_kg < 0:
                raise ValidationError(_(
                    'Gross weight must be positive.'
                ))

    @api.constrains('sortasi_deduction_kg', 'gross_kg')
    def _check_deduction_not_exceed_gross(self):
        for rec in self:
            if rec.sortasi_deduction_kg and rec.gross_kg:
                if rec.sortasi_deduction_kg > rec.gross_kg:
                    raise ValidationError(_(
                        'Sortasi deduction (%s kg) cannot exceed gross weight '
                        '(%s kg).',
                        rec.sortasi_deduction_kg, rec.gross_kg,
                    ))
