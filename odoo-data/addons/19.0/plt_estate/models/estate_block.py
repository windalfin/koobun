# -*- coding: utf-8 -*-
import json
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EstateBlock(models.Model):
    _name = 'estate.block'
    _description = 'Block'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ── Basic Fields ──────────────────────────────────────────
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    afdeling_id = fields.Many2one(
        'estate.afdeling', string='Afdeling', required=True,
        ondelete='restrict', tracking=True,
    )
    estate_id = fields.Many2one(
        'estate.estate', string='Estate', related='afdeling_id.estate_id',
        store=True, readonly=True,
    )
    area_ha_planted = fields.Float(
        string='Planted Area (ha)', digits=(16, 4), tracking=True,
    )
    area_ha_total = fields.Float(
        string='Total Area (ha)', digits=(16, 4), tracking=True,
    )
    tahun_tanam = fields.Integer(string='Planting Year', tracking=True)
    seed_source = fields.Char(string='Seed Source', tracking=True)
    SPH = fields.Integer(string='SPH (Stand per Hectare)', tracking=True)
    planting_density = fields.Integer(string='Planting Density', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    # ── Classifications ───────────────────────────────────────
    soil_class = fields.Selection(
        selection=[
            ('mineral', 'Mineral'),
            ('gambut', 'Gambut'),
            ('pasir', 'Pasir'),
            ('liat', 'Liat'),
        ],
        string='Soil Class', tracking=True,
    )
    topography_class = fields.Selection(
        selection=[
            ('datar', 'Datar'),
            ('bergelombang', 'Bergelombang'),
            ('berbukit', 'Berbukit'),
            ('curam', 'Curam'),
        ],
        string='Topography Class', tracking=True,
    )

    # ── Status ────────────────────────────────────────────────
    status = fields.Selection(
        selection=[
            ('tbm', 'TBM (Immature)'),
            ('tm', 'TM (Mature)'),
        ],
        string='Status', default='tbm', required=True, tracking=True,
    )

    # ── GIS ───────────────────────────────────────────────────
    polygon_geojson = fields.Text(
        string='Polygon (GeoJSON)', tracking=True,
    )

    # ── Analytic Account ──────────────────────────────────────
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account',
        readonly=True, copy=False,
    )

    # ── Computed Fields ───────────────────────────────────────
    computed_gis_area = fields.Float(
        string='Computed GIS Area (ha)', digits=(16, 4),
        compute='_compute_gis_area', store=False,
    )
    area_variance_pct = fields.Float(
        string='Area Variance (%)', digits=(16, 2),
        compute='_compute_variance_pct', store=False,
    )

    # ── Status History ────────────────────────────────────────
    status_history_ids = fields.One2many(
        'estate.block.status.history', 'block_id',
        string='Status History', readonly=True,
    )

    # ── SQL Constraints ───────────────────────────────────────
    _sql_constraints = [
        (
            'code_afdeling_unique',
            'unique(code, afdeling_id)',
            'Block code must be unique per afdeling!',
        ),
    ]

    # ── Constraints ──────────────────────────────────────────
    @api.constrains('area_ha_total', 'area_ha_planted')
    def _check_area_positive(self):
        for block in self:
            if block.area_ha_total and block.area_ha_total <= 0:
                raise ValidationError(_(
                    'Total area must be positive for block %s.', block.code
                ))
            if block.area_ha_planted and block.area_ha_planted <= 0:
                raise ValidationError(_(
                    'Planted area must be positive for block %s.', block.code
                ))
            if (block.area_ha_total and block.area_ha_planted
                    and block.area_ha_planted > block.area_ha_total):
                raise ValidationError(_(
                    'Planted area (%s ha) cannot exceed total area (%s ha) '
                    'for block %s.',
                    block.area_ha_planted, block.area_ha_total, block.code,
                ))

    # ── Computed Methods ──────────────────────────────────────
    @api.depends('polygon_geojson')
    def _compute_gis_area(self):
        """Compute GIS area from GeoJSON polygon using a simplified
        area calculation.  In a full implementation this would use
        a GIS library or pyproj for accurate geodetic area."""
        for block in self:
            area = 0.0
            if block.polygon_geojson:
                try:
                    geojson = json.loads(block.polygon_geojson)
                    coords = self._extract_coordinates(geojson)
                    if coords:
                        area = self._polygon_area_ha(coords)
                except (json.JSONDecodeError, KeyError, TypeError) as exc:
                    _logger.warning(
                        'Invalid GeoJSON for block %s: %s',
                        block.code, exc,
                    )
            block.computed_gis_area = area

    def _extract_coordinates(self, geojson):
        """Extract polygon coordinates from GeoJSON geometry."""
        if geojson.get('type') == 'Polygon':
            return geojson.get('coordinates', [[]])[0]
        if geojson.get('type') == 'Feature':
            geom = geojson.get('geometry', {})
            if geom.get('type') == 'Polygon':
                return geom.get('coordinates', [[]])[0]
        return None

    def _polygon_area_ha(self, coords):
        """Calculate area in hectares using Shoelace formula (planar).
        Approximate: assume coordinates are in WGS84 degrees and
        apply a rough lat/lon → metre conversion."""
        if len(coords) < 3:
            return 0.0
        # Shoelace area in square degrees → approximate m² → ha
        area_sqdeg = 0.0
        n = len(coords)
        for i in range(n):
            x1, y1 = coords[i][0], coords[i][1]
            x2, y2 = coords[(i + 1) % n][0], coords[(i + 1) % n][1]
            area_sqdeg += (x1 * y2 - x2 * y1)
        area_sqdeg = abs(area_sqdeg) / 2.0
        # Approximate: 1 deg lat ≈ 111320 m, 1 deg lon ≈ 111320 * cos(lat)
        # Use average latitude
        avg_lat = sum(c[1] for c in coords) / n
        import math
        m_per_deg_lat = 111320.0
        m_per_deg_lon = 111320.0 * math.cos(math.radians(avg_lat))
        area_m2 = area_sqdeg * m_per_deg_lat * m_per_deg_lon
        return area_m2 / 10000.0  # m² → hectares

    @api.depends('area_ha_total', 'computed_gis_area')
    def _compute_variance_pct(self):
        for block in self:
            if (block.area_ha_total and block.area_ha_total > 0
                    and block.computed_gis_area):
                block.area_variance_pct = (
                    abs(block.area_ha_total - block.computed_gis_area)
                    / block.area_ha_total * 100.0
                )
            else:
                block.area_variance_pct = 0.0

    # ── Onchange ─────────────────────────────────────────────
    @api.onchange('tahun_tanam')
    def _onchange_tahun_tanam(self):
        """Auto-set planting_density from configuraiton when planting year
        changes.  In production this would read from a config model."""
        if self.tahun_tanam:
            # Default SPH-based density lookup — placeholder for config model
            self.planting_density = 143  # standard oil palm density

    # ── Create: Auto-create analytic account ──────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code') and not vals.get('analytic_account_id'):
                estate_id = vals.get('estate_id')
                if not estate_id and vals.get('afdeling_id'):
                    # Resolve estate from afdeling
                    afd = self.env['estate.afdeling'].browse(
                        vals['afdeling_id'],
                    )
                    estate_id = afd.estate_id.id
                vals['analytic_account_id'] = self.env[
                    'account.analytic.account'
                ].create({
                    'name': 'BLK-%s' % vals['code'],
                    'plan_id': 1,
                }).id
        return super().create(vals_list)

    # ── Status Change ─────────────────────────────────────────
    def action_set_tm(self, date):
        """Change block status to TM (Mature) and create a status history
        record."""
        self.ensure_one()
        if self.status == 'tm':
            return
        self.env['estate.block.status.history'].create({
            'block_id': self.id,
            'date_from': date,
            'status': 'tm',
            'approved_by': self.env.uid,
        })
        self.status = 'tm'


class EstateBlockStatusHistory(models.Model):
    _name = 'estate.block.status.history'
    _description = 'Block Status History'
    _order = 'date_from desc, id desc'

    block_id = fields.Many2one(
        'estate.block', string='Block', required=True,
        ondelete='cascade', index=True,
    )
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date')
    status = fields.Selection(
        selection=[
            ('tbm', 'TBM (Immature)'),
            ('tm', 'TM (Mature)'),
        ],
        string='Status', required=True,
    )
    approved_by = fields.Many2one(
        'res.users', string='Approved By',
    )
    effective = fields.Boolean(
        string='Effective', default=True,
        help='Whether this status change is currently effective.',
    )
