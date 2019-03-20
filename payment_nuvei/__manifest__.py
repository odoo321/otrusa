# -*- coding: utf-8 -*-

{
    'name': "DTR Nuvei Payment Acquirer",
    'version': '1.1',
    'summary': """
        Nuvei Payment Acquirer
    """,
    'description': """
Description
-----------
    - Nuvei Payment Acquirer

Changelog
---------

**Version 1.1**
    - Nuvei Payment Acquirer

    """,
    'author': "Dataroot Asia Co.,Ltd",
    'website': "",
    'created_by': 'Siddharth K',
    'category': 'Payment',
    'depends': ['payment', 'website_sale'],
    'external_dependencies': {'python': ['xmltodict']},
    'data': [
        'wizard/authorize_and_capture_wizard_view.xml',
        'views/assets.xml',
        'views/auto_reconciliation_views.xml',
        'views/invoice_payment_template.xml',
        'views/payment_views.xml',
        'views/sale_order_views.xml',
        'views/payment_nuvei_templates.xml',
        'data/email_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'demo': [
    ],
}
