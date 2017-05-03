# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class website_config_settings(osv.osv_memory):
    _inherit = 'website.config.settings'

    _columns = {        
        'wechat_poster': fields.related('website_id', 'wechat_poster', type="binary", string='Wechat Share Poster',
            help="This field holds the image used as wechat share poster, limited to 1280x720px"),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
