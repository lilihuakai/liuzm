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
# 3: imports of openerp
from openerp.osv import osv, fields
from openerp import api

class ProductTemplate(osv.Model):
    _inherit = 'product.template'

    _columns = {
        'sale_comment_ids': fields.one2many("sale.comment", "product_tmp_id", string="Website Sale Comments"),
        'rating': fields.integer(compute="_get_rating", string="Rating", store=True),
    }

    @api.depends("message_last_post")
    def _get_rating(self):
        """This method gets the rating for each rated template based on the
        comments, the rating per comment is stored in the mail.message model
        """
        self._cr.execute("""
            SELECT product_tmp_id, avg(rating)
            FROM sale_comment
            WHERE product_tmp_id IN %s AND rating > 0
            GROUP BY product_tmp_id""", (self._ids,))
        res = dict(self._cr.fetchall())
        for record in self:
            record.rating = res.get(record.id)
