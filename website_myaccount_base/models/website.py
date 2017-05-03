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
    def get_order_fields_list(self,field_name=None):
        value = {
            # 全部, 待支付, 待卖家发货, 待收货, 待评价, 维权
            'all' : [('state','not in',['cancel'])],  # 全部
            'draft' : [('state','=','draft')],  # 待支付
            # 'draft' : [('state','in',['draft'])],  # 待支付
            'undelivered' : ['|','&',('state','in',['manual','progress','done']),('logistics_state', '=', 'waiting_send'),'&',('state','in',['manual','progress']),('logistics_state', '=', 'sent')],  # 待卖家发货
            'wait_delivery' : [('state','=','done'),('logistics_state','=','sent')],  # 待收货
            'wait_comment' : [('logistics_state','=','signed')],  # 待评价
            'activist' : [('state','=','done')]  # 维权
        }
        if field_name is not None:
            return value.get(field_name)
        else:
            return value

    def get_partner_id(self,cr,uid,context=None):
        user=self.pool.get('res.users').browse(cr,uid,uid,context=context)
        partner_id = user.partner_id.id
        _logger.info('========== %s(), <%s>   ========== partner_id=%s , parent_id=%s' % (sys._getframe().f_code.co_name,request.env.user.name,partner_id,user.partner_id.parent_id.id))

        return partner_id
    def get_partner_name(self,cu,uid,context=None):
        user=self.pool.get('res.users').browse(cr,uid,uid,context=context)
        partner_name = user.partner_id.name
        return partner_name


    def user_image_url(self, cr, uid, user, field, size=None, context=None):
        """Returns a local url that points to the image field of a given browse record."""

        id = '%s_%s' % (user.id, hashlib.sha1(time.strftime('%Y-%m-%d %H:%M:%S') or '').hexdigest()[0:7])
        size = '' if size is None else '/%s' % size
        return '/website/image/%s/%s/%s%s' % ('res.users', id, field, size)


    def sudo_image_url(self, cr, uid, record, field, size=None, context=None):
        """Returns a local url that points to the image field of a given browse record."""
        # model = record._name
        # sudo_record = record.sudo()
        # id = '%s_%s' % (record.id, hashlib.sha1(sudo_record.write_date or sudo_record.create_date or '').hexdigest()[0:7])
        # size = '' if size is None else '/%s' % size
        # return '/website/image/%s/%s/%s%s' % (model, id, field, size)
        return self.image_url(cr, SUPERUSER_ID, record, field, size=size, context=context)

    def get_default_orderlist_record_count(self,offset=None,limit=None):
        if offset is None:
            offset = 0
        if limit is None:
            limit = 10
        return {'offset':offset, 'limit':limit}

    def get_orderlist_customize_domain(self,cr,uid,fields_list=None):
        partner_id = self.get_partner_id(cr,uid)
        must_field_list= [('partner_id', '=', partner_id), ('amount_total','>=',0.01)]
        new_domain= self.append_field_list(must_field_list, fields_list)
        return new_domain

    def get_order_logistics_detail_tel_highlight(self,order_logistics_line_obj):
        if order_logistics_line_obj:
            for package in order_logistics_line_obj:
                for line in package:
                    line.log_context = self.get_order_logistics_tel_highlight(line.log_context)

        return order_logistics_line_obj

    def get_order_logistics_tel_highlight(self,log_context):
        init_log_context = log_context
        # 正则匹配 手机号 或 固话,  若匹配到, 则重新渲染手机号
        pattern=re.compile(r'(?:\+86)?(\d{3})\d{8}|(?:\+86)?(0\d{2,3})\d{7,8}')
        has_tel = re.search(pattern,log_context)
        if has_tel is not None:
            def replace_tel(matched):
                tel = matched.group();
                # replace 13312341234  to  <a>13312341234</a>
                replace_string = '<a class="logistics_courier" href="tel://'+tel+'">'+tel+'</a>'
                return replace_string
            log_context = re.sub(pattern,replace_tel,log_context)

        if init_log_context != log_context:
            _logger.info('========== %s(), <%s>   ==========is used highlight tel, log_context is %s' % (sys._getframe().f_code.co_name,request.env.user.name,log_context))
        return log_context


    def get_order_logistics_top1(self, cr,uid,order_id,context=None):
        try:
            order = self.pool.get('sale.order').browse(cr,uid,order_id,context=context)
        except Exception:
            order = self.pool.get('sale.order').browse(cr,SUPERUSER_ID,order_id,context=context)
        value = {}
        logistics = order.logistics_line
        # 分多个包裹出发,每个包裹有多条记录
        if logistics:
            logistics_top1 = logistics[0].logistics_line[0]

        if logistics and logistics_top1:
            log_context = logistics_top1.log_context
            log_time = logistics_top1.log_time
            log_context = self.get_order_logistics_tel_highlight(log_context)
            value.update({'log_time' : log_time, 'log_context': log_context})

        _logger.info('========== %s(), <%s>   ==========logistics is %s, value is %s, order_id is %s' % (sys._getframe().f_code.co_name,request.env.user.name,logistics,value,order_id))
        return value;

    def append_field_list(self,old_fields_list,new_fields_list=None):
        # if None,  convert to list
        if new_fields_list == None:
            new_fields_list = []
        # if type(new_fields_list) == tuple , convert to list
        if isinstance(new_fields_list,tuple):
            new_fields_list = [new_fields_list]
        return old_fields_list + new_fields_list

    def try_func(self,func):
        try:
            func()
        except Exception as e:
            _logger.info('========== %s(), <%s>   ========== Exception:e is %s:%s' % (sys._getframe().f_code.co_name,request.env.user.name,Exception,e))
            pass

    def public_get_order_ids_match_for_field(self,cr,uid,fields_list,offset=None,limit=None,context=None):
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)

        order_ids = self.pool.get('sale.order').search(cr,uid,fields_list,context=context,offset=offset,limit=limit)
        _logger.info('========== %s(), <%s>   ==========uid is %s, len(order_ids) is %s fields_list is %s,request.uid is %s' % (sys._getframe().f_code.co_name,request.env.user.name,uid,len(order_ids),fields_list,request.uid))
        # def test_1():
        #     tmp_id = self.pool.get('sale.order').search(cr,uid,fields_list,context=context,offset=0,limit=10)
        #     tmp_id_count = len(tmp_id)
        #     _logger.info('========== %s(), <%s>   ========== tmp_id is %s,tmp_id_count is %s' % (sys._getframe().f_code.co_name,request.env.user.name,tmp_id,tmp_id_count))
        # def test_2():
        #     tmp_id = self.pool.get('sale.order').search(cr,uid,fields_list,context=context,offset=20,limit=10)
        #     tmp_id_count = len(tmp_id)
        #     _logger.info('========== %s(), <%s>   ========== tmp_id is %s,tmp_id_count is %s' % (sys._getframe().f_code.co_name,request.env.user.name,tmp_id,tmp_id_count))

        # self.try_func(test_1)
        # self.try_func(test_2)
        return order_ids

    def public_get_order_obj_match_for_order_ids(self,cr,uid,order_ids,context=None):
        orders = self.pool.get('sale.order').browse(cr,uid,order_ids,context=context)
        _logger.info('========== %s(), <%s>   ==========uid is %s,  order_ids is %s' % (sys._getframe().f_code.co_name,request.env.user.name,uid,order_ids))
        return orders


    def get_order_match_for_field(self,cr,uid,ids,fields_list,limit=None,offset=None,context=None):
        # domain = self.get_orderlist_customize_domain(cr,uid,fields_list)
        # order_ids = self.public_get_order_ids_match_for_field(cr,uid,domain,limit=limit,offset=offset)
        # orders = self.public_get_order_obj_match_for_order_ids(cr,uid,order_ids)
        orders_dict = self.public_get_order_ids_10_record(cr,uid,ids,fields_list,offset,limit,context=None)
        _logger.info('===== %s(), <%s>  ===== orders_dict=%s' % (sys._getframe().f_code.co_name,request.env.user.name,orders_dict))
        return orders_dict

    def public_get_order_ids_10_record(self,cr,uid,ids,fields_list,offset=None,limit=None,context=None):
        if offset is None:
            offset = self.get_default_orderlist_record_count().get('offset')
        if limit is None:
            limit = self.get_default_orderlist_record_count().get('limit')

        domain = self.get_orderlist_customize_domain(cr,uid,fields_list)
        order_ids = self.public_get_order_ids_match_for_field(cr,uid,domain,offset=offset,limit=limit)
        _logger.info('========== %s(), <%s>   ========== len(order_ids) is %s, order_ids=%s' % (sys._getframe().f_code.co_name,request.env.user.name,len(order_ids),order_ids))
        # if !empty , !0 , !None
        value = {}
        if ((not order_ids) and offset)  or (len(order_ids) < limit):
            value.update({'not_enough_data': 1})

        orders = self.public_get_order_obj_match_for_order_ids(cr,uid,order_ids)
        value.update({'orders':orders})
        return value

    def get_order_search(self,cr,uid,ids,search_text,context=None):
        search_str=str(search_text)
        # search_int=int(search_text)

        domain = []
        # 字符类型搜索条件
        domain += [('date_order', 'ilike', search_str)]
        # domain += ['|', ('date_order', 'ilike', search_str), ('order_line.display_name', 'ilike', search_str)]
        # 数字类型搜索条件
        # domain += ['|', '|', '|',  '|',  '|',  '|', ('product_count', 'ilike', search_int),
        #     ('cash_amount', 'ilike', search_int), 
        #     ('freight', 'ilike', search_int), 
        #     ('order_line.display_name', 'ilike', search_int), 
        #     ('order_line.price_unit', 'ilike', search_int), 
        #     ('order_line.product_uom_qty', '=', search_int)]

        orders_ids = self.pool.get('sale.order').search(cr,uid,domain,context=context)
        orders = self.pool.get('sale.order').browse(cr,uid,orders_ids,context=context)

        _logger.info('========== %s(), <%s>   ========== orders_ids is %s,len(ids) is %s, search_text is %s, domain is %s' % 
            (sys._getframe().f_code.co_name,
            request.env.user.name,
            orders_ids,
            len(orders_ids),
            search_text,
            domain))
        return orders

    def get_order_count_list(self,cr,uid,ids,field_name=None):
        json  = self.get_order_fields_list()
        value = {}
        for k,v in json.items():
            count = self.get_order_count_by_field(cr,uid,ids,v).get('count')
            value.update({k+'_count':count})

        _logger.info('========== %s(), <%s>   ========== value is %s' % (sys._getframe().f_code.co_name,request.env.user.name,value))
        if field_name is not None:
            return value.get(field_name)
        else:
            return value

    def get_order_count_by_field(self,cr,uid,ids,fields_list,context=None):
        value = {}
        # 必要条件
        partner_id = self.get_partner_id(cr,uid)
        must_field_list= [('partner_id', '=', partner_id), ('amount_total','>=',0.01)]
        new_fields_list= self.append_field_list(must_field_list, fields_list)
        order_ids = self.public_get_order_ids_match_for_field(cr,uid,new_fields_list)
        count = len(order_ids)
        value.update({'count' : count})
        _logger.info('========== %s(), <%s>   ========== value is %s, fields_list is %s' % (sys._getframe().f_code.co_name,request.env.user.name,value,fields_list))
        return value

    def datetime_utc2local(self, cr, uid, ids, utc_datetime, utc_format='%Y-%m-%d %H:%M:%S', local_format='%Y-%m-%d %H:%M:%S', context=None):
        """
        转换日期同，传入 UTC 时间的字符串，返回本地时间字符串

        @param utc_datetime: date string like 2016-12-28 15:13:28
        @param utc_format: utc datetime format
        """
        # user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
              
        # UTC Time Zone  
        from_zone = tz.gettz('UTC')  
        # User Time Zone  
        to_zone = tz.gettz(context.get('tz') or "PRC")  
          
        utc = datetime.strptime(utc_datetime, utc_format)  
        # Tell the datetime object that it's in UTC time zone  
        utc = utc.replace(tzinfo=from_zone)  
          
        # Convert time zone  
        local = utc.astimezone(to_zone)  
        return datetime.strftime(local, local_format)  