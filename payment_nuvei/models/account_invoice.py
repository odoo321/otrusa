# -*- coding: utf-8 -*-

import random

from odoo import api, fields, models, http

CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_default_password(self):
        return ''.join(random.SystemRandom().choice(CHARS) for i in range(16))

    unique_invoice_number = fields.Char("Unique Invoice Number", default=_get_default_password, copy=False, readonly=True)
    payment_link = fields.Char("Payment Link", compute="_compute_payment_link", copy=False)

    @api.multi
    @api.depends("unique_invoice_number")
    def _compute_payment_link(self):
        for record in self:
            if record.unique_invoice_number:
                base_url = http.request.httprequest.host_url
                if 'https://' not in base_url:
                    base_url = base_url.replace("http://", "https://")
                record.payment_link = base_url + "payment/nuvei/invoice/" + record.unique_invoice_number
