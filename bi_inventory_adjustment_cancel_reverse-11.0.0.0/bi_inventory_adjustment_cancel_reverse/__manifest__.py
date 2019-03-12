# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Inventory Adjustment Cancel/Reverse",
    'version': "11.0.0.0",
    'category': "Warehouse",
    'summary': 'This apps helps to reverse the done inventory adustment also allow to cancel it and set to draft',
    'description': """This module helps to reverse inventory adjustments, allow to cancel inventory on done stage and reset inventory on cancel stage
    -stock inventory reverse workflow, stock inventory cancel, inventory adjustment cancel, incoming shipment cancel, cancel inventory adjustment, cancel delivery order, cancel incoming shipment, cancel order, set to draft picking, cancel done picking, revese picking process, cancel done delivery order.reverse delivery order.
    stock inventory adjustment reverse workflow, stock inventory adjustment cancel
stock adjustment reverse workflow,warehouse stock cancel,stock warehouse cancel, cancel stock for inventory, cancel stock inventory, cancel inventory adjustment from done state, cancel warehouse stock adjustment, cancel order, set to draft picking, cancel done picking, revese picking process, cancel done delivery order. orden de entrega inversa.

sélection de stock reverse workflow, sélection de stock annuler, annulation de commande, annulation de livraison, annulation de commande, annulation de livraison, annulation de livraison, annulation de la commande, annulation de la sélection, annulation de la préparation, annulation du bon de livraison. ordre de livraison inverse.
    cancel stock Inventory Adjustment
    cancel and reset to draft Inventory Adjustment
    cancel reset Inventory Adjustment
    cancel Inventory Adjustment
    cancel delivery stock Adjustment
    cancel stock Adjustment
    reverse Inventory Adjustment
    reverse stock Inventory Adjustment
    cancel orders
    order cancel
    delivery cancel, picking cancel, Reverse order, reverse picking, reverse delivery, reverse shipment

    """,
    'author': "BrowseInfo",
    'website' : "www.browseinfo.in",
    'price': 19.00,
    'currency': "EUR",
    'depends': ['stock'],
    'data': [
        "security/ir.model.access.csv",
        "security/inventory_adjustment_group.xml",
        "views/inventory_adjustment_view.xml"
    ],
    'qweb': [
    ],
    'auto_install': False,
    'installable': True,
    'live_test_url':"https://youtu.be/gAuSrPqwQtk",
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
