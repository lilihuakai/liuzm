# -*- coding: utf-8 -*-
import random

from openerp import SUPERUSER_ID
from openerp.osv import osv, orm, fields
from openerp.addons.web.http import request
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class website(orm.Model):
    _inherit = 'website'

    _columns = {
        'wechat_poster': fields.binary("Wechat Share Poster",
            help="This field holds the image used as wechat share poster, limited to 1280x720px"),
    }


