# -*- coding: utf-8 -*-

try:
    import simplejson as json
except ImportError:
    import json
import logging
import pprint
import urllib2
import werkzeug
import time
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp import http

_logger = logging.getLogger(__name__)


class PaymentController(http.Controller):
 
    @http.route('/payment/parameters/', type='http', auth='user', website=True)
    def payment_parameters(self, **post):
        """ Payment Parameters"""
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        user = pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        acquirer_obj = pool.get('payment.acquirer')
        acquirer_ids = acquirer_obj.search(cr, SUPERUSER_ID, [('website_published','=',True)])
        acquirers = acquirer_obj.browse(cr, SUPERUSER_ID, acquirer_ids, context)

        # if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
        if request.httprequest.method == 'GET':
            _logger.info('========== payment_parameters ==========post=%s'%request.params.get('redirect'))
            return request.website.render("mobile_payment.payment_parameters", 
                {'partner': user.partner_id, 'acquirers': acquirers, 'redirect': request.params.get('redirect')})
        else:
            _logger.info('========== payment_parameters ==========post=%s'%post)
            if post.get('default_acquirer_id') and post.get('name_real'):
                user.write({
                    'default_acquirer_id': int(post.get('default_acquirer_id')),
                    'name_real': post.get('name_real'),
                    })
            else:
                return request.website.render("mobile_payment.payment_parameters", {
                    'partner': user.partner_id, 
                    'acquirers': acquirers,
                    'error': _('Receipt Method and Real Name Required.'),
                    })

            redirect = request.params.get('redirect') or '/'
            return http.redirect_with_hash(redirect)

    # 提现支付前，判断用户信息是否完整 add by Liuzm 20170516
    @http.route('/payment/pay2user/', type='http', auth='user', website=True)
    def payment_pay2user(self, **post):
        """ Payment Judgement"""
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        user = pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)

        # 如果没有设置实名或收款方式，则跳到相应的页面
        if (not user.partner_id.name_real) or (not user.partner_id.default_acquirer_id):
            return http.redirect_with_hash('/payment/parameters/?redirect=/payment/pay2user/')

        # 计算'提现中'的佣金
        if user.partner_id:
            user.partner_id.action_calc_commission()

        inv_obj = pool.get('account.invoice')
        ids = inv_obj.search(cr, SUPERUSER_ID, [('partner_id', '=', user.partner_id.id)], context=context)
        commissions = inv_obj.browse(cr, SUPERUSER_ID, ids, context=context)
        return request.website.render("mobile_payment.payment_pay2user", 
            {'user': user, 'commissions': commissions})

    # 对具体佣金发票进行支付 add by Liuzm 20170519
    @http.route('/payment/pay2user/pay_commission', type='json', auth='user', website=True)
    def payment_pay2user_commission(self, invoice_id, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        invoice_id = int(invoice_id)

        _logger.info('===============  payment_pay2user_commission  ============== invoice_id = %s' % invoice_id)
        commission = registry.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        return commission.pay2user()

    # 对具体用户进行佣金结算 add by Liuzm 20170519
    @http.route('/payment/pay2user/compute_commission', type='json', auth='user', website=True)
    def paymeny_pay2user_compute_comm(self, partner_id, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        partner_id = int(partner_id)

        _logger.info('==============  paymeny_pay2user_compute_comm  ============== partner_id = %s' % partner_id)
        return registry.get('res.partner').action_calc_commission(cr, uid, partner_id, context=context)
