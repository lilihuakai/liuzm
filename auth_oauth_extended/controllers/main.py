#-*- coding: utf-8 -*-

from werkzeug.exceptions import BadRequest
import functools
import logging
import simplejson
import urllib2
import urlparse
import urlparse
import werkzeug.urls
import werkzeug.utils

import openerp

from openerp import fields,models
from openerp import http
from openerp import SUPERUSER_ID
from openerp.addons.auth_oauth.controllers.main import fragment_to_query_string
from openerp.addons.auth_oauth.controllers.main import OAuthLogin
from openerp.addons.auth_oauth.controllers.main import OAuthController
from openerp.addons.auth_signup.controllers.main import AuthSignupHome as Home
from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.web.controllers.main import db_monodb
from openerp.addons.web.controllers.main import ensure_db
from openerp.addons.web.controllers.main import login_and_redirect
from openerp.addons.web.controllers.main import set_cookie_and_redirect
from openerp.http import request
from openerp.modules.registry import RegistryManager
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class OAuthLogin_extend(OAuthLogin):
    # 添加微信认证处理
    def list_providers(self):
        try:
            provider_obj = request.registry.get('auth.oauth.provider')
            providers = provider_obj.search_read(request.cr, SUPERUSER_ID, 
                [('enabled', '=', True), ('auth_endpoint', '!=', False), ('validation_endpoint', '!=', False)])
            # TODO in forwardport: remove conditions on 'auth_endpoint' and 'validation_endpoint' 
            # when these fields will be 'required' in model
        except Exception:
            providers = []
        for provider in providers:
            if provider['provider_type'] != 'weixin':
                return_url = request.httprequest.url_root + 'auth_oauth/signin'
                state = self.get_state(provider)
                params = dict(
                    response_type='token',
                    client_id=provider['client_id'],
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    state=simplejson.dumps(state),
                )
            else:
                return_url = request.httprequest.url_root + 'auth_oauth/signin'
                state = self.get_state(provider)
                params = dict(
                    response_type='code',
                    appid=provider['client_id'],                                            #微信认证ID
                    # redirect_uri=return_url,
                    redirect_uri="http://www.bw47.com.cn",  #just for test
                    scope=provider['scope'],
                    state=simplejson.dumps(state),
                )

            provider['auth_link'] = provider['auth_endpoint'] + '?' + werkzeug.url_encode(params)

        return providers


class OAuthController_extend(OAuthController):

    @http.route('/auth_oauth/signin', type='http', auth='none')
    @fragment_to_query_string
    def signin(self, **kw):
        kw = simplejson.loads(simplejson.dumps(kw).replace('+',''))
        state = simplejson.loads(kw['state'])
        dbname = state['d']
        provider = state['p']
        context = state.get('c', {})
        registry = RegistryManager.get(dbname)
        with registry.cursor() as cr:
            try:
                u = registry.get('res.users')
                credentials = u.auth_oauth(cr, SUPERUSER_ID, provider, kw, context=context)
                cr.commit()
                action = state.get('a')
                menu = state.get('m')
                redirect = werkzeug.url_unquote_plus(state['r']) if state.get('r') else False
                url = '/web'
                if redirect:
                    url = redirect
                elif action:
                    url = '/web#action=%s' % action
                elif menu:
                    url = '/web#menu_id=%s' % menu
                return login_and_redirect(*credentials, redirect_url=url)
            except AttributeError:
                # auth_signup is not installed
                _logger.error("auth_signup not installed on database %s: oauth sign up cancelled." % (dbname,))
                url = "/web/login?oauth_error=1"
            except openerp.exceptions.AccessDenied:
                # oauth credentials not valid, user could be on a temporary session
                _logger.info('OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies')
                url = "/web/login?oauth_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception, e:
                # signup error
                _logger.exception("OAuth2: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return set_cookie_and_redirect(url)

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
