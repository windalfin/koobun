# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GCGAuthorityMatrix(models.Model):
    """Authority Matrix / Delegation of Authority engine.

    Defines who can approve documents of a given type and within what
    monetary value range.
    """
    _name = 'gcg.authority.matrix'
    _inherit = ['mail.thread']
    _description = 'GCG Authority Matrix'
    _order = 'sequence, id'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    document_model = fields.Char(
        string='Document Model',
        required=True,
        help='Odoo model name this authority row applies to (e.g. upkeep.bpb).',
        tracking=True,
    )
    document_type_name = fields.Char(
        string='Document Type Name',
        help='Human-readable name for the document type.',
        tracking=True,
    )
    min_value = fields.Monetary(
        string='Minimum Value',
        currency_field='currency_id',
        help='Lower bound of the approval band (inclusive).',
    )
    max_value = fields.Monetary(
        string='Maximum Value',
        currency_field='currency_id',
        help='Upper bound of the approval band (inclusive).',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    approver_role_id = fields.Many2one(
        'res.groups',
        string='Approver Role',
        required=True,
        help='Security group whose members are authorised to approve.',
    )
    approver_role_2_id = fields.Many2one(
        'res.groups',
        string='Second Approver Role',
        help='Optional second security group for joint approval.',
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    version = fields.Integer(
        string='Version',
        default=1,
        tracking=True,
    )
    approved_date = fields.Datetime(
        string='Approved Date',
        tracking=True,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        tracking=True,
    )

    @api.constrains('min_value', 'max_value')
    def _check_value_range(self):
        for record in self:
            if record.min_value and record.max_value and record.min_value > record.max_value:
                raise ValidationError(_(
                    'Minimum value (%(min)s) must be less than or equal to '
                    'maximum value (%(max)s).',
                    min=record.min_value,
                    max=record.max_value,
                ))

    @api.constrains('approver_role_id', 'approver_role_2_id')
    def _check_distinct_roles(self):
        for record in self:
            if record.approver_role_id and record.approver_role_2_id and \
               record.approver_role_id == record.approver_role_2_id:
                raise ValidationError(_(
                    'The primary and secondary approver roles must be different.'
                ))

    @api.model
    def get_approvers_for_value(self, document_model, amount):
        """Return matching authority matrix rows for a given model and value.

        :param str document_model: The Odoo model name (e.g. 'upkeep.bpb')
        :param float amount: The monetary amount to check
        :returns: Recordset of matching gcg.authority.matrix rows
        """
        domain = [
            ('document_model', '=', document_model),
            ('is_active', '=', True),
        ]
        rows = self.search(domain, order='sequence')
        matching = self.browse()
        for row in rows:
            if row.min_value and amount < row.min_value:
                continue
            if row.max_value and amount > row.max_value:
                continue
            matching |= row
        return matching
