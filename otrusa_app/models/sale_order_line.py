# -*- coding: utf-8 -*-

###########################################
# OTRUSA_COM
# Leo
# 03-2019
###########################################

from odoo import models, fields, api

class sale_order_line(models.Model):
    _inherit= 'sale.order.line'
    x_test_app = fields.Float('x_test_app')

@api.multi
def x_set_dropship_route_id(self):
    for order in self:
        test = 6
        order.order_line.route_id = 6
