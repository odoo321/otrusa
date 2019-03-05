# -*- coding: utf-8 -*-
#231231
from odoo import models, fields, api

class saleOrder(models.Model):
    _inherit= 'sale.order'
    x_test_otrusa = fields.Float('test_otrusa')


    @api.multi
    def x_dropship_route(self):
        for order in self:
            order.order_line.update({'x_description': order.x_internal_note})
