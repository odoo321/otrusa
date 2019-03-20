# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AutoReconciliation(models.Model):
    _name = 'auto.reconciliation'
    _rec_name = 'transaction_id'

    @api.model
    def _default_matching_payment(self):
        payment_id = self.env['account.payment'].search([('amount', '=', self.env.context.get('amount', False))])
        if payment_id and len(payment_id) == 1:
            return payment_id.id

    @api.model
    def _default_matching_invoice(self):
        invoice_id = self.env['account.invoice'].search([('amount_total', '=', self.env.context.get('amount', False))], limit=1)
        if invoice_id and len(invoice_id) == 1:
            return [(4, invoice_id.id)]

    transaction_id = fields.Many2one('payment.transaction', "Payment Transaction", required=True, states={'done': [('readonly', True)]})
    reference = fields.Char("Reference", related="transaction_id.reference", store=True, readonly=True)
    x_sb_wo_n = fields.Char("SB Work Order #", related="transaction_id.x_sb_wo_n", store=True, readonly=True)
    x_qb = fields.Char("QB #", related="transaction_id.x_qb", store=True, readonly=True)
    partner_id = fields.Many2one("res.partner", string="Customer", related="transaction_id.partner_id", store=True, readonly=True)
    amount = fields.Float("Amount", related="transaction_id.amount", store=True, readonly=True)
    total_amount = fields.Float("Total Amount", compute="_compute_total_amount")
    payment_id = fields.Many2one("account.payment", "Customer Payment", default=_default_matching_payment, states={'done': [('readonly', True)]})
    invoice_ids = fields.Many2many("account.invoice", string="Customer Invoices", default=_default_matching_invoice, states={'done': [('readonly', True)]})
    matched_date = fields.Date("Matched Date", states={'done': [('readonly', True)]})
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([('draft', 'Draft'), ('invoice', 'Invoice'), ('payment', 'Payment'),
                              ('matched', 'Matched'), ('done', 'Done')], string="Status", default="draft")

    @api.multi
    @api.depends("invoice_ids")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum([x.amount_total for x in record.invoice_ids])

    @api.multi
    def action_validate(self):
        for record in self:
            if not (record.total_amount == record.payment_id.amount == record.transaction_id.amount):
                raise ValidationError(_("Amount doesn't match with transaction and customer payment"))

            record.state = 'done'
            record.transaction_id.x_sale_order_invoice = record.invoice_ids.ids
            record.transaction_id.x_sale_order_invoice_payment = [(6, 0, [record.payment_id.id])]
