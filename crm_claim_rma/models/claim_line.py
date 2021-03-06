# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Copyright 2013 Camptocamp
#    Copyright 2009-2013 Akretion,
#    Author: Emmanuel Samyn, Raphaël Valyi, Sébastien Beau,
#            Benoît Guillot, Joel Grand-Guillaume,
#            Osval Reyes, Yanina Aular
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
import calendar
import math
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from openerp import _, api, exceptions, fields, models
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)

from ..exceptions import (InvoiceNoDate, ProductNoSupplier)


class ClaimLine(models.Model):

    _name = "claim.line"
    _order = "date, priority desc"
    _inherit = 'mail.thread'
    _description = "List of product to return"
    _rec_name = "display_name"

    SUBJECT_LIST = [('none', 'Not specified'),
                    ('legal', 'Legal retractation'),
                    ('cancellation', 'Order cancellation'),
                    ('damaged', 'Damaged delivered product'),
                    ('error', 'Shipping error'),
                    ('exchange', 'Exchange request'),
                    ('lost', 'Lost during transport'),
                    ('perfect_conditions',
                     'Perfect Conditions'),
                    ('imperfection', 'Imperfection'),
                    ('physical_damage_client',
                     'Physical Damage by Client'),
                    ('physical_damage_company',
                     'Physical Damage by Company'),
                    ('other', 'Other')]
    WARRANT_COMMENT = [('valid', _("Valid")),
                       ('expired', _("Expired")),
                       ('not_define', _("Not Defined"))]

    number = fields.Char(readonly=True,
                         default='/',
                         help='Claim Line Identification Number')
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 readonly=False,
                                 change_default=True,
                                 default=lambda self:
                                 self.env['res.company'].
                                 _company_default_get('claim.line'))
    date = fields.Date('Claim Line Date',
                       select=True,
                       default=fields.date.today())
    name = fields.Text('Description',
                       default='none',
                       required=True,
                       help="More precise description of the problem")
    priority = fields.Selection([('0_not_define', 'Not Define'),
                                 ('1_normal', 'Normal'),
                                 ('2_high', 'High'),
                                 ('3_very_high', 'Very High')],
                                'Priority',
                                store=True,
                                compute='_compute_priority',
                                inverse='_inverse_priority',
                                help="Priority attention of claim line")
    claim_diagnosis = fields.Selection([('damaged', 'Product Damaged'),
                                        ('repaired', 'Product Repaired'),
                                        ('good', 'Product in good condition'),
                                        ('hidden',
                                         'Product with hidden physical '
                                         'damage')],
                                       help="To describe the line product "
                                       "diagnosis")
    claim_origin = fields.Selection(SUBJECT_LIST, 'Subject',
                                    required=True, help="To describe the "
                                    "line product problem")
    product_id = fields.Many2one('product.product', string='Product',
                                 help="Returned product")
    product_returned_quantity = fields.Float('Quantity',
                                             digits=(12, 2),
                                             help="Quantity of product "
                                             "returned")
    unit_sale_price = fields.Float(digits=(12, 2),
                                   help="Unit sale price of the product. "
                                   "Auto filled if return done "
                                   "by invoice selection. Be careful "
                                   "and check the automatic "
                                   "value as don't take into account "
                                   "previous refunds, invoice "
                                   "discount, can be for 0 if product "
                                   "for free,...")
    return_value = fields.Float(compute='_compute_line_total_amount',
                                string='Total return',
                                help="Quantity returned * Unit sold price",)
    prodlot_id = fields.Many2one('stock.production.lot',
                                 string='Serial/Lot number',
                                 help="The serial/lot of the returned product")
    applicable_guarantee = fields.Selection([('us', 'Company'),
                                             ('supplier', 'Supplier'),
                                             ('brand', 'Brand manufacturer')],
                                            'Warranty type')
    guarantee_limit = fields.Date('Warranty limit',
                                  readonly=True,
                                  help="The warranty limit is "
                                       "computed as: invoice date + warranty "
                                       "defined on selected product.")
    warning = fields.Selection(WARRANT_COMMENT,
                               'Warranty',
                               readonly=True,
                               help="If warranty has expired")
    display_name = fields.Char('Name',
                               compute='_compute_display_name')
    date_deadline = fields.Date(related="claim_id.date_deadline")
    priority_date = fields.Date(compute='_compute_priority_date')

    @api.model
    def get_warranty_return_partner(self):
        return self.env['product.supplierinfo'].get_warranty_return_partner()

    warranty_type = fields.Selection(
        get_warranty_return_partner, readonly=True,
        help="Who is in charge of the warranty return treatment towards "
        "the end customer. Company will use the current company "
        "delivery or default address and so on for supplier and brand "
        "manufacturer. Does not necessarily mean that the warranty "
        "to be applied is the one of the return partner (ie: can be "
        "returned to the company and be under the brand warranty")
    warranty_return_partner = fields.Many2one('res.partner',
                                              string='Warranty Address',
                                              help="Where the customer has to "
                                              "send back the product(s)")
    claim_id = fields.Many2one('crm.claim',
                               string='Related claim',
                               ondelete='cascade',
                               help="To link to the case.claim object")
    state = fields.Selection([('draft', 'Draft'), ('refused', 'Refused'),
                              ('confirmed', 'Confirmed, waiting for product'),
                              ('in_to_control', 'Received, to control'),
                              ('in_to_treate', 'Controlled, to treate'),
                              ('treated', 'Treated')],
                             string='State', default='draft')
    substate_id = fields.Many2one('substate.substate', string='Sub state',
                                  help="Select a sub state to precise the "
                                       "standard state. Example 1: "
                                       "state = refused; substate could "
                                       "be warranty over, not in "
                                       "warranty, no problem,... . "
                                       "Example 2: state = to treate; "
                                       "substate could be to refund, to "
                                       "exchange, to repair,...")
    last_state_change = fields.Date(string='Last change',
                                    help="To set the"
                                    "last state / substate change")
    invoice_line_id = fields.Many2one('account.invoice.line',
                                      string='Invoice Line',
                                      help='The invoice line related'
                                      ' to the returned product')
    refund_line_id = fields.Many2one('account.invoice.line',
                                     string='Refund Line',
                                     help='The refund line related'
                                     ' to the returned product')
    move_in_id = fields.Many2one('stock.move',
                                 string='Move Line from picking in',
                                 help='The move line related'
                                 ' to the returned product')
    move_out_id = fields.Many2one('stock.move',
                                  string='Move Line from picking out',
                                  help='The move line related'
                                  ' to the returned product')
    location_dest_id = fields.Many2one('stock.location',
                                       string='Return Stock Location',
                                       help='The return stock location'
                                       ' of the returned product')
    claim_type = fields.Many2one(related='claim_id.claim_type',
                                 string="Claim Line Type",
                                 store=True, help="Claim classification")
    invoice_date = fields.Date(related='invoice_line_id.invoice_id.'
                                       'date_invoice',
                               help="Date of Claim Invoice")

    # Method to calculate total amount of the line : qty*UP
    @api.multi
    def _compute_line_total_amount(self):
        for line in self:
            line.return_value = (line.unit_sale_price *
                                 line.product_returned_quantity)

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        std_default = {
            'move_in_id': False,
            'move_out_id': False,
            'refund_line_id': False,
        }
        std_default.update(default)
        return super(ClaimLine, self).copy(default=std_default)

    @api.model
    def _get_priority_level(self):
        priority_max = self.env.user.company_id.priority_maximum
        priority_min = self.env.user.company_id.priority_minimum

        priority = "0_not_define"
        if self.invoice_date:
            days = fields.datetime.strptime(self.date, "%Y-%m-%d") - \
                fields.datetime.strptime(self.invoice_date,
                                         DEFAULT_SERVER_DATE_FORMAT)
            if days.days <= priority_max:
                priority = "3_very_high"
            elif priority_max < days.days <= priority_min:
                priority = "2_high"
            elif days.days > priority_min:
                priority = "1_normal"
        return priority

    @api.depends("priority_date", "invoice_line_id.invoice_id.date_invoice")
    def _compute_priority(self):
        """To determine the priority of claim line
        """
        for line_id in self:
            line_id.priority = line_id._get_priority_level()

    @api.multi
    def _compute_priority_date(self):
        for line_id in self:
            line_id.priority_date = line_id.claim_id.date

    @api.multi
    def _inverse_priority(self):
        """To determine the priority of claim line
        """
        support_group_id = self.env.ref('crm_claim_rma.group_rma_user')
        support_user_ids = support_group_id.users

        # Internal claims are created by warehouse users and they are not
        # allowed to edit supplier claims, but create supplier claims
        # can be created from internal ones, so if a user is validating
        # an internal claims this calculation should be applied.
        from_internal_claim = self.env.context.get(
            'validate_internal_claim', False)

        if not from_internal_claim and self.env.user not in support_user_ids:
            raise exceptions.ValidationError(
                _("You must belong to the group '%s' in order to be "
                  "allowed to set priority level") % support_group_id.name
            )
        # Having priority level and invoice date an aproximation of
        # claim date can be computed
        priority_max = self.env.user.company_id.priority_maximum
        priority_min = self.env.user.company_id.priority_minimum
        for line_id in self:
            invoice_date = line_id.invoice_line_id.invoice_id.date_invoice

            # functionally this is not possible, but tested for
            # default values
            if not invoice_date:
                continue

            days = priority_min + 1
            if line_id.priority == "3_very_high":
                days = priority_max
            elif line_id.priority == "2_high":
                days = (priority_max + priority_min) * .5

            line_id.priority_date = fields.datetime.strptime(
                invoice_date,
                DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=days)

    def _get_subject(self, num):
        """Based on a subject number given, it returns the proper subject
        value only if the number is between the limits, in counter case is the
        first value of SUBJECT_LIST will be returned
        """
        subject_index = num - 1 if 0 < num <= len(self.SUBJECT_LIST) else 0
        return self.SUBJECT_LIST[subject_index][0]

    @staticmethod
    def warranty_limit(start, warranty_duration):
        """Take a duration in float, return the duration in relativedelta
        ``relative_delta(months=...)`` only accepts integers.
        We have to extract the decimal part, and then, extend the delta with
        days.

        """
        decimal_part, months = math.modf(warranty_duration)
        months = int(months)
        # If we have a decimal part, we add the number them as days to
        # the limit.  We need to get the month to know the number of
        # days.
        delta = relativedelta(months=months)
        monthday = start + delta
        __, days_month = calendar.monthrange(monthday.year, monthday.month)
        # ignore the rest of the days (hours) since we expect a date
        days = int(days_month * decimal_part)
        return start + relativedelta(months=months, days=days)

    def _get_warranty_limit_values(self, invoice, claim_type, product,
                                   claim_date):
        """Calculate the warranty of claim line product depending of
        invoice date.
        """
        if not (invoice and claim_type and product and claim_date):
            return {'guarantee_limit': False, 'warning': False}

        # If the invoice has invoice date, the warranty of
        # damaged product can be calculated
        invoice_date = invoice.date_invoice
        if not invoice_date:
            raise InvoiceNoDate

        # First, the warranty is set as not defined
        warning = 'not_define'

        # The invoice date is converted to DATE FORMAT
        invoice_date = datetime.strptime(invoice_date,
                                         DEFAULT_SERVER_DATE_FORMAT)

        warranty_duration = False
        # If claim is supplier type, then, search the warranty specified for
        # the supplier in the suppliers configured for the damaged product.
        supplier_type = self.env.ref('crm_claim_rma.crm_claim_type_supplier')

        if claim_type == supplier_type:
            seller_id = product.seller_ids.filtered(
                lambda r: r.name == invoice.partner_id)
            if not seller_id:
                raise ProductNoSupplier
            warranty_duration = seller_id.warranty_duration
            if not warranty_duration:
                raise exceptions.Warning(
                    _("Supplier warranty period for one or more products in "
                      "your claim is(are) not set"))
        else:
            # If the claim is not supplier type, then, take the basic warranty
            # configured in the product
            warranty_duration = product.warranty

        # Get the limit_date
        limit_date = self.warranty_limit(invoice_date, warranty_duration)
        claim_date = datetime.strptime(claim_date,
                                       DEFAULT_SERVER_DATETIME_FORMAT)

        # Warranty is valid only when claim date is lesser than limit date,
        # in counter case the warranty is expired
        warning = 'valid' if claim_date <= limit_date else 'expired'

        # if the conditions above are not met, then, the warranty
        # is not defined
        limit_date = limit_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return {'guarantee_limit': limit_date, 'warning': warning}

    def set_warranty_limit(self):
        self.ensure_one()

        claim_id = self.claim_id
        invoice_id = self.invoice_line_id.invoice_id
        values = self._get_warranty_limit_values(
            invoice_id, claim_id.claim_type, self.product_id, claim_id.date)
        self.write(values)
        return True

    @api.returns('stock.location')
    def get_destination_location(self, product_id, warehouse_id):
        """Compute and return the destination location to take
        for a return. Always take 'Supplier' one when return type different
        from company.
        """
        location_dest_id = warehouse_id.lot_stock_id

        seller_id = product_id.seller_ids and product_id.seller_ids[0]
        if seller_id and seller_id.warranty_return_partner != 'company' \
                and seller_id.name \
                and seller_id.name.property_stock_supplier:
            location_dest_id = seller_id.name.property_stock_supplier

        return location_dest_id

    def _warranty_return_address_values(self, product, company, warehouse):
        """Return the partner to be used as return destination and
        the destination stock location of the line in case of return.

        We can have various cases here:
            - company or other: return to company partner or
              crm_return_address_id if specified
            - supplier: return to the supplier address
        """
        if not (product and company and warehouse):
            return {
                'warranty_return_partner': False,
                'warranty_type': False,
                'location_dest_id': False
            }
        seller_ids = product.seller_ids
        if seller_ids:
            seller_id = seller_ids[0]
            return_address_id = seller_id.warranty_return_address
            return_type = seller_id.warranty_return_partner
        else:
            # when no supplier is configured, returns to the company
            return_address_id = (company.crm_return_address_id or
                                 company.partner_id)
            return_type = 'company'
        location_dest = self.get_destination_location(product, warehouse)
        return {
            'warranty_return_partner': return_address_id.id,
            'warranty_type': return_type,
            'location_dest_id': location_dest.id
        }

    def set_warranty_return_address(self):
        self.ensure_one()
        claim_id = self.claim_id
        values = self._warranty_return_address_values(
            self.product_id, claim_id.company_id, claim_id.warehouse_id)
        self.write(values)
        return True

    @api.multi
    def set_warranty(self):
        """Calculate warranty limit and address
        """
        for line_id in self:
            if not line_id.product_id:
                raise exceptions.Warning(
                    _('Error'), _('Please set product first'))

            # 因为售后单由sale.order生成，不存在发票明细，忽略此判断
            # if not line_id.invoice_line_id:
            #     raise exceptions.Warning(
            #         _('Error'), _('Please set invoice first'))

            # line_id.set_warranty_limit()
            line_id.set_warranty_return_address()
        return True

    @api.model
    def _get_sequence_number(self):
        """@return the value of the sequence for the number field in the
        claim.line model.
        """
        return self.env['ir.sequence'].get('claim.line')

    @api.model
    def create(self, vals):
        """@return write the identify number once the claim line is create.
        """
        vals = vals or {}
        if ('number' not in vals) or (vals.get('number', False) == '/'):
            vals['number'] = self._get_sequence_number()
        res = super(ClaimLine, self).create(vals)
        return res

    @api.multi
    def _compute_display_name(self):
        for line_id in self:
            line_id.display_name = "%s - %s" % (
                line_id.claim_id.code, line_id.name)

    @api.multi
    def name_get(self):
        names = []
        for line_id in self:
            names.append((line_id.id, "%s - %s" %
                          (line_id.claim_id.code, line_id.name)))
        return names
