# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class sale_order(osv.osv):
    _name = "website_myaccount_base.myaddress"

    _columns = {
        'name': fields.char('Order Reference', required=True, copy=False,
            readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True),
        'origin': fields.char('Source Document', help="Reference of the document that generated this sales order request."),
        'client_order_ref': fields.char('Reference/Description', copy=False),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'date_order': fields.datetime('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False),
        'create_date': fields.datetime('Creation Date', readonly=True, select=True, help="Date on which sales order is created."),
        'date_confirm': fields.date('Confirmation Date', readonly=True, select=True, help="Date on which sales order is confirmed.", copy=False),
        'user_id': fields.many2one('res.users', 'Salesperson', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
        'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Invoice address for current sales order."),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order."),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""This field controls how invoice and delivery operations are synchronized."""),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order."),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Currency", readonly=True, required=True),
        'project_id': fields.many2one('account.analytic.account', 'Contract / Analytic', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="The analytic account related to a sales order."),

        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=True),
        'invoice_ids': fields.many2many('account.invoice', 'sale_order_invoice_rel', 'order_id', 'invoice_id', 'Invoices', readonly=True, copy=False, help="This is the list of invoices that have been generated for this sales order. The same sales order may have been invoiced in several times (by line for example)."),
        'invoiced_rate': fields.function(_invoiced_rate, string='Invoiced Ratio', type='float'),
        'invoiced': fields.function(_invoiced, string='Paid',
            fnct_search=_invoiced_search, type='boolean', help="It indicates that an invoice has been paid."),
        'invoice_exists': fields.function(_invoice_exists, string='Invoiced',
            fnct_search=_invoiced_search, type='boolean', help="It indicates that sales order has at least one invoice."),
        'note': fields.text('Terms and conditions'),

        'amount_untaxed': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),

        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position'),
        'company_id': fields.many2one('res.company', 'Company'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team'),
        'procurement_group_id': fields.many2one('procurement.group', 'Procurement group', copy=False),
        'product_id': fields.related('order_line', 'product_id', type='many2one', relation='product.product', string='Product'),
    }