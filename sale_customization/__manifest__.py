# -*- coding: utf-8 -*-
{
    'name': "Sale Customization",

    'summary': """
        Sale Customization""",

    'description': """
        Customization Of Odoo's Base Sale Module
    """,

    'author': "ItSales",
    'website': "https://www.itsalescorp.com/",
    'category': 'Sale',
    'version': '0.1',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/sale_order_reports.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
