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



class MyComment(http.Controller):

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

        if ajax ==1:
            ajax_value['categary_tab'] = request.website._render('sale_comment.mobile_myaccount_order_sale_comment_list_tab',
                {'value':value}).decode('utf-8')
            ajax_value['orderlist'] = request.website._render('website_myaccount_base.public_mobile_foreach_productList',
                {'value':value}).decode('utf-8')
            return ajax_value

    @http.route(['/m/myaccount/order/sale_comment/create_comment/'], type='json', auth='user', methods=['post'], website=True)
    def m_order_sale_comment_create(self, line_id, rating=4, description=None, website_published=False, is_anonymous=False)
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
    def m_order_sale_comment_by_categary(self):
        categary=str(categary)
        _logger.info('========== %s(), <%s>   ========== categary is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary))
        return self.get_sale_comment_by_categary(categary)

    @http.route(['/m/myaccount/order/sale_comment/ajax/<categary>'], type='json', auth='user', methods=['POST'], website=True)
    def m_order_sale_comment_ajax_categary(self,categary,limit=None,offset=None,**post):
        _logger.info('========== %s(), <%s>   ========== categary is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary))
        return self.get_sale_comment_by_categary(categary,ajax=1,limit=limit,offset=offset)
