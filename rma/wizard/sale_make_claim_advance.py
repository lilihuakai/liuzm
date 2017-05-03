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

from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

# class sale_advance_rma_claim(osv.osv_memory):
class sale_advance_rma_claim(osv.osv):
    _name = "sale.advance.rma.claim"
    _description = "Sales Advance Rma Claim"

    SUBJECT_LIST = [('none', 'Not specified'),
                    ('legal', 'Legal retractation'),
                    ('cancellation', 'Order cancellation'),
                    ('damaged', 'Damaged delivered product'),
                    ('error', 'Shipping error'),
                    ('exchange', 'Exchange request'),
                    ('lost', 'Lost during transport'),
                    ('perfect_conditions', 'Perfect Conditions'),
                    ('imperfection', 'Imperfection'),
                    ('physical_damage_client', 'Physical Damage by Client'),
                    ('physical_damage_company', 'Physical Damage by Company'),
                    ('other', 'Other')]

    _columns = {
        'advance_payment_method':fields.selection(
            [('all', 'Claim the whole sales order'), ('lines', 'Some order lines')],
            'What do you want to claim?', required=True,
            help="""Use Claim the whole sale order to create the final claim.
                Use Some Order Lines to claim a selection of the sales order lines."""),
        'claim_origin': fields.selection(SUBJECT_LIST, 'Subject',required=True, 
            help="To describe the line product problem"),
        'description': fields.text('Description'),
        'item_ids': fields.one2many('sale.advance.rma.claim_items', 'item_id', 'Items', domain=[('product_id', '!=', False)]),
        'order_id': fields.many2one('sale.order', 'Order Reference'),
    }

    _defaults = {
        'advance_payment_method': 'all',
        'claim_origin': 'none',
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(sale_advance_rma_claim, self).default_get(cr, uid, fields, context=context)
        order_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not order_ids or len(order_ids) != 1:
            # Partial claim Processing may only be done for one claim at a time
            return res
        assert active_model in ('sale.order'), 'Bad context propagation'
        order_id, = order_ids
        orders = self.pool.get('sale.order').browse(cr, uid, order_id, context=context)
        items = []
        for line in orders.order_line:
            item = {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'price_subtotal': line.price_subtotal,
                'claimed_qty': line.product_uom_qty,
                'unclaimed_qty': line.product_uom_qty,
                'line_id': line.id,
            }
            if line.product_id:
                items.append(item)
        res.update(item_ids=items)
        return res

    def create_claims(self, cr, uid, ids, context=None):
        """ create claims for the active sales orders """
        sale_obj = self.pool.get('sale.order')
        items_obj = self.pool.get('sale.advance.rma.claim_items')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])
        claim_origin = wizard.claim_origin
        description = wizard.description
        item_ids = wizard.id
        advance_payment_method = wizard.advance_payment_method

        if advance_payment_method == "all":
            is_claim = True
        else:
            is_claim = False
            for claims in wizard.item_ids:
                for items in items_obj.browse(cr, uid, claims.id, context=context):
                    if items.is_claim:
                        is_claim = True
                        break
                if is_claim:
                    break;
        if not is_claim:
            # for claims in wizard.item_ids:
            #     items_obj.reset_items(cr, uid, claims.id, context=context)
            raise osv.except_osv(_('Warnning!'), _('You have to choice one of them to claim!'))
        res = sale_obj.manual_claim(cr, uid, sale_ids, claim_origin, description, advance_payment_method, item_ids, context)

        # create the final claims of the active sales orders
        if context.get('is_open_claims', False) and is_claim:
            return res
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def wizard_view(self):
        view = self.env.ref('rma.view_stock_enter_claim_details')

        return {
            'name': _('Enter claim details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.advance.rma.claim',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }


# class sale_advance_rma_claim_items(osv.osv_memory):
class sale_advance_rma_claim_items(osv.osv):
    _name = "sale.advance.rma.claim_items"
    _description = "Sales Advance Rma Claim Items"

    _columns = {
        'item_id': fields.many2one('sale.advance.rma.claim', 'Item'),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'name': fields.text('Description', required=True, readonly=True),
        'product_uom_qty': fields.float('Quantity', required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True, readonly=True),
        'price_unit': fields.float('Unit Price', required=True, readonly=True),
        'discount': fields.float('Discount (%)', readonly=True),
        'price_subtotal': fields.float(string='Subtotal', readonly=True),
        'claimed_qty': fields.float('Caimed Quantity', required=True, readonly=True),
        'unclaimed_qty': fields.float('Unlaimed Quantity', required=True, readonly=True),
        'is_claim': fields.boolean('Is Claim', help="If it is true, the product will be claimed"),
        'line_id' : fields.many2one('sale.order.line', 'ID of sale.order.line'),
    }

    _defaults = {
        'is_claim': False,
    }

    # 重置数据
    @api.multi
    def reset_items(self):
        self.product_uom_qty = self.unclaimed_qty
        self.is_claim = False

        return self
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
