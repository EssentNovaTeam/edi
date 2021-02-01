# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, tools, _
from openerp.exceptions import Warning as UserError
import os
from tempfile import mkstemp
import pkg_resources
import logging
logger = logging.getLogger(__name__)

try:
    from invoice2data.main import extract_data
    from invoice2data.template import read_templates
    from invoice2data.main import logger as loggeri2data
except ImportError:
    logger.debug('Cannot import invoice2data')


class AccountInvoiceImport(models.TransientModel):
    _inherit = 'account.invoice.import'

    @api.model
    def fallback_parse_pdf_invoice(self, file_data):
        '''This method must be inherited by additionnal modules with
        the same kind of logic as the account_bank_statement_import_*
        modules'''
        return self.invoice2data_parse_invoice(file_data)

    @api.model
    def invoice2data_parse_invoice(self, file_data):
        logger.info('Trying to analyze PDF invoice with invoice2data lib')
        fd, file_name = mkstemp()
        try:
            os.write(fd, file_data)
        finally:
            os.close(fd)
        # Transfer log level of Odoo to invoice2data
        loggeri2data.setLevel(logger.getEffectiveLevel())
        local_templates_dir = tools.config.get(
            'invoice2data_templates_dir', False)
        logger.debug(
            'invoice2data local_templates_dir=%s', local_templates_dir)
        templates = []
        if local_templates_dir and os.path.isdir(local_templates_dir):
            templates += read_templates(local_templates_dir)
        exclude_built_in_templates = tools.config.get(
            'invoice2data_exclude_built_in_templates', False)
        if not exclude_built_in_templates:
            templates += read_templates(
                pkg_resources.resource_filename('invoice2data', 'templates'))

        templates += self.env['invoice2data.template'].get_templates('purchase_invoice')

        logger.debug(
            'Calling invoice2data.extract_data with templates=%s',
            templates)

        try:
            invoice2data_res = extract_data(file_name, templates=templates)
        except Exception, e:
            raise UserError(_(
                "PDF Invoice parsing failed. Error message: %s") % e)
        if not invoice2data_res:
            raise UserError(_(
                "This PDF invoice doesn't match a known template of "
                "the invoice2data lib."))
        logger.info(
            'Result of invoice2data PDF extraction: %s', invoice2data_res)
        return self.invoice2data_to_parsed_inv(invoice2data_res)

    @api.model
    def invoice2data_to_parsed_inv(self, invoice2data_res):
        parsed_inv = {
            'partner': {
                'vat': invoice2data_res.get('vat'),
                'name': invoice2data_res.get('partner_name'),
                'email': invoice2data_res.get('partner_email'),
                'website': invoice2data_res.get('partner_website'),
                'siren': invoice2data_res.get('siren'),
                },
            'currency': {
                'iso': invoice2data_res.get('currency'),
                },
            'amount_total': invoice2data_res.get('amount'),
            'invoice_number': invoice2data_res.get('invoice_number'),
            'date': invoice2data_res.get('date'),
            'date_due': invoice2data_res.get('date_due'),
            'date_start': invoice2data_res.get('date_start'),
            'date_end': invoice2data_res.get('date_end'),
            'description': invoice2data_res.get('description'),
            'mapping_lines': invoice2data_res.get('lines', [])
            }
        if 'amount_untaxed' in invoice2data_res:
            parsed_inv['amount_untaxed'] = invoice2data_res['amount_untaxed']
        if 'amount_tax' in invoice2data_res:
            parsed_inv['amount_tax'] = invoice2data_res['amount_tax']
        return parsed_inv

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv):
        """ Extend invoice with line mapping. """
        vals = super(AccountInvoiceImport, self)._prepare_create_invoice_vals(
            parsed_inv)
        template = self.env['invoice2data.template'].search([
            ('related_partner.name', '=', parsed_inv.get('partner')['name'])
        ])
        if parsed_inv.get('mapping_lines'):
            il_vals = []

            # Get default account_id based on the partner
            partner_account = template.related_partner.default_account_id
            for line in parsed_inv.get('mapping_lines'):
                match = False
                for prod in template.product_mapping:
                    if prod.rec_name in line['description']:
                        match = True
                        # Determine account_id based on the mapping line
                        if prod.account_id:
                            product_account = prod.account_id
                        else:
                            product_account = (prod.product_id.
                                               property_account_expense)

                        # Create invoice line based on the matched product
                        il_vals.append(
                            (0, False, {
                                'product_id': prod.product_id.id,
                                'name': line['description'],
                                'account_id': (
                                    product_account.id if product_account
                                    else partner_account.id),
                                'account_analytic_id':
                                    prod.account_analytic_id.id,
                                'invoice_line_tax_id': [
                                    (6, 0, [prod.tax_id.id])],
                                'quantity': 1,
                                'price_unit': line['price_unit']
                            }))
                        # Be sure that we add a line only once
                        break

                if not match:
                    if not partner_account:
                        # No product match, and account is missing on the
                        # partner
                        raise UserError(
                            _('No default account set for res.partner#(%s)' %
                              template.related_partner.id))

                    # No match, create line without product
                    il_vals.append(
                        (0, False, {
                            'name': line['description'],
                            'account_id': partner_account.id,
                            'quantity': 1,
                            'price_unit': line['price_unit']
                        }))

            vals['invoice_line'] = il_vals

        return vals
