# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author: Yanina Aular
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

{
    "name": "App RMA",
    "version": "8.0.1.0.0",
    "author": "Vauxoo,Odoo Community Association (OCA)",
    "category": "Generic Modules/CRM & SRM",
    "website": "http://www.vauxoo.com",
    "license": "AGPL-3",
    "depends": [
        "crm_rma_location",
        # "crm_rma_prodlot_invoice",
        "crm_claim_rma",
        # "crm_claim_product_supplier",
        # "crm_rma_claim_make_claim",
        # "crm_rma_advance_warranty",
        "website_myaccount_base",
        "common_code",
    ],
    'data': [
        "security/ir.model.access.csv",
        'wizard/sale_make_claim_advance.xml',
        'wizard/claim_invoice_refund_view.xml',
        'views/sale_view.xml',
        'views/crm_claim.xml',
        'views/rma_view.xml',
        'views/mobile_admin_route.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": True
}
