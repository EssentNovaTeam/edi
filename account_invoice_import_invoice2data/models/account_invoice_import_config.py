# coding: utf-8
# Copyright (C) 2021 Essent <http://www.essent.be>
# @author Stefan Rijnhart <stefan.rijnhart@dynapps.be>
# @author Robin Conjour <r.conjour@essent.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class AccountInvoiceImportConfig(models.Model):
    _inherit = 'account.invoice.import.config'

    # Extend invoice_line_methods with `product_mapping`
    invoice_line_method = fields.Selection([
        ('1line_no_product', 'Single Line, No Product'),
        ('1line_static_product', 'Single Line, Static Product'),
        ('nline_no_product', 'Multi Line, No Product'),
        ('nline_static_product', 'Multi Line, Static Product'),
        ('nline_auto_product', 'Multi Line, Auto-selected Product'),
        ('product_mapping', 'Multi Line, Product mapping template'),
        ])
