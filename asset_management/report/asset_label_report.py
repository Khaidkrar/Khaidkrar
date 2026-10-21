# -*- coding: utf-8 -*-
from collections import defaultdict
from urllib.parse import quote_plus
from odoo import models


def _prepare_data(env, data):
    """Prepare data for asset label reports - Odoo 15 version"""
    layout_wizard = env['asset.label.layout'].browse(data.get('layout_wizard'))
    Asset = env['asset.management']
    
    if not layout_wizard:
        return {}

    total = 0
    qty_by_asset_in = data.get('quantity_by_asset')
    # Search for assets all at once, ordered by name desc
    assets = Asset.search([('id', 'in', [int(a) for a in qty_by_asset_in.keys()])], order='name desc')
    
    # Flatten the data structure: create a list of items to print
    # Each item is a dict with asset, barcode, and quantity
    label_items = []
    for asset in assets:
        q = qty_by_asset_in[str(asset.id)]
        # Use barcode if available, otherwise use asset name as barcode
        barcode_value = asset.barcode if asset.barcode else asset.name
        # Add one entry per label to print
        for _ in range(q):
            label_items.append({
                'asset': asset,
                'barcode': barcode_value,
            })
        total += q

    # Get custom dimensions if provided
    custom_columns = data.get('custom_columns')
    custom_rows = data.get('custom_rows')
    
    # Use custom dimensions if provided, otherwise use wizard dimensions
    columns = custom_columns if custom_columns else layout_wizard.columns
    rows = custom_rows if custom_rows else layout_wizard.rows
    
    # Get company for template
    company = env.company
    
    # Get price_included from data, default to True for formats that should include price
    price_included = data.get('price_included')
    if price_included is None:
        # Default to True if not specified (for 2x7, 4x7, 4x12 with price formats)
        price_included = True
    
    return {
        'label_items': label_items,
        'total_items': len(label_items),  # Total count for template use
        'page_numbers': (total - 1) // (rows * columns) + 1 if (rows * columns) > 0 else 1,
        'price_included': price_included,
        'columns': columns,
        'rows': rows,
        'red_band_color': data.get('red_band_color', '#dc3545'),
        'quote_plus': quote_plus,  # Make quote_plus available in QWeb templates
        'company': company,  # Add company to template context
        'env': env,  # Add env for backward compatibility
    }


class ReportAssetTemplateLabel2x7(models.AbstractModel):
    _name = 'report.asset_management.report_assettemplatelabel2x7'
    _description = 'Asset Label Report 2x7'

    def _get_report_values(self, docids, data=None):
        return _prepare_data(self.env, data or {})


class ReportAssetTemplateLabel4x7(models.AbstractModel):
    _name = 'report.asset_management.report_assettemplatelabel4x7'
    _description = 'Asset Label Report 4x7'

    def _get_report_values(self, docids, data=None):
        return _prepare_data(self.env, data or {})


class ReportAssetTemplateLabel4x12(models.AbstractModel):
    _name = 'report.asset_management.report_assettemplatelabel4x12'
    _description = 'Asset Label Report 4x12'

    def _get_report_values(self, docids, data=None):
        return _prepare_data(self.env, data or {})


class ReportAssetTemplateLabel4x12NoPrice(models.AbstractModel):
    _name = 'report.asset_management.report_assettemplatelabel4x12noprice'
    _description = 'Asset Label Report 4x12 No Price'

    def _get_report_values(self, docids, data=None):
        return _prepare_data(self.env, data or {})


class ReportAssetTemplateLabelCustom(models.AbstractModel):
    _name = 'report.asset_management.report_assettemplatelabel_custom'
    _description = 'Asset Label Report Custom Columns'

    def _get_report_values(self, docids, data=None):
        return _prepare_data(self.env, data or {})

