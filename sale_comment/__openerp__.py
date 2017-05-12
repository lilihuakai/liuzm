# -*- encoding: utf-8 -*-
{
    "name": "Sale Order Comment & Rate",
    "version": "1.0",
    "author": "Liuzm",
    "category": "Website",
    "website": "http://oducn.com/",
    "license": "AGPL-3",
    'description': """
销售留言、评论功能
========================================================
产品详情页展示用户留言内容
    """,
    "depends": [
        "website_sale"
    ],
    "demo": [
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/layout.xml",
        "views/star_rate.xml",
        "views/templates.xml",
        "views/sale_comment.xml",
        "views/sale_order_view.xml",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
