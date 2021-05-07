# coding: utf-8
# Copyright (C) 2021 Essent <http://www.essent.be>
# @author Stefan Rijnhart <stefan.rijnhart@dynapps.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# @author Robin Conjour <r.conjour@essent.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import logging

logger = logging.getLogger(__name__)


class AccountInvoiceImportError(models.TransientModel):
    _name = 'account.invoice.import.error'
    _description = 'Wizard to show errors after completion'

    @api.multi
    def view_invoice(self):
        """ Method to redirect to the invoice view. """
        self.ensure_one()

        invoice_id = self.env.context.get('invoice_id')
        if not invoice_id:
            raise UserError(_("No invoice ID available, wizard failed!"))

        iaao = self.env['ir.actions.act_window']
        action = iaao.for_xml_id('account', 'action_invoice_tree2')
        action.update({
            'view_mode': 'form,tree,calendar,graph',
            'views': False,
            'res_id': invoice_id,
        })
        return action
