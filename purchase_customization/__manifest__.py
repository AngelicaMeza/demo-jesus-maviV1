# -*- coding: utf-8 -*-
{
        'name': "Purchase Customization",

    'summary': """
        Purchase Customization""",

    'description': """
        Customization Of Odoo's Base Purchase Module
    """,

    'author': "ItSales",
    'website': "https://www.itsalescorp.com/",
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/purchase_order_reports.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
