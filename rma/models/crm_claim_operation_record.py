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
from openerp.osv import osv, fields
import time


class CrmClaimOperationRecord(osv.Model):
    _name = "crm.claim.operation.record"
    _description = "Crm Claim Operation Record"

    _columns = {
        'author_id': fields.many2one('res.partner', 'Author'),
        'record_date': fields.datetime('Record Date'),
        'record_body': fields.char('Record Description'),
        'claim_id':fields.many2one('crm.claim', "Related Crm Claim ID"),
    }

    _order = "record_date desc"

    def _prepare_record(self, cr, uid, claim_id, author_id, record_date=None, record_body=None, context=None):
        if context is None:
            context = {}
        if not record_date:
            record_date = time.strftime("%Y-%m-%d %H:%M:%S")

        value = {}
        value['claim_id'] = claim_id
        value['author_id'] = author_id
        value['record_date'] = record_date
        value['record_body'] = record_body
        return value


    def create_record(self, cr, uid, claim_id, author_id, record_date=None, record_body=None, context=None):
        """Create the record by those values

            :param claim_id: crm claim ID(int)
            :param author_id: res partner ID(int)
            :param record_date: the record_date of given(datetime)
            :param record_body: description of record(char)
        """
        if context is None:
            context = {}
        value = self._prepare_record(cr, uid, claim_id, author_id, record_date, record_body, context=context)
        comm_ids = self.create(cr, uid, value, context=context)
        return comm_ids
