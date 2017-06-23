# -*- coding: utf-8 -*-
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
# 1: imports of python lib
import sys
import logging

# 3: imports of openerp
import openerp
from openerp.osv import orm
from openerp.http import request

# 6: Import of unknown third party lib
_logger = logging.getLogger(__name__)

class website(orm.Model):
    _inherit = 'website'

    # 继承修改了 website_myaccount_base 模块的处理代码
    def get_order_fields_list(self,field_name=None):
        value = {
            # 全部, 待支付, 待卖家发货, 待收货, 待评价, 维权
            'all' : [('state','not in',['cancel'])],  # 全部
            'draft' : [('state','=','draft')],  # 待支付
            # 'draft' : [('state','in',['draft'])],  # 待支付
            'undelivered' : ['|','&',('state','in',['manual','progress','done']),('logistics_state', '=', 'waiting_send'),'&',('state','in',['manual','progress']),('logistics_state', '=', 'sent')],  # 待卖家发货
            'wait_delivery' : [('state','=','done'),('logistics_state','=','sent')],  # 待收货
            'waiting_comment' : [('state','=','done'), ('is_complete_comment', '=', False)],  # 待评价
        }
        if field_name is not None:
            return value.get(field_name)
        else:
            return value

    def get_sale_comment_fields_list(self):
        value = {
            # 待评价、待晒单、已评价
            'waiting_comment' : [('state','=','done'), ('is_complete_comment', '=', False)],
            # 'waiting_public' : [('state','=','done'), ('is_public', '=', False)],             #取消待晒单
            'already_comment' : [('state','=','done'), ('is_commented', '=', True)],
        }

        return value

    def get_product_sale_comment_fields_list(self, product_tmp_id):
        value = {
            # 全部、好评、中评、差评
            'all_comment' : [('product_tmp_id', '=', product_tmp_id)],
            'good_comment' : [('product_tmp_id', '=', product_tmp_id), ('rating', '>', 3)],
            'no_bed_comment' : [('product_tmp_id', '=', product_tmp_id), ('rating', '=', 3)],
            'bed_comment' : [('product_tmp_id', '=', product_tmp_id), ('rating', '<', 3)],
        }

        return value

    # 获取产品评论
    def get_product_comments(self, cr, uid, ids, domain, limit=10, offset=0, context=None):
        comment_obj = self.pool.get('sale.comment')
        comment_ids = comment_obj.search(cr, uid, domain, limit=limit, offset=offset, context=context)
        _logger.info('======= %s(), <%s>======= comment_ids = %s' % (sys._getframe().f_code.co_name, request.env.user.name, comment_ids))
        comments = comment_obj.browse(cr, uid, comment_ids, context=context)

        return comments

    # 获取评论相关的订单数量
    def get_comments_order_count_by_field(self, cr, uid, ids, field_name, context=None):
        fields_list = self.get_sale_comment_fields_list()
        domain = fields_list.get(field_name)
        count = self.get_order_count_by_field(cr,uid,ids,domain).get('count')

        if count:
            return count
        else:
            return 0

    # 获取评论总数
    def get_comments_count(self, cr, uid, ids, domain, context=None):
        comment_count = self.pool.get('sale.comment').search_count(cr, uid, domain, context=context)
        _logger.info('======= %s(), <%s>======= domain is %s, comment_count = %s' % 
            (sys._getframe().f_code.co_name, request.env.user.name, domain, comment_count))

        return comment_count

    def get_comments_count_by_field(self, cr, uid, ids, product_tmp_id, field_name, context=None):
        fields_list = self.get_product_sale_comment_fields_list(product_tmp_id)
        domain = fields_list.get(field_name)
        count = self.get_comments_count(cr, uid, ids, domain, context=context)

        if count:
            return count
        else:
            return 0

    # 获取产品评论翻页功能所需的初始数据
    def get_product_comments_init_value(self, cr, uid, ids, product_tmp_id, context=None):
        url = "/m/myaccount/product/%s/sale_comment" % product_tmp_id
        domain = [('product_tmp_id', '=', product_tmp_id)]
        comment_count = self.get_comments_count(cr, uid, ids, domain, context=context)

        pager = request.website.pager(
            url=url, total=comment_count, page=1, step=10, scope=6, url_args={})
        value={
            'domain': domain,
            'flag':"all_comment",
            'pager':pager,
            'limit':10,
            'offset':0,
            'product_tmp_id':product_tmp_id,
        }
        _logger.info('======= %s(), <%s>======= value = %s' % (sys._getframe().f_code.co_name, request.env.user.name, value))

        return value

