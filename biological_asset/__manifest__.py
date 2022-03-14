# -*- coding: utf-8 -*-
{
    'name': "Biological Asset",

    'summary': """
        Biological Asset""",

    'description': """
        Implementation of the posture curve as an asset depreciation method
    """,

    'author': "ItSales",
    'website': "https://www.itsalescorp.com/",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['base', 'account_asset'],

    'data': [
        'security/ir.model.access.csv',
        'views/biological_asset_models_views.xml',
        'views/biological_asset_views.xml',
    ],
}
