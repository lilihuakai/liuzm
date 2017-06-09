# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Liuzm
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# 1: imports of python lib
import time
import logging

# 3: imports of openerp
from openerp.osv import osv, fields
from openerp.tools.translate import _

# 6: Import of unknown third party lib
_logger = logging.getLogger(__name__)


class MailMessage(osv.Model):
    _name = "sale.comment"
    _description = "Sale Comment"

    _columns = {
        'comment_date': fields.datetime('Comment Date'),
        'seller_reply_date': fields.datetime('Seller Reply Date'),
        'chase_comment_date': fields.datetime('Chase Comment Date'),
        'comment_body': fields.html('Comment Contents', help='Automatically sanitized HTML contents'),
        'seller_reply_body': fields.html('Seller Reply Contents', help='Automatically sanitized HTML contents'),
        'chase_comment_body': fields.html('Chase Comment Contents', help='Automatically sanitized HTML contents'),
        'rating': fields.integer("Rating"),
        'order_id': fields.many2one('sale.order', "Related Sale Order ID"),
        'author_id': fields.many2one('res.partner', 'Author', help="Author of the comment."),
        'product_tmp_id': fields.many2one('product.template', "Related Product Template ID"),
        'website_published': fields.boolean(
            'Published', help="Visible on the website as a comment", copy=False,
        ),
        'is_anonymous': fields.boolean('Is Anonymous', default=False),
    }

    def _prepare_comment(self, cr, uid, line_id, context=None):
        line_obj = self.pool.get('sale.order.line')
        if context is None:
            context = {}
        description = context.get('description')
        rating = context.get('rating')
        website_published = context.get('website_published')
        is_anonymous = context.get('is_anonymous')

        values = {}
        for line in line_obj.browse(cr, uid, line_id, context=context):
            values['comment_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
            values['comment_body'] = description
            values['rating'] = rating
            values['order_id'] = line.order_id.id
            values['author_id'] = line.order_partner_id.id
            values['product_tmp_id'] = line.product_id.product_tmpl_id.id
            values['website_published'] = website_published
            values['is_anonymous'] = is_anonymous
        return values


    def create_comment(self, cr, uid, line_id, context=None):
        """Create the comment by those values

            :param line_id: sale order line ID(int)
        """
        if context is None:
            context = {}
        value = self._prepare_comment(cr, uid, line_id, context=context)
        comm_ids = self.create(cr, uid, value, context=context)
        _logger.info('========== %s(), <%s>   ========== value = %s comm_ids = %s ' % 
            (sys._getframe().f_code.co_name,request.env.user.name, value, comm_ids))

        return comm_ids
