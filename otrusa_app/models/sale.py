# -*- coding: utf-8 -*-

from odoo import models, fields, api

class saleOrder(models.Model):
    _inherit= 'sale.order'
    x_test_otrusa = fields.Float('test_otrusa')

    @api.multi
    def test01(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
