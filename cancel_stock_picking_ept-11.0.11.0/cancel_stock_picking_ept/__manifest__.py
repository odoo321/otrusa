{
    # App information
    'name': 'Cancel Stock Picking',
    'version': '11.0',
    'category': 'stock',
    'summary' : 'Allow to cancel Processed Picking.',
    'license': 'OPL-1',
   
    
     # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    
  
    
    # Dependencies
       
    'depends': ['stock','account_cancel'],
    
    # Views
    
    'data': [
     'view/stock_picking.xml',
     'view/stock_location.xml'
    ],
    'demo': [
    ],
    
    
     # Odoo Store Specific
    'images': ['static/description/cover-img.jpg'],
    'live_test_url' :'http://www.emiprotechnologies.com/free-trial?app=cancel-stock-picking-ept&version=11',
    'price': '59' ,
    'currency': 'EUR',
    
    
    'installable': True,
    'auto_install': False,
    'application': True,

}
