# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
from openerp.addons.crm import crm
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import html2plaintext


class crm_claim(osv.osv):
    """ Crm claim inherit
    """
    _inherit = "crm.claim"

    _columns = {
        'state': fields.selection([
                ('draft','Draft'),
                ('proforma','Pro-forma'),
                ('proforma2','Pro-forma'),
                ('open','Open'),
                ('paid','Paid'),
                ('cancel','Cancelled'),
            ], string='Status', default='draft'),
        'record_ids': fields.one2many("crm.claim.operation.record", 'claim_id', string="Operation Record"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
