{
    
    # App information
    'name': 'Cancel Purchase Order In Odoo',
    'version': '11.0',
    'category': 'purchase',
    'summary' : 'Allow to Cancel such Purchase Orders whose incoming shipment is processed / invoice is generated.',
    'license': 'OPL-1',
   
    
     # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    
          
    
    
    # Dependencies
    
    'depends': ['purchase','cancel_stock_picking_ept'],
    
    
    
    # Views
    'data': [
     'view/purchase_order.xml'
    ],
    
    'demo': [
    ],

   # Odoo Store Specific
    'images': ['static/description/Odoo-covor.jpg'],
     #'live_test_url' : 'https://goo.gl/xkUP1S',
    'price': '40' ,
    'currency': 'EUR',
    'live_test_url':'http://www.emiprotechnologies.com/free-trial?app=cancel-purchase-order-ept&version=11',
    
    'installable': True,
    'auto_install': False,
    'application': True,
}
