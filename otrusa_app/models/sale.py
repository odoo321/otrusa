# -*- coding: utf-8 -*-

from odoo import models, fields, api

class saleOrder(models.Model):
    _inherit= 'sale.order'
    x_test_otrusa = fields.Float('test_otrusa')

    @api.multi
    def test01(self):
        for order in self:
            order.order_line.update({'x_description': order.x_internal_note})
