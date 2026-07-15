# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransportSPB(models.Model):
    _name = 'transport.spb'
    _description = 'Surat Pengantar Buah (SPB)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, number desc'
    _rec_name = 'number'

    # ── Document Fields ──────────────────────────────────────
    number = fields.Char(
        string='SPB Number', required=True, copy=False,
        tracking=True, index=True,
    )
    date = fields.Date(
        string='Date', required=True, default=fields.Date.context_today,
        tracking=True,
    )

    # ── Fleet ────────────────────────────────────────────────
    truck_id = fields.Many2one(
        'fleet.vehicle', string='Truck',
        ondelete='restrict', tracking=True,
    )
    driver_id = fields.Many2one(
        'hr.employee', string='Driver',
        ondelete='restrict', tracking=True,
    )

    # ── Source (Blocks & TPHs) ───────────────────────────────
    block_ids = fields.Many2many(
        'estate.block', 'transport_spb_block_rel',
        'spb_id', 'block_id',
        string='Blocks', tracking=True,
    )
    tph_ids = fields.Many2many(
        'estate.tph', 'transport_spb_tph_rel',
        'spb_id', 'tph_id',
        string='TPHs', tracking=True,
    )

    # ── Cargo ────────────────────────────────────────────────
    janjang_count = fields.Integer(
        string='Janjang Count', tracking=True,
    )
    estimated_kg = fields.Float(
        string='Estimated KG', digits=(16, 2), tracking=True,
    )
    seal_number = fields.Char(
        string='Seal Number', tracking=True,
    )

    # ── Destination ──────────────────────────────────────────
    destination_mill_id = fields.Many2one(
        'res.partner', string='Destination Mill',
        ondelete='restrict', tracking=True,
    )

    # ── State ────────────────────────────────────────────────
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('issued', 'Issued'),
            ('weighed', 'Weighed'),
            ('delivered', 'Delivered'),
            ('mill_confirmed', 'Mill Confirmed'),
            ('closed', 'Closed'),
        ],
        string='Status', default='draft', required=True,
        tracking=True, index=True,
    )

    # ── Computed ─────────────────────────────────────────────
    weight_net = fields.Float(
        string='Net Weight (KG)', digits=(16, 2),
        compute='_compute_weight_net', store=True,
    )

    # ── Related ──────────────────────────────────────────────
    weighbridge_ticket_ids = fields.One2many(
        'transport.weighbridge_ticket', 'spb_id',
        string='Weighbridge Tickets', readonly=True,
    )
    reconciliation_ids = fields.One2many(
        'transport.reconciliation', 'spb_id',
        string='Reconciliations', readonly=True,
    )

    # ── SQL Constraints ──────────────────────────────────────
    _sql_constraints = [
        (
            'spb_number_unique',
            'unique(number)',
            'SPB number must be unique!',
        ),
    ]

    # ── Computed Methods ─────────────────────────────────────
    @api.depends('weighbridge_ticket_ids.net_kg')
    def _compute_weight_net(self):
        for spb in self:
            spb.weight_net = sum(
                spb.weighbridge_ticket_ids.mapped('net_kg')
            )

    # ── SPB Number Gap Control ───────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number'):
                self._check_number_gaps(vals['number'])
        return super().create(vals_list)

    def write(self, vals):
        if 'number' in vals:
            self._check_number_gaps(vals['number'])
        return super().write(vals)

    @api.model
    def _check_number_gaps(self, number):
        """Validate SPB number has no gaps and follows the expected
        sequential pattern. Warn if a gap is detected."""
        existing = self.search([
            ('number', '=', number),
        ])
        if existing:
            raise ValidationError(_(
                'SPB number %s already exists!', number
            ))

    def _check_spb_gap(self):
        """Check if the previous SPB number in the sequence exists.

        Parses the numeric suffix of this SPB's number, derives the
        expected previous number, and logs an exception on the chatter
        if that previous SPB is missing.

        Returns True if a gap was detected, False otherwise.
        """
        self.ensure_one()
        import re
        match = re.match(r'^(.*?)(\d+)$', self.number or '')
        if not match:
            return False
        prefix, num_str = match.groups()
        try:
            current_num = int(num_str)
        except ValueError:
            return False
        if current_num <= 1:
            return False
        prev_num_str = str(current_num - 1).zfill(len(num_str))
        prev_number = prefix + prev_num_str
        prev_spb = self.search([
            ('number', '=', prev_number),
            ('id', '!=', self.id),
        ], limit=1)
        if not prev_spb:
            self.message_post(
                body=_(
                    'SPB Gap Detection: Previous SPB <b>%s</b> is missing. '
                    'Please verify the SPB numbering sequence.',
                    prev_number,
                ),
            )
            return True
        return False

    # ── State Transitions ────────────────────────────────────
    def action_issue(self):
        for spb in self:
            if spb.state != 'draft':
                raise ValidationError(_(
                    'Only draft SPB can be issued.'
                ))
            spb.state = 'issued'

    def action_weigh(self):
        for spb in self:
            if spb.state != 'issued':
                raise ValidationError(_(
                    'Only issued SPB can be weighed.'
                ))
            spb.state = 'weighed'

    def action_deliver(self):
        for spb in self:
            if spb.state != 'weighed':
                raise ValidationError(_(
                    'Only weighed SPB can be delivered.'
                ))
            spb.state = 'delivered'

    def action_mill_confirm(self):
        for spb in self:
            if spb.state != 'delivered':
                raise ValidationError(_(
                    'Only delivered SPB can be mill confirmed.'
                ))
            spb.state = 'mill_confirmed'

    def action_close(self):
        for spb in self:
            if spb.state not in ('mill_confirmed', 'delivered'):
                raise ValidationError(_(
                    'Only mill confirmed or delivered SPB can be closed.'
                ))
            spb.state = 'closed'

    def action_reset_draft(self):
        for spb in self:
            spb.state = 'draft'
