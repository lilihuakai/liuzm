# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale
import re
import operator  # add by jinchao
import sys  # add by jinchao,    using in testing env
import logging
_logger = logging.getLogger(__name__)

import werkzeug

class MyAccount(http.Controller):

    def get_partner_company(self):
        user = request.env.user
        return user.partner_id

    def get_order_fields_list(self):
        json =  request.website.get_order_fields_list()
        return json


    def get_distribution_product_promotion_default(self,limit=10,offset=0):
        value = {
            'limit':10,
            'offset':0
        }
        return value


    

    # adit by liuzm
    # def orderlist_page_by_activist(self,value,ajax=0):
    #     # 维权新开页面
    #     if ajax == 1:
    #         ajax_value['orderlist'] = request.website._render('website_myaccount_base.public_mobile_foreach_productList',{'value':value}).decode('utf-8')
    #         return ajax_value
    #     else:
    #         return request.website.render('website_myaccount_base.mobile_orderlist_activist_page', {'value': value})

    def get_template_orderlist_by_categary(self,categary,ajax=0,limit=None,offset=None):
        categary=str(categary)
        ajax=int(ajax)
        fields_list = self.get_order_fields_list()
        value={}
        ajax_value={}
        # 全部, 待支付, 待卖家发货, 待收货, 待评价, 维权
        value={'fields_list': fields_list.get(categary),'flag':categary,'limit':limit,'offset':offset}
        _logger.info('========== %s(), <%s>   ========== categary is %s, ajax is %s,value is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary,ajax,value))

        # adit by liuzm
        # if categary == 'activist':
        #         # 维权需要特殊处理,新开页面
        #     return self.orderlist_page_by_activist(value,ajax)

        if ajax==0 and categary != 'activist':
            return request.website.render('website_myaccount_base.mobile_myaccount_user_orderlist', {'value': value})

        if ajax ==1 and categary != 'activist':
            ajax_value['categary_tab'] = request.website._render('website_myaccount_base.public_mobile_order_category_tab',{'value':value}).decode('utf-8')
            ajax_value['orderlist'] = request.website._render('website_myaccount_base.public_mobile_foreach_productList',{'value':value}).decode('utf-8')
            return ajax_value

    @http.route(['/m/myaccount/orderlist/get_default_limit_offset'], type='json', auth='user', methods=['POST'], website=True)
    def m_myaccount_orderlist_limit_offset(self,sid):
        if int(sid) == 1:
            default_dict =  request.website.get_default_orderlist_record_count()
            limit = default_dict.get('limit')
            offset = default_dict.get('offset')
            value = { 'limit':limit , 'offset':offset}
            return value

    @http.route(['/myaccount'], type='http', auth='user', website=True)
    def myaccount(self, container=None, **post):
        return request.website.render('website_myaccount_base.dashboard', {})


    @http.route(['/myaccount/profile'],
                type='http', auth='user', website=True)
    def profile(self, container=None, **post):
        return request.website.render('website_myaccount_base.profile', {
            'user': request.env.user
            })

    @http.route(['/myaccount/profile/update'], type='json', auth='user', methods=['POST'], website=True)
    def profile_update(self, data):
        env = request.env

        if 'email' in data and data['email'] and env.user.email != data['email']:
            exist = env.user.search([('email', '=', data['email'])])
            if exist:
                return {'error': _('The email %s has alread exists') % data['email'] or '', 'result': False}
        if 'mobile' in data and data['mobile'] and env.user.mobile != data['mobile']:
            exist = env.user.search([('mobile', '=', data['mobile'])])
            if exist:
                return {'error': _('The mobile %s has alread exists') % data['mobile'] or '', 'result': False}

        result = env.user.write(data)
        return {'error': _('update successfully'), 'result': result}

    @http.route(['/myaccount/addresses'],
                type='http', auth='user', website=True)
    def addresses(self, container=None, **post):
        env = request.env
        partner = self.get_partner_company() or env.user.partner_id
        shipping = [p for p in partner.child_ids if p.type == 'delivery']
        invoices = [p for p in partner.child_ids if p.type == 'invoice']
        return request.website.render('website_myaccount_base.addresses', {
            'partner': partner,
            'shipping_address': shipping,
            'invoice_address': invoices})

    @http.route(['/myaccount/default_address/update'], type='json', auth='user',
                methods=['POST'], website=True)
    def default_address_update(self, data):
        env = request.env
        # _logger.info('update default address, data=%s'%data)

        result = env.user.write(data)
        return {'error': '', 'result': result}


    # +begin append by jinchao------------------------------

    @http.route(['/m/myaccount/distribution/faq'], type='http', auth='user', website=True)
    def mobile_distribution_FAQ(self, container=None, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        faq_ids = registry.get('website_myaccount_base.distribution.faq').search(cr,SUPERUSER_ID,[],context=context)
        faqs = registry.get('website_myaccount_base.distribution.faq').browse(cr,SUPERUSER_ID,faq_ids,context=context)
        _logger.info('========== %s(), <%s>   ==========  faqs is %s' % (sys._getframe().f_code.co_name,request.env.user.name,faqs))
        return request.website.render('website_myaccount_base.mobile_distribution_FAQ', {'faqs':faqs})

    @http.route(['/m/myaccount/distribution/info'], type='http', auth='user', website=True)
    def mobile_distribution_info(self, container=None, **post):
        return request.website.render('website_myaccount_base.mobile_distribution_info', {'user': request.env.user})

    @http.route(['/m/myaccount/address/list'], type='http', auth='user', website=True)
    def m_address_list(self, container=None, **post):
        return request.website.render('website_myaccount_base.mobile_address_list', {})

    @http.route(['/m/myaccount/address/edit'],type='http',methods=['POST'],auth='user', website=True)
    def m_address_edit(self,shipto_id,**kw):
        shipto_id = int(shipto_id)
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        orm_partner = registry.get('res.partner')
        address = orm_partner.browse(cr, SUPERUSER_ID, shipto_id, context=context)
        _logger.info('========== %s(), <%s>   ==========  address=%s' % (sys._getframe().f_code.co_name,request.env.user.name,address.id))
        orm_address = registry.get('address.list')
        value = {
            'name': '',
            'mobile': '',
            'street': '',
            'province': '',
            'city': '',
            'county': '',
            'zip_code': '',
        }
        if address and address.address_id:
            value.update(orm_address.get_address(cr, uid, address.address_id.id, context=context))
        # value['shipto_info'] = request.website.render('website_myaccount_base.mobile_address_edit', {'address': address}).decode('utf-8')
        # return request.website.render('website_myaccount_base.mobile_address_edit', {'address': address})
        res = request.website.render('website_myaccount_base.mobile_address_edit', {'address': address})
        _logger.info('================== render =================== res=%s'% res)
        return res

    @http.route(['/m/myaccount/address/add'], type='http', auth='user', website=True)
    def m_address_add(self, container=None, **post):
        return request.website.render('website_myaccount_base.mobile_address_edit', {})

    @http.route(['/m/myaccount'], type='http', auth='user', website=True)
    def mobile_myaccount(self, container=None, **post):
        return request.website.render('website_myaccount_base.mobile_admin_index', {'user':request.env.user})

    @http.route(['/m/myaccount/coupon'], type='http', auth='user', website=True)
    def mobile_myaccount_coupon(self, container=None, **post):
        return request.website.render('website_myaccount_base.mobile_myaccount_coupon_html', {'user':request.env.user})

    @http.route(['/m/myaccount/coupon/ajax'], type='json', auth='user',methods=['POST'],website=True)
    def mobile_myaccount_coupon_ajax(self,ajax, **post):
        return request.website.render('website_myaccount_base.mobile_myaccount_coupon_foreach_list', {})

    @http.route(['/m/myaccount/infor'], type='http', auth='user', website=True)
    def mobile_myaccount_infor(self, container=None, **post):
        env = request.env
        partner = self.get_partner_company() or env.user.partner_id
        return request.website.render('website_myaccount_base.mobile_admin_infor', {
            'user': request.env.user,
            'partner': partner
            })

    @http.route(['/m/myaccount/distribution'], type='http', auth='user', website=True)
    def mobile_myaccount_distribution(self, container=None, **post):
        return request.website.render(
            'website_myaccount_base.mobile_admin_distribution',
            {'user': request.env.user})


    @http.route(['/m/myaccount/distribution/account'], type='http', auth='user', website=True)
    def mobile_myaccount_distribution_account(self, container=None, **post):
        return request.website.render('website_myaccount_base.mobile_admin_distribution_account', {'user': request.env.user})

    @http.route(['/m/myaccount/distribution/productPromotion'], type='http', auth='user', website=True)
    def mobile_myaccount_distribution_productPromotion(self, container=None, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        default_dict = self.get_distribution_product_promotion_default()
        limit = default_dict.get('limit')
        offset = default_dict.get('offset')
        value = {}
        # first_id is new_time
        result = registry.get('res.partner').get_distribution_products(cr,SUPERUSER_ID,[],request.env.user.id,order="id desc",limit=limit, offset=offset)
        _logger.info('========== %s(), <%s>   ==========offset=%s,limit=%s,  result is %s' % (sys._getframe().f_code.co_name,request.env.user.name,offset,limit,result))

        if ((not result) and offset)  or (len(result) < limit):
            value.update({'not_enough_data':1})

        value.update({'promotion_lines':result})
        return request.website.render('website_myaccount_base.mobile_myaccount_distribution_productPromotion', {'value':value})

    @http.route(['/m/myaccount/distribution/productPromotion_post'], type='json', auth='user',methods=['POST'],website=True)
    def mobile_myaccount_distribution_productPromotion_post(self,sort_regexp=None,limit=None,offset=None, **post):
        sort_regexp = str(sort_regexp)
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value ={}
        def get_sort_result(case,result):
            case = str(case)
            if " desc" in case:
                case = case.replace(' desc','')
                _logger.info('========== %s(), <%s>   ==========  case is %s' % (sys._getframe().f_code.co_name,request.env.user.name,case))
                return sorted(result, key=operator.itemgetter(case),reverse=True)
            else:
                return sorted(result, key=operator.itemgetter(case)) # end

        if offset is None:
            offset = self.get_distribution_product_promotion_default().get('offset')
        if limit is None:
            limit = self.get_distribution_product_promotion_default().get('limit')


        # if want sort 'sales_count' or 'amount_commission' ,因为是计算字段作特殊处理
        if sort_regexp == "sales_count" or sort_regexp == "sales_count desc" or sort_regexp == "amount_commission" or sort_regexp == "amount_commission desc":
            result = registry.get('res.partner').get_distribution_products(cr,SUPERUSER_ID,[],request.env.user.id,limit=limit,offset=offset)
            result = get_sort_result(sort_regexp,result)
        else:
            result = registry.get('res.partner').get_distribution_products(cr,SUPERUSER_ID,[],request.env.user.id,limit=limit,offset=offset,order=sort_regexp)

        if ((not result) and offset)  or (len(result) < limit):
            value.update({'not_enough_data':1})

        value.update({'promotion_lines':result})
        _logger.info('===== %s(), <%s>  =====request.env.user.id=%s, sort_regexp=%s, result=%s, offset=%s, limit=%s' % (sys._getframe().f_code.co_name,request.env.user.name,request.env.user.id,sort_regexp,result,offset,limit))
        ajax_value = {}
        ajax_value['promotion_lines'] = request.website._render('website_myaccount_base.mobile_distribution_productPromotion_list', {'value':value}).decode('utf-8')
        _logger.info('===== %s(), <%s>  ===== ajax_value=%s' % (sys._getframe().f_code.co_name,request.env.user.name,ajax_value['promotion_lines']))
        
        return ajax_value


    # 为了统一提现功能跳转链接，现将此代码注释，将功能转移到mobile_payment模块 add by Liuzm 20170517
    # @http.route(['/m/myaccount/distribution/account/WithdrawalAccount'], type='http', auth='user', website=True)
    # def mobile_myaccount_distribution_account_WithdrawalAccount(self, container=None, **post):
    #     return request.website.render('website_myaccount_base.mobile_admin_distribution_account_WithdrawalAccount', {'user': request.env.user})

    @http.route(['/m/myaccount/distribution/customer'], type='http', auth='user', website=True)
    def mobile_myaccount_distribution_customer(self, container=None, **post):
        return request.website.render('website_myaccount_base.mobile_admin_distribution_customer', {'user': request.env.user})

    @http.route(['/m/myaccount/distribution/myqrcode'], type='http', auth='user', website=True)
    def mobile_myaccount_distribution_myqrcode(self, container=None, **post):
        # template_html = request.website._render('website_myaccount_base.mobile_admin_distribution_myqrcode',{'user':request.env.user}).decode('utf-8')
        # _logger.info('===== %s(), <%s>  ===== template_html=%s' % (sys._getframe().f_code.co_name,request.env.user.name,template_html))
        # return request.website.render('website_myaccount_base.mobile_admin_distribution_myqrcode', {'user': request.env.user})

    # @http.route(['/m/myaccount/distribution/get_ssuid_qrcode'], type='json', auth='user',methods=['POST'],website=True)
    # def mobile_myaccount_distribution_ordersManager_post(self,ssuid):
    #     # user = registry['res.users'].browse(cr, SUPERUSER_ID, int(ssuid), context)
    #     # ajax_value['user_qrcode'] =
    #     return

    # @http.route(['/m/myaccount/distribution/spread'], type='http', auth='public',website=True)
    # def mobile_myaccount_distribution_spread(self, puid, container=None, **post):
    #     cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

    #     user = registry['res.users'].browse(cr, SUPERUSER_ID, int(puid), context)
    #     return request.website.render('website_myaccount_base.mobile_admin_distribution_myqrcode', {'user': user})

        return werkzeug.utils.redirect("/m/myaccount/distribution/myqrcode/html2image")


    @http.route(['/m/myaccount/distribution/ordersmanager'], type='http', auth='user', website=True)
    def mobile_myaccount_distribution_ordersManager(self,container=None, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        partner_id = self.get_partner_company().id
        _logger.info('========== %s(), <%s>   ==========  partner_id is %s' % (sys._getframe().f_code.co_name,request.env.user.name,partner_id))
        # all ids
        commission_ids = registry.get('sale.commission.agent').search(cr,SUPERUSER_ID,[('state','not in',['draft']),('agent_id','=',partner_id)],order="id desc",context=context)
        commission_lines = registry.get('sale.commission.agent').browse(cr,SUPERUSER_ID,commission_ids,context=context)
        _logger.info('========== %s(), <%s>   ==========  orders_ids is %s' % (sys._getframe().f_code.co_name,request.env.user.name,commission_ids))
        _logger.info('========== %s(), <%s>   ==========  commission_line_ids is %s' % (sys._getframe().f_code.co_name,request.env.user.name,commission_lines))
        confirmed_order_count=len(registry.get('sale.commission.agent').search(cr,SUPERUSER_ID,[('state','=','confirmed'),('agent_id','=',partner_id)],context=context))
        _logger.info('========== %s(), <%s>   ==========  count is %s' % (sys._getframe().f_code.co_name,request.env.user.name,confirmed_order_count))
        return request.website.render('website_myaccount_base.mobile_myaccount_distribution_ordersManager', {'commission_lines':commission_lines,'confirmed_order_count':confirmed_order_count})


    @http.route(['/m/myaccount/distribution/ordersmanager_post'], type='json', auth='user',methods=['POST'],website=True)
    def mobile_myaccount_distribution_ordersManager_post(self,state):
        state=str(state)
        partner_id = self.get_partner_company().id
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        _logger.info('========== %s(), <%s>   ========== state is %s' % (sys._getframe().f_code.co_name,request.env.user.name,state))
        if state == 'all':
            commission_ids = registry.get('sale.commission.agent').search(cr,SUPERUSER_ID,[('state','not in',['draft']),('agent_id','=',partner_id)],order="id desc",context=context)
        else:
            commission_ids = registry.get('sale.commission.agent').search(cr,SUPERUSER_ID,[('state','=',state),('agent_id','=',partner_id)],order="id desc",context=context)


        _logger.info('========== %s(), <%s>   ========== ids is %s' % (sys._getframe().f_code.co_name,request.env.user.name,commission_ids))
        commission_lines = registry.get('sale.commission.agent').browse(cr,SUPERUSER_ID,commission_ids,context=context)
        _logger.info('========== %s(), <%s>   ========== commission_lines is %s' % (sys._getframe().f_code.co_name,request.env.user.name,commission_lines))
        value = {}
        value['commission_lines'] = request.website._render('website_myaccount_base.mobile_myaccount_distribution_ordersManager_list', {'commission_lines': commission_lines}).decode('utf-8')
        return value

    @http.route(['/m/myaccount/orderlist'],
                type='http', auth='user', website=True)
    def m_orders(self, container=None, **post):
        # 些为旧的,已弃用
        # env = request.env
        # partner = self.get_partner_company()
        # if partner:
        #     orders = env['sale.order'].search(
        #         [('partner_id', '=', partner.id),
        #          ('state', 'not in', ['cancel'])])
        # else:
        #     orders = []

        # return request.website.render(
        #     'website_myaccount_base.mobile_admin_orderlist',
        #     {'orders': orders})
        return request.redirect('/m/myaccount/orderlist/all')

    @http.route(['/m/myaccount/red_revelopes'], type='http', auth='user', website=True)
    def mobile_myaccount_red_revelopes(self, **post):
        _logger.info('========== %s(), <%s>   ========== is called' % (sys._getframe().f_code.co_name,request.env.user.name))
        return request.website.render('website_myaccount_base.mobile_myaccount_red_envelopes', {})

    @http.route(['/m/myaccount/orderlist/<categary>'], type='http', auth='user',website=True)
    def m_orderlist_by_categary(self,categary):
        categary=str(categary)
        value={}
        _logger.info('========== %s(), <%s>   ========== categary is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary))
        # 全部, 待支付, 待卖家发货, 待收货, 待评价, 维权
        return self.get_template_orderlist_by_categary(categary)

    @http.route(['/m/myaccount/orderlist/ajax/<categary>'], type='json', auth='user', methods=['POST'], website=True)
    def m_orderlist_ajax_categary(self,categary,limit=None,offset=None,**post):
        _logger.info('========== %s(), <%s>   ========== categary is %s' % (sys._getframe().f_code.co_name,request.env.user.name,categary))
        return self.get_template_orderlist_by_categary(categary,ajax=1,limit=limit,offset=offset)

    @http.route(['/m/myaccount/orderlist_search'], type='json', auth='user',methods=['POST'],website=True)
    def m_orderlist_search(self, search_text):
        # 订单搜索
        search_text=str(search_text)
        orders = request.website.get_order_search(search_text)
        _logger.info('========== %s(), <%s>   ========== commission_lines is %s' % 
            (sys._getframe().f_code.co_name,
            request.env.user.name,
            search_text))

        value={'fields_list': [('state','=','search')], 'flag':'search'}
        result = {}
        result['orders'] = request.website._render('website_myaccount_base.public_mobile_foreach_productList', {
            'value':value, 'orders':orders}).decode('utf-8')
        return result

    @http.route(['/m/myaccount/order/logistics_detail/<order_id>'], type='http', auth='user', website=True)
    def m_order_logistics_detail(self,order_id,**post):
        env = request.env
        partner = self.get_partner_company()
        if partner:
            _logger.info('========== %s(), <%s>   ========== partner is %s' % (sys._getframe().f_code.co_name,request.env.user.name,partner))
            try:
                order = env['sale.order'].search(
                    [('partner_id', '=', partner.id),('id','=',order_id)])
            except Exception:
                order = env['sale.order'].sudo().search(
                    [('partner_id', '=', partner.id),('id','=',order_id)])

        else:
            order = []
        _logger.info('========== %s(), <%s>   ========== order is %s' % (sys._getframe().f_code.co_name,request.env.user.name,order))
        return request.website.render('website_myaccount_base.mobile_show_order_logistics_page', {'order': order})

    @http.route(['/m/myaccount/orderlist/action/<action>'], type='json', auth='user', methods=['POST'], website=True)
    def m_orderlist_action(self,action,order_id, **post):
        action=str(action)
        order_id=int(order_id)
        value = {}
        if action == 'draft_cancel':
            categary = 'draft'
            success=request.registry.get('sale.order').action_cancel(request.cr, SUPERUSER_ID, [order_id])
        if success:
            _logger.info('========== %s(), <%s>   ========== success is %s' % (sys._getframe().f_code.co_name,request.env.user.name,success))
            fields_list = self.get_order_fields_list()
            value={'fields_list': fields_list.get(categary),'flag':categary,'limit':None,'offset':None}
            ajax_value = {}
            ajax_value['categary_tab'] = request.website._render('website_myaccount_base.public_mobile_order_category_tab',{'value':value}).decode('utf-8')
            ajax_value['orderlist'] = request.website._render('website_myaccount_base.public_mobile_foreach_productList',{'value':value}).decode('utf-8')

            return ajax_value

    @http.route(['/myaccount/orders'],
                type='http', auth='user', website=True)
    def orders(self, container=None, **post):
        env = request.env
        partner = self.get_partner_company()
        if partner:
            orders = env['sale.order'].search(
                [('partner_id', '=', partner.id),
                 ('state', 'not in', ['cancel'])])
        else:
            orders = []
        return request.website.render(
            'website_myaccount_base.orders',
            {'orders': orders})


    @http.route(['/m/myaccount/order/detail/<order_id>'], type='http', auth='user', website=True)
    def m_order_detail(self, order_id=None, **post):
        env = request.env
        partner = self.get_partner_company()
        if partner:
            _logger.info('========== %s(), <%s>   ========== partner is %s' % (sys._getframe().f_code.co_name,request.env.user.name,partner))
            order = env['sale.order'].sudo().search(
                [('partner_id', '=', partner.id),('id','=',order_id)])
        else:
            order = []
        _logger.info('========== %s(), <%s>   ========== order is %s' % (sys._getframe().f_code.co_name,request.env.user.name,order))
        return request.website.render(
            'website_myaccount_base.m_sale_order_detail',
            {'order': order})

    # adit by liuzm
    # @http.route(['/m/myaccount/order/after_sale/<order_id>'], type='http', auth='user', website=True)
    # def m_order_after_sale(self, order_id=None, **post):
    #     return request.website.render('website_myaccount_base.mobile_order_activist_service_page', {})

    @http.route(['/myaccount/order/detail/<model("sale.order"):order_id>'],
                type='http', auth='user', website=True)
    def order_detail(self, order_id=None, **post):
        env = request.env
        partner = self.get_partner_company()
        if partner:
            orders = env['sale.order'].search(
                [('partner_id', '=', partner.id),('id','=',int(order_id))])
        else:
            orders = []
        return request.website.render(
            'website_myaccount_base.sale_order_detail',
            {'orders': orders})


    @http.route(['/myaccount/people'],
                type='http', auth='user', website=True)
    def people(self, container=None, **post):
        env = request.env
        partner = self.get_partner_company()
        if partner:
            people = env['res.partner'].search(
                [('upline_id', '=', partner.id)], order="create_date desc")
        else:
            people = []
        return request.website.render(
            'website_myaccount_base.mypeople',
            {'members': people})