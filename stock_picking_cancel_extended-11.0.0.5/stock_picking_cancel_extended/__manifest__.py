# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Stock Picking Cancel/Reverse",
    "version": "11.0.0.5",
    "author": "BrowseInfo",
    "category": "Warehouse",
    "website": "http://www.browseinfo.in",
    'summary': 'This module helps to reverse the done picking, allow to cancel picking and set to draft',
    "depends": [
        "stock","sale_stock","sale_management","purchase",
    ],
    "demo": [],
    'description': """
    -stock picking reverse workflow, stock picking cancel, delivery order cancel, incoming shipment cancel, cancel picking order, cancel delivery order, cancel incoming shipment, cancel order, set to draft picking, cancel done picking, revese picking process, cancel done delivery order.reverse delivery order.

stock picking reverse workflow, stock picking cancel, delivery order cancel, delivering cancel, cancel picking order, cancel delivery order, cancel shipment shipment, cancel order, set to draft picking, cancel done picking, revese picking process, cancel done delivery order. orden de entrega inversa.

sélection de stock reverse workflow, sélection de stock annuler, annulation de commande, annulation de livraison, annulation de commande, annulation de livraison, annulation de livraison, annulation de la commande, annulation de la sélection, annulation de la préparation, annulation du bon de livraison. ordre de livraison inverse.
    cancel stock picking
    `cancel and reset to draft picking
    cancel reset picking
    cancel picking
    cancel delivery order
    cancel incoming shipment
    reverse stock picking
    reverse delivery order
    cancel orders
    order cancel
    delivery cancel, picking cancel, Reverse order, reverse picking, reverse delivery, reverse shipment

    """,
    'price': '49',
    'currency': "EUR",
    "data": [
        "security/picking_security.xml",
        "views/stock_view.xml"
    ],
    'live_test_url':'https://www.youtube.com/watch?v=ebUnHk_eStc&feature=youtu.be',
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "images":['static/description/Banner.png'],
}
