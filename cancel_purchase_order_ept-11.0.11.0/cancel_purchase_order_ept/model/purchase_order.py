from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # when cancel the po check if invoice available if yes then cancel the invoice.also check related picking..cancel the picking.
    @api.multi
    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state in ('open', 'draft', 'paid'):
                    inv.action_cancel()#action_invoice_cancel()
            for pick in order.picking_ids.filtered(lambda r: r.state != 'cancel'):
                pick.with_context({'from_picking': True}).action_cancel()
            order.write({'state': 'cancel'})
        return super(PurchaseOrder, self).button_cancel()

    # set to purchase order in draft state and cancel the related invoice and picking.
    @api.multi
    def button_draft(self):
        self.button_cancel()
        return super(PurchaseOrder, self).button_draft()