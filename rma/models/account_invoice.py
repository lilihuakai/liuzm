# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_invoice(models.Model):
    _inherit = ['account.invoice']

    # 构建退款发票明细
    def _refund_invoice_claimed_lines(self, cr, uid, lines, origin, account_id, partner_id, context=None):
        """ Convert records to dict of values suitable for one2many line creation

            :param recordset lines: records to convert
            :return: list of command tuple for one2many line creation [(0, 0, dict of valueis), ...]
        """
        result = []
        for line in lines:
            values = {}
            values['name'] = line.name
            values['origin'] = origin
            values['quantity'] = line.product_returned_quantity
            values['account_id'] = account_id
            values['partner_id'] = partner_id
            values['company_id'] = line.company_id.id
            values['product_id'] = line.product_id.id
            values['price_unit'] = line.unit_sale_price
            values['display_name'] = line.display_name
            values['price_subtotal'] = line.return_value
            result.append((0, 0, values))
        return result

    def _prepare_claim_refund(self, cr, uid, claim_id, date=None, period_id=None, description=None, journal_id=None, context=None):
        values = {}
        account_id = 0
        claim_obj = self.pool.get('crm.claim')
        invoice_line_obj = self.pool.get('account.invoice.line')
        if context is None:
            context = {}

        # 获取对应的销售订单ID
        cr.execute('SELECT rel.order_id ' \
                'FROM sale_order_claim_rel AS rel ' \
                'WHERE rel.claim_id = \'' + str(claim_id) +'\'')
        order_id = cr.fetchall()

        # 从相关发票中获取参数
        orders = self.pool.get('sale.order').browse(cr, uid, order_id[0], context=context)
        for invoice in self.browse(cr, uid, orders.invoice_ids.id, context=context):
            # values['tax_line'] = 
            values['account_id'] = invoice.account_id.id
            values['currency_id'] = invoice.currency_id.id
            values['payment_term'] = invoice.payment_term.id
            values['fiscal_position'] = invoice.fiscal_position.id
            for line in invoice_line_obj.browse(cr, uid, invoice.invoice_line.ids, context=context):
                account_id = line.account_id.id
                break
            break

        # 从售后单中获取参数
        for claim in claim_obj.browse(cr, uid, claim_id, context=context):
            values['origin'] = claim.code
            # values['user_id'] = 
            # values['reference'] = 
            values['partner_id'] = claim.partner_id.id
            values['company_id'] = claim.company_id.id
            values['invoice_line'] = self._refund_invoice_claimed_lines(cr, uid, 
                claim.claim_line_ids, 
                claim.code, 
                account_id, 
                claim.partner_id.id, 
                context=context)

        if period_id:
            values['period_id'] = period_id
        if description:
            values['name'] = description
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            values['journal_id'] = journal.id
        else:
            raise osv.except_osv(_('Error!'), _('The %s is empty!') % (journal_id))
        values['type'] = 'out_refund'
        values['state'] = 'draft'
        values['number'] = False
        values['claim_id'] = claim_id
        values['date_invoice'] = date

        return values

    def claimed_refund(self, cr, uid, ids, date=None, period_id=None, description=None, journal_id=None, context=None):
        claim_obj = self.pool.get('crm.claim')
        if context is None:
            context = {}

        for claim in claim_obj.browse(cr, uid, context.get('active_ids'), context=context):
            # create the new invoice
            values = self._prepare_claim_refund(cr, uid, claim.id, date, period_id, description, journal_id, context=context)
            new_invoice = self.create(cr, uid, values, context=context)
        return new_invoice

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
