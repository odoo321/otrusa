# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class my_module(models.Model):
#     _name = 'my_module.my_module'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100





class sale_order(models.Model):
    _inherit= 'sale.order'

    x_test_otrusa = fields.Float('test_otrusa')

@api.multi
def x_set_dropship_route_id(self):
    for order in self:
        test = 6
        order.order_line.route_id = 6
