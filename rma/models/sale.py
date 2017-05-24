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

from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

import sys
import logging
_logger = logging.getLogger(__name__)

class sale_order(osv.Model):
    _inherit = "sale.order"

    # 判断是否存在售后订单
    def _claim_exists(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for claim in self.browse(cursor, user, ids, context=context):
            res[claim.id] = False
            if claim.claim_ids:
                res[claim.id] = True
        return res

    # 判断是否全部产品都申请了售后订单
    def _claimed(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = False
            for claim in sale.advance_id:
                for claim_items in claim.item_ids:
                    if claim_items.unclaimed_qty:
                        res[sale.id] = False
                        break
                    else:
                        res[sale.id] = True
                if not res[sale.id]:
                    break
        return res

    def _claimed_search(self, cursor, user, obj, name, args, context=None):
        if not len(args):
            return []

        cursor.execute('SELECT distinct sale.id ' \
                'FROM sale_order_claim_rel AS rel , sale_order AS sale , sale_order_line AS line ' \
                'WHERE rel.order_id = sale.id AND sale.id = line.order_id and line.claimed = \'TRUE\'' )
        res1 = cursor.fetchall()
        cursor.execute('SELECT distinct sale.id ' \
                'FROM sale_order_claim_rel AS rel , sale_order AS sale , sale_order_line AS line ' \
                'WHERE rel.order_id = sale.id AND sale.id = line.order_id and line.claimed = \'FALSE\'' )
        res2 = cursor.fetchall()
        res = [x[0] for x in res1]
        for x in res2:
            if x[0] in res:
                res.remove(x[0])

        if not res:
            return [('id', '=', 0)]
        for arg in args:
            if (arg[1] == '=' and arg[2]) or (arg[1] == '!=' and not arg[2]):
                return [('id', 'in', res)]
            else:
                return [('id', 'not in', res)]

    def _claim_exists_search(self, cursor, user, obj, name, args, context=None):
        if not len(args):
            return []

        cursor.execute('SELECT distinct rel.order_id FROM sale_order_claim_rel AS rel')
        res = cursor.fetchall()

        if not res:
            return [('id', '=', 0)]
        for arg in args:
            if (arg[1] == '=' and arg[2]) or (arg[1] == '!=' and not arg[2]):
                return [('id', 'in', [x[0] for x in res])]
            else:
                return [('id', 'not in', [x[0] for x in res])]

    _columns = {
        'partner_claim_id': fields.many2one('res.partner', 'Claim Address', readonly=True, 
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Claim address for current sales order."),
        'claim_ids': fields.many2many('crm.claim', 'sale_order_claim_rel', 'order_id', 'claim_id', 
            'Claims', readonly=True, copy=False, 
            help="This is the list of claims that have been generated for this sales order. \
            The same sales order may have been claimd in several times (by line for example)."),
        'claimed': fields.function(_claimed, string='Claimed',
            fnct_search=_claimed_search, type='boolean', help="It indicates that an claim has been claimed completely."),
        'claim_exists': fields.function(_claim_exists, string='Claimed',
            fnct_search=_claim_exists_search, type='boolean', help="It indicates that crm claim has at least one claim."),
        'advance_id': fields.one2many('sale.advance.rma.claim', 'order_id', 'Advance Rma Claim', readonly=True),
    }

    def _prepare_claim(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new claim for a
           sales order. This method may be overridden to implement custom
           claim generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to claim
           :param list(int) line: list of claim line IDs that must be
                                  attached to the claim
           :return: dict of value to create() the claim
        """
        if context is None:
            context = {}
        description = context.get('description')
        deal_method = context.get('deal_method')
        if not deal_method:
            deal_method = "RMA"

        claim_vals = {
            'claim_line_ids': [(6, 0, lines)], 
            'claim_type': 1,                                                            #暂不考虑供应商
            'date': time.strftime("%Y-%m-%d %H:%M:%S"), 
            # 'date_deadline': '2017-03-17', 
            'delivery_address_id': order.partner_id.id, 
            'description': description, 
            'email_from': order.partner_id.email,
            'partner_id': order.partner_id.id, 
            'partner_phone': order.partner_id.phone, 
            'priority': '1', 
            'stage_id': 1, 
            'user_id': order.user_id.id, 
            'warehouse_id': order.warehouse_id.id, 
            # 'action_next': False, 
            # 'categ_id': False, 
            # 'cause': False, 
            # 'date_action_next': False, 
            'name': deal_method, 
            # 'pick': False, 
            # 'ref': False, 
            # 'resolution': False, 
            # 'rma_number': False, 
            # 'type_action': False, 
            # 'section_id': False, 
            # 'user_fault': False, 
            }
        return claim_vals

    def _make_claim(self, cr, uid, order, lines, context=None):
        inv_obj = self.pool.get('crm.claim')
        if context is None:
            context = {}
        inv = self._prepare_claim(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, SUPERUSER_ID, inv, context=context)
        return inv_id

    def manual_claim(self, cr, uid, ids, context=None):
        """ create claims for the given sales orders (ids), and open the form
            view of one of the newly created claims
        """
        if not context:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        
        # create claims through the sales orders' workflow
        inv_ids0 = set(inv.id for sale in self.browse(cr, uid, ids, context) for inv in sale.claim_ids)
        self.crm_claim_create(cr, uid, ids, context=context)
        inv_ids1 = set(inv.id for sale in self.browse(cr, uid, ids, context) for inv in sale.claim_ids)
        # determine newly created claims
        new_inv_ids = list(inv_ids1 - inv_ids0)

        res = mod_obj.get_object_reference(cr, uid, 'crm_claim', 'crm_case_claims_form_view')
        res_id = res and res[1] or False,

        return {
            'name': _('Customer Claims'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'crm.claim',
            # 'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': new_inv_ids and new_inv_ids[0] or False,
        }

    def action_view_claim(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing claims of given sales order ids. 
        It can either be a in a list or in a form view, if there is only one claim to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'crm_claim', 'crm_case_categ_claim0')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of claim to display
        inv_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            inv_ids += [claim.id for claim in so.claim_ids]
        #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'crm_claim', 'crm_case_claims_form_view')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result

    def crm_claim_create(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        claim = self.pool.get('crm.claim')
        obj_sale_order_line = self.pool.get('sale.order.line')

        res = False
        claims = {}
        claim_ids = []
        partner_currency = {}
        states = ['confirmed', 'done', 'exception']

        for o in self.browse(cr, uid, ids, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and (partner_currency[o.partner_id.id] <> currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id
            lines = []
            for line in o.order_line:
                if line.claimed:
                    continue
                elif (line.state in states):
                    lines.append(line.id)
            created_lines = obj_sale_order_line.claim_line_create(cr, uid, lines, context=context)
            if created_lines:
                claims.setdefault(o.partner_claim_id.id or o.partner_id.id, []).append((o, created_lines))
        if not claims:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.claim_ids:
                    if i.state == 'draft':
                        return i.id
        for val in claims.values():
            for order, il in val:
                res = self._make_claim(cr, uid, order, il, context=context)
                claim_ids.append(res)
                cr.execute('insert into sale_order_claim_rel (order_id,claim_id) values (%s,%s)', (order.id, res))
                # 因为cr在执行 CREATE，UPDATE，DELETE 的 SQL语句之前，清空cache是很有必要的，否则models的调用
                # 可能会出现未知错误。
                self.invalidate_cache(cr, uid, ['claim_ids'], [order.id], context=context)
        return res

    @api.cr_uid_ids_context
    def do_enter_claim_details(self, cr, uid, order, context=None):
        if not context:
            context = {}
        else:
            context = context.copy()
        context.update({
            'active_model': self._name,
            'active_ids': order,
            'active_id': len(order) and order[0] or False
        })

        created_id = self.browse(cr, uid, order, context=context).advance_id.id
        if not created_id:
            created_id = self.pool['sale.advance.rma.claim'].create(cr, uid, 
                {'order_id': len(order) and order[0] or False}, context)
        return self.pool['sale.advance.rma.claim'].wizard_view(cr, uid, created_id, context)


class sale_order_line(osv.Model):
    _inherit = "sale.order.line"

    def _fnct_line_claimed(self, cr, uid, ids, field_name, args, context=None):
        claim_obj = self.pool.get("sale.advance.rma.claim")
        items_obj = self.pool.get("sale.advance.rma.claim_items")
        res = dict.fromkeys(ids, False)
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = this.claim_lines and \
                all(iline.claim_id.state != 'cancel' for iline in this.claim_lines) 
            claim = claim_obj.browse(cr, uid, this.order_id.advance_id.id, context=context)
            for o in claim.item_ids:
                for items in items_obj.browse(cr, uid, o.id, context=context):
                    if items.product_id.id == this.product_id.id:
                        if items.unclaimed_qty:
                            res[this.id] = False
                            break
        return res

    def _order_lines_from_claim(self, cr, uid, ids, context=None):
        # direct access to the m2m table is the less convoluted way to achieve this (and is ok ACL-wise)
        cr.execute("""SELECT DISTINCT sol.id FROM sale_order_claim_rel rel JOIN
                                                  sale_order_line sol ON (sol.order_id = rel.order_id)
                                    WHERE rel.claim_id = ANY(%s)""", (list(ids),))
        return [i[0] for i in cr.fetchall()]

    _columns = {
        'claim_lines': fields.many2many('claim.line', 'sale_order_line_claim_rel', 'order_line_id', 'claim_id', 
            'Claim Lines', readonly=True, copy=False),
        'claimed': fields.function(_fnct_line_claimed, string='Claimed', type='boolean',
            store={
                'crm.claim': (_order_lines_from_claim, ['state'], 10),
                'sale.order.line': (lambda self,cr,uid,ids,ctx=None: ids, ['claim_lines'], 10)
            }),
    }

    def _prepare_order_line_claim_line(self, cr, uid, line, context=None):
        """Prepare the dict of values to create the new claim line for a
           sales order line. This method may be overridden to implement custom
           claim generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to claim
           :return: dict of values to create() the claim line
        """
        if context is None:
            context = {}

        line_obj = self.pool.get("claim.line")
        claim_obj = self.pool.get("sale.advance.rma.claim")
        items_obj = self.pool.get("sale.advance.rma.claim_items")
        res = {}
        quantity = 0
        item_ids = context.get('item_ids')
        claim_origin = context.get('claim_origin')
        advance_payment_method = context.get('advance_payment_method')

        claim = claim_obj.browse(cr, uid, item_ids, context=context)
        for o in claim.item_ids:
            for items in items_obj.browse(cr, uid, o.id, context=context):
                if items.line_id.id == line.id:
                    if not items.is_claim and advance_payment_method == "lines":
                        items_obj.reset_items(cr, uid, o.id, context=context)
                        return res
                    elif (items.product_uom_qty <= 0) or (items.unclaimed_qty < items.product_uom_qty):
                        # items_obj.reset_items(cr, uid, o.id, context=context)
                        # return res
                        raise osv.except_osv(_('Warnning!'), _("%s's quantity %s can't be use!") 
                            % (items.product_id.name, items.product_uom_qty))
                    else:
                        quantity = items.product_uom_qty
                        tmp = items.unclaimed_qty - items.product_uom_qty
                        items_obj.write(cr, uid, [items.id], 
                            {'unclaimed_qty': tmp, 
                            'product_uom_qty': tmp, 
                            'is_claim': False})
                        break
                else:
                    _logger.info('========== %s(),   ========== line_id is %s line.id %s'% 
                            (sys._getframe().f_code.co_name,items.line_id.id, line.id))
        location_dest_id = line_obj.get_destination_location(
            line.product_id,
            line.order_id.warehouse_id).id

        if not line.claimed and quantity:
            res = {
                'claim_origin': claim_origin,
                'claim_type': 1,
                'last_state_change': time.strftime("%Y-%m-%d"),
                'location_dest_id': location_dest_id,
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_returned_quantity': quantity,
                'return_value': line.price_subtotal,
                'unit_sale_price': line.price_unit,
                # 'date_deadline': date_deadline,
                # 'guarantee_limit': ,
                # 'move_in_id': ,
                # 'move_out_id': ,
                # 'refund_line_id': ,
                # 'warning': ,
                # 'warranty_return_partner': ,
                # 'warranty_type': ,
            }

        return res

    def claim_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        create_ids = []
        sales = set()
        for line in self.browse(cr, SUPERUSER_ID, ids, context=context):
            vals = self._prepare_order_line_claim_line(cr, uid, line, context=context)
            if vals:
                inv_id = self.pool.get('claim.line').create(cr, SUPERUSER_ID, vals, context=context)
                self.write(cr, SUPERUSER_ID, [line.id], {'claim_lines': [(4, inv_id)]}, context=context)
                sales.add(line.order_id.id)
                create_ids.append(inv_id)
        # Trigger workflow events
        for sale_id in sales:
            workflow.trg_write(uid, 'sale.order', sale_id, cr)
        return create_ids