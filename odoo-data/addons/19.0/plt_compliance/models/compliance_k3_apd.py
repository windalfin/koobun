# -*- coding: utf-8 -*-
from odoo import models, fields


class ComplianceK3APD(models.Model):
    """K3 APD / PPE issue records."""
    _name = 'compliance.k3_apd'
    _description = 'Catatan Penyerahan APD (Alat Pelindung Diri)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    date = fields.Date(
        string='Tanggal',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Pekerja',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    apd_type = fields.Selection([
        ('helmet', 'Helm (Safety Helmet)'),
        ('boots', 'Sepatu Safety (Boots)'),
        ('gloves', 'Sarung Tangan (Gloves)'),
        ('mask', 'Masker (Respirator)'),
        ('goggles', 'Kacamata (Safety Goggles)'),
        ('vest', 'Rompi Reflektif (Safety Vest)'),
        ('harness', 'Body Harness'),
        ('earplug', 'Penutup Telinga (Earplug)'),
        ('raincoat', 'Jas Hujan'),
        ('other', 'Lainnya'),
    ], string='Jenis APD', required=True, tracking=True)
    quantity_issued = fields.Integer(
        string='Jumlah Diserahkan',
        default=1,
        required=True,
        tracking=True,
    )
    condition = fields.Selection([
        ('new', 'Baru'),
        ('good', 'Baik'),
        ('damaged', 'Rusak'),
    ], string='Kondisi', default='good', required=True, tracking=True)
    notes = fields.Text(string='Catatan')