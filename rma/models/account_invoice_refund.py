# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval

class account_invoice_refund(osv.osv_memory):

    _inherit = "account.invoice.refund"

    def claim_refund(self, cr, uid, ids, context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account claim refund’s ID or list of IDs

        """
        inv_obj = self.pool.get('account.invoice')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        claim_obj = self.pool.get('crm.claim')
        res_users_obj = self.pool.get('res.users')
        if context is None:
            context = {}

        for form in self.browse(cr, uid, ids, context=context):
            created_inv = []
            date = False
            period = False
            description = False
            company = res_users_obj.browse(cr, uid, uid, context=context).company_id
            mode = self.read(cr, uid, ids, ['filter_refund'],context=context)[0]['filter_refund']
            journal_id = form.journal_id.id

            if mode in ('cancel', 'modify'):
                raise osv.except_osv(_('Error!'), _('Cannot %s invoice now, You can only refund this claim.') % (mode))
            if form.period.id:
                period = form.period.id
            else:
                period = False
            if form.date:
                date = form.date
                if not form.period.id:
                        cr.execute("select name from ir_model_fields \
                                        where model = 'account.period' \
                                        and name = 'company_id'")
                        result_query = cr.fetchone()
                        if result_query:
                            cr.execute("""select p.id from account_fiscalyear y, account_period p where y.id=p.fiscalyear_id \
                                and date(%s) between p.date_start AND p.date_stop and y.company_id = %s limit 1""", (date, company.id,))
                        else:
                            cr.execute("""SELECT id
                                    from account_period where date(%s)
                                    between date_start AND  date_stop  \
                                    limit 1 """, (date,))
                        res = cr.fetchone()
                        if res:
                            period = res[0]
            if not period:
                raise osv.except_osv(_('Insufficient Data!'), \
                                        _('No period found on the claim.'))

            # 调用方法claimed_refund创建发票
            for claim in claim_obj.browse(cr, uid, context.get('active_ids'), context=context):
                if form.description:
                    description = form.description
                else:
                    description = claim.name

                refund_id = inv_obj.claimed_refund(cr, uid, ids, date, period, description, journal_id, context=context)
                refund = inv_obj.browse(cr, uid, refund_id, context=context)
                inv_obj.write(cr, uid, [refund.id], {'date_due': date})

                created_inv.append(refund_id)

            # 创建成功后，进入发票页面
            result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree3')
            id = result and result[1] or False

            result = act_obj.read(cr, uid, [id], context=context)[0]
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
