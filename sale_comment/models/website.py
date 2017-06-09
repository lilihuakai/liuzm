# -*- coding: utf-8 -*-
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
import openerp
from openerp.osv import orm

class website(orm.Model):
    _inherit = 'website'

    def get_sale_comment_fields_list(self):
        value = {
            # 待评价、待晒单、已评价
            'waiting_comment' : [('state','=','done'), ('is_commented', '=', False)],
            'waiting_public' : [('state','=','done'), ('is_public', '=', False)],
            'already_comment' : [('state','=','done'), ('is_commented', '=', True)],
        }

        return value