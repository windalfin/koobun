# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransportWeighbridgeTicket(models.Model):
    _name = 'transport.weighbridge_ticket'
    _description = 'Weighbridge Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'timestamp desc, id desc'

    # ── Link to SPB ──────────────────────────────────────────
    spb_id = fields.Many2one(
        'transport.spb', string='SPB', required=True,
        ondelete='restrict', index=True, tracking=True,
    )

    # ── Weights ──────────────────────────────────────────────
    gross_kg = fields.Float(
        string='Gross Weight (KG)', digits=(16, 2),
        tracking=True,
    )
    tare_kg = fields.Float(
        string='Tare Weight (KG)', digits=(16, 2),
        tracking=True,
    )
    net_kg = fields.Float(
        string='Net Weight (KG)', digits=(16, 2),
        compute='_compute_net_kg', store=True,
    )

    # ── Metadata ─────────────────────────────────────────────
    timestamp = fields.Datetime(
        string='Timestamp', default=fields.Datetime.now,
        tracking=True,
    )
    operator_id = fields.Many2one(
        'res.users', string='Operator',
        default=lambda self: self.env.uid,
        tracking=True,
    )

    # ── Mode ─────────────────────────────────────────────────
    mode = fields.Selection(
        selection=[
            ('auto', 'Auto (Estate Estimate)'),
            ('manual', 'Manual'),
        ],
        string='Mode', default='auto', required=True,
        tracking=True,
    )

    # ── Manual Approval ──────────────────────────────────────
    manual_approved = fields.Boolean(
        string='Manual Approved', default=False,
        tracking=True,
    )
    approved_by = fields.Many2one(
        'res.users', string='Approved By',
        tracking=True,
    )

    # ── Computed Methods ─────────────────────────────────────
    @api.depends('gross_kg', 'tare_kg')
    def _compute_net_kg(self):
        for ticket in self:
            if ticket.gross_kg and ticket.tare_kg:
                ticket.net_kg = ticket.gross_kg - ticket.tare_kg
            else:
                ticket.net_kg = 0.0

    # ── Constraints ──────────────────────────────────────────
    @api.constrains('gross_kg', 'tare_kg')
    def _check_weights_positive(self):
        for ticket in self:
            if ticket.gross_kg is not None and ticket.gross_kg < 0:
                raise ValidationError(_(
                    'Gross weight cannot be negative.'
                ))
            if ticket.tare_kg is not None and ticket.tare_kg < 0:
                raise ValidationError(_(
                    'Tare weight cannot be negative.'
                ))
            if (ticket.gross_kg is not None and ticket.tare_kg is not None
                    and ticket.tare_kg > ticket.gross_kg):
                raise ValidationError(_(
                    'Tare weight cannot exceed gross weight.'
                ))

    @api.constrains('mode', 'manual_approved')
    def _check_manual_approval(self):
        """Manual mode tickets require approval from Estate Manager."""
        for ticket in self:
            if ticket.mode == 'manual' and not ticket.manual_approved:
                raise ValidationError(_(
                    'Manual weighbridge tickets require Estate Manager '
                    'approval. Please set manual_approved and approved_by.'
                ))

    # ── Actions ──────────────────────────────────────────────
    def action_approve_manual(self):
        for ticket in self:
            if ticket.mode != 'manual':
                raise ValidationError(_(
                    'Only manual mode tickets need approval.'
                ))
            ticket.manual_approved = True
            ticket.approved_by = self.env.uid
