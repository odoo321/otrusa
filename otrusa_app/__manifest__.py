# -*- coding: utf-8 -*-
{
    'name': "otrusa_app",
    'version': 'beta.1.0',
    'category': 'Warehouse',
    'sequence': 1,
    'summary':
        """
            Custom app by OTRUSA.COM
        """,
    'description':
        """
            This app contain modification of view for OTRUSA.COM
        """,
    'author': "OTRUSA.COM",
    'website': "http://www.otrusa.com",
    'images': ['images/main_screenshot.png'],
    'depends': ['stock','sale','account','purchase'], # any module necessary for this one to work correctly
    'data': [
                # 'security/ir.model.access.csv',
                # 'views/sale_order_view.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,

    # only loaded in demonstration mode
}
