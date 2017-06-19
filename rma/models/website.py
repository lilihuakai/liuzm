# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import osv, orm, fields
from openerp.addons.web.http import request
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from dateutil import tz  
from datetime import datetime

import time
import hashlib
import sys
import re
import logging
_logger = logging.getLogger(__name__)

class website(orm.Model):
    _inherit = 'website'
    def get_rma_claim_id(self, cr, uid, order_id, context=None):
        if not context:
            context = {}
        else:
            context = context.copy()
        orders = []
        rma_claim_id = self.pool.get('sale.order').browse(cr, uid, order_id, context=context).advance_id.id
        if not rma_claim_id:
            orders.append(order_id)
            context.update({
                'active_model': "sale.order",
                'active_ids': 1 and orders,
            })
            rma_claim_id = self.pool['sale.advance.rma.claim'].create(cr, uid, 
                {'order_id': order_id}, context=context)
        return rma_claim_id

    def get_after_sale_fields_list(self,field_name=None):
        value = {
            # 售后申请、进度查询
            'waiting_claim' : [('state','=','done'), ('claimed', '=', False)],
            'already_claimed' : [('state','=','done'), ('claim_exists', '=', True)],
        }
        if field_name is not None:
            return value.get(field_name)
        else:
            return value

    def get_after_sale_order_count_by_field(self,cr,uid,ids, field_name=None, context=None):
        domain = self.get_after_sale_fields_list(field_name)
        count = self.get_order_count_by_field(cr,uid,ids,domain).get('count')

        if count:
            return count
        else:
            return 0
