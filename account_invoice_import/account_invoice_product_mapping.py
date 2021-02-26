# coding: utf-8
# Copyright (C) 2021 Essent <http://www.essent.be>
# @author Stefan Rijnhart <stefan.rijnhart@dynapps.be>
# @author Robin Conjour <r.conjour@essent.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class AccountInvoiceProductMapping(models.Model):
    _name = 'account.invoice.product.mapping'
    _description = 'Productmapping for invoice products'

    account_analytic_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account')
    invoice_import_id = fields.Many2one('account.invoice.import.config')
    product_id = fields.Many2one('product.product')
    recognition_string = fields.Char(
        help='String to match products, the productname on the invoice line '
             'should contain this string.')
