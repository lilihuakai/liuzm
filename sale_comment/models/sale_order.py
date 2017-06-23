# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Liuzm
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# 3: imports of openerp
from openerp.osv import osv, fields
from openerp import api

class sale_order(osv.Model):
    _inherit = 'sale.order'

    # 判断是否存在订单评论
    def _comment_exists(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = False
            if sale.sale_comment_ids:
                res[sale.id] = True
        return res

    def _comment_exists_search(self, cursor, user, obj, name, args, context=None):
        if not len(args):
            return []

        cursor.execute('SELECT distinct comment.order_id FROM sale_comment AS comment')
        res = cursor.fetchall()

        if not res:
            return [('id', '=', 0)]
        for arg in args:
            if (arg[1] == '=' and arg[2]) or (arg[1] == '!=' and not arg[2]):
                return [('id', 'in', [x[0] for x in res])]
            else:
                return [('id', 'not in', [x[0] for x in res])]

    # 判断是否全部产品都做了评论
    def _cmmented(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = True
            for line in sale.order_line:
                if line.is_commented == False:
                    res[sale.id] = False
                    break
        return res

    def _commented_search(self, cursor, user, obj, name, args, context=None):
        # res1 保存的是用户提交的并等待商家回复的评论
        # res2 保存的是商家已经回复的评论，并等待用户回复的评论
        if not len(args):
            return []

        cursor.execute('SELECT distinct comment.order_id ' \
                'FROM sale_comment AS comment ' \
                'WHERE comment.wait_business_reply = \'TRUE\'' )
        res1 = cursor.fetchall()
        cursor.execute('SELECT distinct comment.order_id ' \
                'FROM sale_comment AS comment , sale_order_line AS line ' \
                'WHERE comment.order_id = line.order_id AND line.is_commented = \'FALSE\'' )
        res2 = cursor.fetchall()
        res = [x[0] for x in res1]
        for x in res2:
            if x[0] in res:
                res.remove(x[0])

        # if not res:
        #     return [('id', '=', 0)]
        for arg in args:
            if (arg[1] == '=' and arg[2]) or (arg[1] == '!=' and not arg[2]):
                return [('id', 'in', res)]
            else:
                return [('id', 'not in', res)]

    _columns = {
        'is_commented': fields.function(_comment_exists, string='Commented',
            fnct_search=_comment_exists_search, type='boolean', help="It indicates that sale order has at least one comment."),
        'is_complete_comment':fields.function(_cmmented, string='Complate Commented',
            fnct_search=_commented_search, type='boolean', help="It indicates that an order has been commented completely."),
        'is_public': fields.boolean('Is Public', default=False),
        'sale_comment_ids': fields.one2many("sale.comment", "order_id", string="Website Sale Comments"),
    }

class sale_order_line(osv.Model):
    _inherit = "sale.order.line"

    def _fnct_line_commented(self, cr, uid, ids, field_name, args, context=None):
        comment_obj = self.pool.get("sale.comment")
        res = dict.fromkeys(ids, False)
        for this in self.browse(cr, uid, ids, context=context):
            comment_ids = comment_obj.search(cr, uid, [('order_line_id', '=', this.id)], context=context)
            for comment in comment_obj.browse(cr, uid, comment_ids, context=context):
                # 暂时不考虑异常的评论数据，只要存在已经评论的数据就结束
                if comment.wait_business_reply:
                    res[this.id] = True
                    break
        return res

    def _order_lines_from_comment(self, cr, uid, ids, context=None):
        result = {}
        for comment in self.pool.get('sale.comment').browse(cr, uid, ids, context=context):
            result[comment.order_line_id.id] = True
        return result.keys()

    _columns = {
        'is_commented': fields.function(_fnct_line_commented, string='Commented', type='boolean',
            store={
                'sale.comment': (_order_lines_from_comment, ['wait_business_reply'], 10),
            }),
    }
