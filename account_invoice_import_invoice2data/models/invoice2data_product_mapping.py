# coding: utf-8
# Copyright (C) 2021 Essent <http://www.essent.be>
# @author Stefan Rijnhart <stefan.rijnhart@dynapps.be>
# @author Robin Conjour <r.conjour@essent.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class Invoice2dataProductMapping(models.Model):
    _name = 'invoice2data.product.mapping'
    _description = 'Productmapping for invoice2data products'

    account_analytic_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account')
    account_id = fields.Many2one(
        'account.account', 'Account')
    product_id = fields.Many2one('product.product')
    rec_name = fields.Char()
    tax_id = fields.Many2one(
        'account.tax', string='Taxes',
        domain=[('type_tax_use', 'in', ('all', 'purchase'))])
    template_id = fields.Many2one('invoice2data.template')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ Set account_id and tax_id based on the product_id. """
        self.account_id = self.product_id.property_account_expense
        self.tax_id = self.product_id.supplier_taxes_id
