# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

{
    'name': 'Reset Stock Inventory Moves',
    'version': "1.0",
    "summary": """Reset Move | Delete Move | Balance Inventory | Cancel Move | Cancel Inventory | Reset Stock Move | Delete Stock Move | Cancel Stock Move""",
    "description": """
    """,
    'author': 'TidyWay',
    'website': 'http://www.tidyway.in',
    'category': 'stock',
    'depends': ["stock"],
    'data': [
        'security/reset_move.xml',
        'wizard/reset_move.xml'
    ],
    'price': 149,
    'currency': 'EUR',
    'installable': True,
    'license': 'OPL-1',
    'application': True,
    'auto_install': False,
    'images': ['images/correct_move.png'],
    'live_test_url': 'https://youtu.be/RwFqYxOrb7s'
}
