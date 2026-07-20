# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GCGSodRule(models.Model):
    """Segregation-of-Duties (SoD) conflict rules.

    Defines pairs of security roles that must not be held by the same user,
    either blocking assignment entirely or raising a warning.
    """
    _name = 'gcg.sod.rule'
    _description = 'GCG Segregation of Duties Rule'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    role_a_id = fields.Many2one(
        'res.groups',
        string='Role A',
        required=True,
        help='First role in the conflict pair.',
    )
    role_b_id = fields.Many2one(
        'res.groups',
        string='Role B',
        required=True,
        help='Second role in the conflict pair.',
    )
    conflict_description = fields.Text(
        string='Conflict Description',
        required=True,
        help='Explanation of why these two roles conflict.',
    )
    document_model_ids = fields.Char(
        string='Document Models',
        help='Comma-separated list of Odoo model names where this SoD '
             'rule applies. Leave empty to apply to all models.',
    )
    is_blocking = fields.Boolean(
        string='Block Assignment',
        default=True,
        help='If True, assignment of the second role to a user already '
             'holding the first is blocked. If False, only a warning is shown.',
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        (
            'unique_sod_pair',
            'UNIQUE(role_a_id, role_b_id)',
            'A SoD rule for this role pair already exists. '
            'Use a single rule or define distinct pairs.'
        ),
    ]

    @api.constrains('role_a_id', 'role_b_id')
    def _check_different_roles(self):
        for record in self:
            if record.role_a_id == record.role_b_id:
                raise ValidationError(_(
                    'Role A and Role B must be different to define a conflict.'
                ))

    @api.model
    def check_conflict(self, user_id, role_id):
        """Check if assigning *role_id* to *user_id* would violate any SoD rule.

        :param int user_id: ID of the res.users record
        :param int role_id: ID of the res.groups record being assigned
        :returns: list of dicts with keys 'rule', 'is_blocking'
        """
        user = self.env['res.users'].browse(user_id)
        current_role_ids = set(user.group_ids.ids)

        if role_id in current_role_ids:
            return []  # Already has the role, re-assignment is fine

        conflicts = []
        rules = self.search([
            ('is_active', '=', True),
            '|',
            ('role_a_id', '=', role_id),
            ('role_b_id', '=', role_id),
        ])
        for rule in rules:
            if rule.role_a_id.id == role_id:
                other_role_id = rule.role_b_id.id
            else:
                other_role_id = rule.role_a_id.id

            if other_role_id in current_role_ids:
                conflicts.append({
                    'rule': rule,
                    'is_blocking': rule.is_blocking,
                })

        return conflicts
