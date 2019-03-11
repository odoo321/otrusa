from odoo import api, fields, models, _

class sale_order(models.Model):
    _inherit = "sale.order"

    # cancel the sale order than automatic cancel the invoice and picking
    @api.multi
    def action_cancel(self):
        stock_picking_ids = self.env['stock.picking'].search([('sale_id', '=', self.id),('state','!=','cancel')])
        if stock_picking_ids:
            return_ids = self.env['stock.return.picking'].search([('picking_id', '=', stock_picking_ids.ids)])
            if return_ids:
                for return_id in return_ids:
                    return_id.picking_id.move_lines.stock_quant_update_ept()
            else:
                for stock_picking_id in stock_picking_ids:
                    stock_picking_id.move_lines.stock_quant_update_ept()

        if self.invoice_ids:
            for invoice_id in self.invoice_ids:
                if invoice_id.state == 'paid':
                    invoice_id.move_id.line_ids.remove_move_reconcile()
                    invoice_id.action_cancel()
                else:
                    invoice_id.action_cancel()
        return super(sale_order, self).action_cancel()

    # if set to quotation than cancel the automatic picking  and invoices
    @api.multi
    def action_draft(self):
        self.action_cancel()
        return super(sale_order, self).action_draft()