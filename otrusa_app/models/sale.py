# -*- coding: utf-8 -*-
#231231
from odoo import models, fields, api

class saleOrder(models.Model):
    _inherit= 'sale.order'
    x_test_otrusa = fields.Float('test_otrusa')


    @api.multi
    def x_dropship_route(self):
        self.ensure_one()
        self.x_drop_ship = True
        self.warehouse_id = 19
        for order in self:
            order.order_line.update({'route_id': 6})

    @api.multi
    def x_dropship_route_counter(self):
        self.ensure_one()
        self.x_drop_ship = False
        self.warehouse_id = False
        for order in self:
            order.order_line.update({'route_id': False})
