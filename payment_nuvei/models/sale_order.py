# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _create_invoices(self):
        payment = self.env['sale.advance.payment.inv'].create({'advance_payment_method': 'all'})
        payment.with_context(active_ids=self.ids).create_invoices()
