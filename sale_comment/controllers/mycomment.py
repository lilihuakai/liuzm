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
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

# 1: imports of python lib
import sys
import logging

# 3: imports of openerp
from openerp import http
from openerp.http import request
from openerp.tools.translate import _

# 6: Import of unknown third party lib
_logger = logging.getLogger(__name__)

CPG = 10   # Comments Per Page

class MyComment(http.Controller):

    def get_product_sale_comment_page(self, product_tmp_id, domain, categary="all_comment", page=0):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        comment_obj = registry.get('sale.comment')

        url = "/m/myaccount/product/%s/sale_comment/%s" % (product_tmp_id, categary)
        comment_count = comment_obj.search_count(cr, uid, domain, context=context)
        pager = request.website.pager(
            url=url, total=comment_count, page=page, step=CPG, scope=6, url_args={})
        return pager

    def get_product_sale_comment_by_categary(self, product_tmp_id, categary="all_comment", page=0, ajax=0):
        categary=str(categary)
        ajax=int(ajax)
        fields_list = request.website.get_product_sale_comment_fields_list(product_tmp_id)
        domain = fields_list.get(categary)
        pager = self.get_product_sale_comment_page(product_tmp_id, domain, categary, page)

        value={}
        ajax_value={}
        value={
            'domain': domain,
            'flag':categary,
            'pager':pager,
            'limit':10,
            'offset':pager['offset'],
        }
        _logger.info('========== %s(), <%s>   ========== categary is %s, ajax is %s,value is %s' % (
            sys._getframe().f_code.co_name,request.env.user.name,categary,ajax,value))

        if ajax==0:
            return request.website.render('sale_comment.', {'value': value})
        if ajax ==1:
            ajax_value['categary_tab'] = request.website._render('sale_comment.product_sale_comment_list_tab',
                {'value':value}).decode('utf-8')
            ajax_value['commentlist'] = request.website._render('sale_comment.public_foreach_commentList',
                {'value':value}).decode('utf-8')
            ajax_value['pager'] = request.website._render('sale_comment.public_foreach_pager',
                {'value':value}).decode('utf-8')
            return ajax_value

    def get_sale_comment_by_categary(self,categary,ajax=0,limit=None,offset=None):
        categary=str(categary)
        ajax=int(ajax)
        fields_list = request.website.get_sale_comment_fields_list()
        value={}
        ajax_value={}
        value={'fields_list': fields_list.get(categary),'flag':categary,'limit':limit,'offset':offset}
        _logger.info('========== %s(), <%s>   ========== categary is %s, ajax is %s,value is %s' % (
            sys._getframe().f_code.co_name,request.env.user.name,categary,ajax,value))

        if ajax==0:
            return request.website.render('sale_comment.mobile_myaccount_order_sale_comment', {'value': value})

        # 刷新“评价中心”界面标题栏
        if ajax == 1:
            ajax_value['categary_tab'] = request.website._render('sale_comment.mobile_myaccount_order_sale_comment_list_tab',
                {'value':value}).decode('utf-8')
        # 刷新“我的订单”界面标题栏
        if ajax == 2:
            ajax_value['categary_tab'] = request.website._render('website_myaccount_base.public_mobile_order_category_tab',
                {'value':value}).decode('utf-8')
        ajax_value['orderlist'] = request.website._render('website_myaccount_base.public_mobile_foreach_productList',
            {'value':value}).decode('utf-8')
        return ajax_value

    @http.route(['/m/myaccount/order/sale_comment/create_comment/'], type='json', auth='user', methods=['post'], website=True)
    def m_order_sale_comment_create(self, line_id, rating=4, description=None, website_published=False, is_anonymous=False):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        res = {}

        context.update({
            'rating':rating,
            'description':description,
            'website_published':website_published,
            'is_anonymous':is_anonymous,
            })
        if line_id:
            res['comment'] = registry.get('sale.comment').create_comment(cr, uid, line_id, context=context)
        _logger.info('========== %s(), <%s>   ========== res = %s ' % 
            (sys._getframe().f_code.co_name,request.env.user.name, res))

        return res

    @http.route(['/m/myaccount/order/sale_comment/<categary>'], type='http', auth='user',website=True)
    def m_order_sale_comment_by_categary(self,categary):
        categary=str(categary)
        _logger.info('========== %s(), <%s>   ========== categary is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary))
        return self.get_sale_comment_by_categary(categary)

    @http.route(['/m/myaccount/order/sale_comment/ajax/<categary>'], type='json', auth='user', methods=['POST'], website=True)
    def m_order_sale_comment_ajax_categary(self,categary,ajax=1,limit=None,offset=None,**post):
        _logger.info('========== %s(), <%s>   ========== categary is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary))
        return self.get_sale_comment_by_categary(categary,ajax,limit=limit,offset=offset)

    # 按页、评论分类刷新产品评论
    @http.route(['/m/myaccount/product/<model("product.template"):product>/sale_comment/<categary>', 
                 '/m/myaccount/product/<model("product.template"):product>/sale_comment/<categary>/page/<int:page>'], type='http', auth='public', website=True)
    def m_product_sale_comment_by_categary(self, product, categary, page=0, **post):
        product_tmp_id = product.id

        return self.get_product_sale_comment_by_categary(product_tmp_id, categary, page)

    @http.route(['/m/myaccount/product/<model("product.template"):product>/sale_comment/ajax/<categary>'], type='json', auth='public', methods=['POST'], website=True)
    def m_product_sale_comment_ajax_categary(self, product, categary, page=0, **post):
        product_tmp_id = product.id

        return self.get_product_sale_comment_by_categary(product_tmp_id, categary, page, ajax=1)

    @http.route(['/m/myaccount/order/comment_view/<categary>/<order_id>'], type='http', auth='user', website=True)
    def m_order_comment_view_by_categary(self,categary,order_id):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        categary = str(categary)
        order_id = int(order_id)

        orders = registry.get('sale.order').browse(cr, uid, order_id, context=context)
        if categary == 'create_and_public':
            return request.website.render("", {'orders':orders})
        elif categary == 'public':
            return request.website.render("", {'orders':orders})
        elif categary == 'check':
            return request.website.render("", {'orders':orders})

    # @http.route(['/m/myaccount/order/comments/create'])
