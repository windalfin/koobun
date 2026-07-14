# -*- coding: utf-8 -*-
from odoo import models, fields, api


class GCGAuditLog(models.Model):
    """Immutable audit trail for all critical field changes.

    Records are append-only: once created they cannot be modified or deleted
    except through superuser administrative tools.
    """
    _name = 'gcg.audit.log'
    _description = 'GCG Audit Log'
    _order = 'changed_at desc, id desc'

    model_name = fields.Char(
        string='Model Name',
        required=True,
        index=True,
        readonly=True,
    )
    record_id = fields.Integer(
        string='Record ID',
        required=True,
        readonly=True,
    )
    record_name = fields.Char(
        string='Record Name',
        readonly=True,
    )
    field_name = fields.Char(
        string='Field Name',
        required=True,
        readonly=True,
    )
    old_value = fields.Text(
        string='Old Value',
        readonly=True,
    )
    new_value = fields.Text(
        string='New Value',
        readonly=True,
    )
    changed_by = fields.Many2one(
        'res.users',
        string='Changed By',
        readonly=True,
        default=lambda self: self.env.user,
    )
    changed_at = fields.Datetime(
        string='Changed At',
        readonly=True,
        default=fields.Datetime.now,
    )
    transaction_type = fields.Selection(
        [
            ('create', 'Create'),
            ('write', 'Write'),
            ('unlink', 'Unlink'),
        ],
        string='Transaction Type',
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Allow creation but prevent modification afterward."""
        return super(GCGAuditLog, self).create(vals_list)

    def write(self, vals):
        """Prevent any modification to existing audit log records."""
        if self:
            raise self.env['ir.rule'].sudo()._make_access_error(
                'write', self._name)
        # Allow empty recordset (no-op write)
        return True

    def unlink(self):
        """Prevent deletion of audit log records."""
        if self:
            raise self.env['ir.rule'].sudo()._make_access_error(
                'unlink', self._name)
        # Allow empty recordset (no-op unlink)
        return True

    @api.model
    def log_change(self, model_name, record_id, field_name,
                   old_value, new_value, record_name=None,
                   transaction_type='write'):
        """Convenience method to create an audit log entry.

        :param str model_name: Technical name of the model
        :param int record_id: ID of the record that changed
        :param str field_name: Name of the field that changed
        :param str old_value: Previous value
        :param str new_value: New value
        :param str record_name: Display name of the record (optional)
        :param str transaction_type: One of 'create', 'write', 'unlink'
        :returns: The created gcg.audit.log record
        """
        return self.create({
            'model_name': model_name,
            'record_id': record_id,
            'record_name': record_name,
            'field_name': field_name,
            'old_value': str(old_value) if old_value is not None else '',
            'new_value': str(new_value) if new_value is not None else '',
            'transaction_type': transaction_type,
        })
