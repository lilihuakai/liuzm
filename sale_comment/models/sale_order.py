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
from openerp.osv import osv, fields
from openerp import api

class sale_order(osv.Model):
    _inherit = 'sale.order'

    _columns = {
        'sale_comment_ids': fields.one2many("sale.comment", "order_id", string="Website Sale Comments"),
    }

    def test_create_comment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        comment_obj = self.pool.get("sale.comment")

        orders = self.browse(cr, uid, ids, context=context)
        for line in orders.order_line:
            comment_obj.create_comment(cr, uid, line.id, context=context)
