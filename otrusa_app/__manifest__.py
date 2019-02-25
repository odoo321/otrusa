# -*- coding: utf-8 -*-
{
    'name': "otrusa_app",

    'summary': """
        Custom app by OTRUSA.COM""",

    'description': """
        This app contain modification of view for OTRUSA.COM
    """,

    'author': "OTRUSA.COM",
    'website': "http://www.otrusa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'images': ['images/main_screenshot.png'],
    # any module necessary for this one to work correctly
    'depends': ['inventory','sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
