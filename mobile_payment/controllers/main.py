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
from openerp import http

_logger = logging.getLogger(__name__)


class PaymentController(http.Controller):
 
    @http.route('/payment/parameters/', type='http', auth='user', website=True)
    def payment_parameters(self, **post):
        """ Payment Parameters"""
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        user = pool.get('res.users').browse(cr, uid, uid)
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

        user = pool.get('res.users').browse(cr, uid, uid)

        _logger.info('========== payment_pay2user ==========post=%s'%post)

        if user.partner_id.name_real and user.partner_id.default_acquirer_id.id:
            commissions = pool.get('account.invoice').browse(cr, uid, uid)
            return request.website.render("mobile_payment.payment_pay2user", 
                {'user': user, 'commissions': commissions})
        else:
            redirect = request.params.get('redirect') or '/'
            return http.redirect_with_hash(redirect)
