# -*- coding: utf-8 -*-pack
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    # App information
    'name': 'Cancel & Reset - Sales, Purchases and Pickings',
    'version': '11.0',
    'category': 'website',
    'license': 'OPL-1',
    'summary': 'Cancel & Reset - Sales, Purchases and Pickings app allows you to cancel processed sales order, purchase order & stock picking by just one click.',
    
    # Dependencies
    'depends': ['cancel_stock_picking_ept','cancel_purchase_order_ept','cancel_sale_order_ept'],
    
    # Odoo Store Specific
    'images': ['static/description/All-In-One-Cancle-Cover.jpg'], 
   
    # Author
    
    "author": "Emipro Technologies Pvt. Ltd.",
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    
    # Views
    'data': [],
    
    
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url': 'http://www.emiprotechnologies.com/free-trial?app=all-in-one-cancel-reset-ept&version=11&edition=enterprise',
    'currency': 'EUR',
}
