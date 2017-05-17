# -*- coding: utf-8 -*-
{
    'name': 'Mobile Payment',
    'summary': 'pay to user',
    'category': 'Website',
    'version': '1.0',
    'description': """
Mobile Payment
=================================
* pay commission to user
* refund
    """,
    'author': 'Kenny',
    'website': 'http://oducn.com',
    'depends': ['website_mobile_menu','distribution_pay'],
    'data': [
        'views/layout.xml',
        'views/mobile_admin_route.xml',
    ],
    'installable': True,
    'application': False,
}
