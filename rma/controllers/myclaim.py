# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_myaccount_base.controllers.myaccount import MyAccount
import re
import operator
import sys
import logging
_logger = logging.getLogger(__name__)

import werkzeug

class MyClaim(http.Controller):

    def get_after_sale_order_and_claim(self, order_id):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value = {}
        order_id = int(order_id)
        claim_id = request.website.get_rma_claim_id(order_id)
        value['orders'] = registry.get('sale.order').browse(cr,uid,order_id,context=context)
        value['claims'] = registry.get('sale.advance.rma.claim').browse(cr,uid,claim_id,context=context)
        return value

    def get_after_sale_fields_list(self):
        json =  request.website.get_after_sale_fields_list()
        return json

    def get_after_sale_by_categary(self,categary,ajax=0,limit=None,offset=None):
        categary=str(categary)
        ajax=int(ajax)
        fields_list = self.get_after_sale_fields_list()
        value={}
        ajax_value={}
        value={'fields_list': fields_list.get(categary),'flag':categary,'limit':limit,'offset':offset}
        _logger.info('========== %s(), <%s>   ========== categary is %s, ajax is %s,value is %s' % (
            sys._getframe().f_code.co_name,request.env.user.name,categary,ajax,value))

        if ajax==0:
            return request.website.render('rma.mobile_myaccount_order_after_sale', {'value': value})

        if ajax ==1:
            ajax_value['categary_tab'] = request.website._render('rma.mobile_myaccount_order_after_sale_list_tab',
                {'value':value}).decode('utf-8')
            ajax_value['orderlist'] = request.website._render('website_myaccount_base.public_mobile_foreach_productList',
                {'value':value}).decode('utf-8')
            return ajax_value

    @http.route(['/m/myaccount/order/after_sale_main/<categary>'], type='http', auth='user',website=True)
    def m_after_sale_by_categary(self,categary):
        categary=str(categary)
        _logger.info('========== %s(), <%s>   ========== categary is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary))
        return self.get_after_sale_by_categary(categary)

    @http.route(['/m/myaccount/order/after_sale_main/ajax/<categary>'], type='json', auth='user', methods=['POST'], website=True)
    def m_after_sale_ajax_categary(self,categary,limit=None,offset=None,**post):
        _logger.info('========== %s(), <%s>   ========== categary is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary))
        return self.get_after_sale_by_categary(categary,ajax=1,limit=limit,offset=offset)

    @http.route(['/m/myaccount/order/after_sale/<order_id>'], type='http', auth='user', website=True)
    def m_order_after_sale(self, order_id=None, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value = self.get_after_sale_order_and_claim(order_id)
        orders = value.get('orders')
        claims = value.get('claims')

        # 每次打开售后详情单前，重置is_claim数据用于展示
        for o in claims.item_ids:
            for items in registry.get('sale.advance.rma.claim_items').browse(cr, uid, o.id, context=context):
                if not items.is_claim:
                    registry.get('sale.advance.rma.claim_items').write(cr, uid, [items.id], {'is_claim': True})

        return request.website.render('rma.mobile_order_activist_service_page', {'orders': orders, 'claims': claims})

    @http.route(['/m/myaccount/order/after_sale/delete_line_json'], type='json', auth="public", methods=['POST'], website=True)
    def mobile_after_saler_delete_line_json(self, order_id, item_id, display=True):
        '''隐藏订单行'''
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        value = self.get_after_sale_order_and_claim(order_id)
        orders = value.get('orders')
        claims = value.get('claims')
        res = {}

        registry.get('sale.advance.rma.claim_items').write(cr, uid, item_id, {'is_claim': False})
        res['mobile_after_sale_product_line'] = request.website._render('rma.mobile_after_sale_product_line', 
            {'orders': orders, 'claims': claims}).decode('utf-8')

        _logger.info('========== %s(), <%s>   ==========' % (sys._getframe().f_code.co_name,request.env.user.name))

        return res

    @http.route(['/m/myaccount/order/after_sale/checkout/<order_id>'], type='http', auth="public", website=True)
    def m_order_after_checkout(self, order_id=None, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        order_id = int(order_id)
        value = self.get_after_sale_order_and_claim(order_id)
        orders = value.get('orders')
        claims = value.get('claims')
        return request.website.render('rma.mobile_after_sale_checkout', {'orders': orders, 'claims': claims})

    @http.route(['/m/myaccount/order/after_sale/claim_create/<order_id>'], type='http', auth='user', website=True)
    def m_order_claim_create(self, order_id=None, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        order_id = int(order_id)
        crm_claim_id = False

        value = self.get_after_sale_order_and_claim(order_id)
        orders = value.get('orders')
        claims = value.get('claims')

        registry.get('sale.advance.rma.claim').write(cr, uid, claims.id, {'advance_payment_method': 'lines'})
        description = claims.description
        claim_origin = claims.claim_origin
        advance_payment_method = claims.advance_payment_method
        crm_claim_id = registry.get('sale.order').crm_claim_create(cr, uid, order_id, 
            claim_origin, description, advance_payment_method, claims.id)
        if crm_claim_id:
            crm_claim = registry.get('crm.claim').browse(cr,uid,crm_claim_id,context=context)
            return request.website.render('rma.mobile_after_sale_created', {'claims': crm_claim})
        else:
            return request.website.render('rma.mobile_order_activist_service_page', {'orders': orders, 'claims': claims})
    @http.route(['/m/myaccount/order/after_sale/claim_view/<order_id>'], type='http', auth='user', website=True)
    def m_order_claim_view(self, order_id=None, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        return request.website.render('website_myaccount_base.mobile_order_activist_service_page', {})
