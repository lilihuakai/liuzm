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

class res_users(models.Model):
    _inherit = 'res.users'


    def _auth_oauth_rpc(self, cr, uid, endpoint, access_token, context=None):
        params = werkzeug.url_encode({'access_token': access_token})
        if urlparse.urlparse(endpoint)[4]:
            url = endpoint + '&' + params
        else:
            url = endpoint + '?' + params
        f = urllib2.urlopen(url)
        response = f.read()
        if response.find('callback') == 0:
            response = response[response.index("(") + 1: response.rindex(")")]
        return simplejson.loads(response)

    def _auth_oauth_signin(self, cr, uid, provider, validation, params, context=None):

        """ retrieve and sign in the user corresponding to provider and validated access token
            :param provider: oauth provider id (int)
            :param validation: result of validation of access token (dict)
            :param params: oauth parameters (dict)
            :return: user login (str)
            :raise: openerp.exceptions.AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        try:

            provider_obj = self.pool['auth.oauth.provider'].read(cr, uid, provider, context=context)
            provider_type = provider_obj['provider_type']

            if provider_type == 'qq':
                oauth_uid = validation['openid']
            elif provider_type == 'weixin':
                oauth_uid = validation['openid']
            elif provider_type == 'weibo':
                oauth_uid = validation['userid']
            else:
                oauth_uid = validation['user_id']

            user_ids = self.search(cr, uid, [("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
            if not user_ids:
                raise openerp.exceptions.AccessDenied()
            assert len(user_ids) == 1
            user = self.browse(cr, uid, user_ids[0], context=context)
            user.write({'oauth_access_token': params['access_token']})
            return user.login
        except openerp.exceptions.AccessDenied, access_denied_exception:
            if context and context.get('no_user_creation'):
                return None
            state = simplejson.loads(params['state'])
            token = state.get('t')

            provider_obj = self.pool['auth.oauth.provider'].read(cr, uid, provider, context=context)
            provider_type = provider_obj['provider_type']

            if provider_type == 'qq':
                oauth_uid = validation['nickname']
            elif provider_type == 'weixin':
                oauth_uid = validation['openid']
            elif provider_type == 'weibo':
                oauth_uid = validation['userid']
            else:
                oauth_uid = validation['user_id']
            email = validation.get('email', '%_%s' % (provider_type, oauth_uid))
            name = validation.get('name', email)
            values = {
                'name': name,
                'login': email,
                'email': email,
                'oauth_provider_id': provider,
                'oauth_uid': oauth_uid,
                'oauth_access_token': params['access_token'],
                'active': True,
            }
            _logger.info(values)
            try:
                _, login, _ = self.signup(cr, uid, values, token, context=context)
                return login
            except SignupError:
                _logger.info(SignupError)
                raise access_denied_exception


    def auth_oauth(self, cr, uid, provider, params, context=None):
        # Advice by Google (to avoid Confused Deputy Problem)
        # if validation.audience != OUR_CLIENT_ID:
        # abort()
        # else:
        # continue with the process
        access_token = params.get('access_token')
        validation = self._auth_oauth_validate(cr, uid, provider, access_token)

        provider_obj = self.pool['auth.oauth.provider'].read(cr, uid, provider, context=context)
        provider_type = provider_obj['provider_type']

        if provider_type == 'qq':
            oauth_uid = 'openid'
        elif provider_type == 'weixin':
            oauth_uid = 'openid'
        elif provider_type == 'weibo':
            oauth_uid = 'userid'
        else:
            oauth_uid = 'user_id'

        if not validation.get(oauth_uid):
            raise openerp.exceptions.AccessDenied()
        # retrieve and sign in user
        login = self._auth_oauth_signin(cr, uid, provider, validation, params, context=context)
        if not login:
            raise openerp.exceptions.AccessDenied()
        # return user credentials
        return (cr.dbname, login, access_token)


#
