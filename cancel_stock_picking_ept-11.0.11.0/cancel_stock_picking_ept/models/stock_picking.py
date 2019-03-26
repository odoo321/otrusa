from odoo import api, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Cancel the sale order than automatic cancel the invoice and picking
    @api.multi
    def action_cancel(self):
        unreserve_picking_ids = []
        return_ids = self.env['stock.return.picking'].search([('picking_id', 'in', self.ids)])
        if return_ids:
            for return_id in return_ids:
                return_id.picking_id.move_lines.stock_quant_update_ept()
        else:
            for stock_picking_id in self:
                if stock_picking_id.picking_type_code == 'incoming':
                    model = self.env['ir.model'].search([('model', '=', 'stock.landed.cost')])
                    if model:
                        cost_ids = self.env['stock.landed.cost'].search(
                            [('picking_ids', 'in', stock_picking_id.ids), ('state', '=', 'done')])
                        if cost_ids:
                            raise UserError(_(
                                'You can not cancel picking because this picking is set in stock landed cost first remove this picking from stock landed cost'))
                    for stock_move in stock_picking_id.move_lines:
                        qty_done = stock_move.product_uom._compute_quantity(stock_move.quantity_done,
                                                                            stock_move.product_id.uom_id)
                        if stock_move.remaining_qty < qty_done:
                            raise UserError(_('You can not cancel the reseverd products'))
                        stock_quant_ids = self.env['stock.quant'].search(
                            [('product_id', '=', stock_move.product_id.id), (
                                'reserved_quantity', '<=', stock_move.quantity_done), ('reserved_quantity', '!=', 0),
                             ('location_id', '=', stock_move.location_dest_id.id)])

                        if stock_quant_ids and not stock_picking_id.picking_type_id.default_location_dest_id.check_reserved_qty:
                            raise UserError(_('You can not cancel the reseverd products'))
                        elif stock_quant_ids and stock_picking_id.picking_type_id.default_location_dest_id.check_reserved_qty:
                            move_ids = self.env['stock.move'].search([('product_id', '=', stock_move.product_id.id), (
                                'state', 'not in', ['done', 'cancel', 'draft'])])
                            for move in move_ids:
                                if move.picking_id.picking_type_code == 'outgoing':
                                    move.picking_id.do_unreserve()
                                    unreserve_picking_ids.append(move.picking_id)
                stock_picking_id.move_lines.stock_quant_update_ept()
        res = super(StockPicking, self).action_cancel()
        for pick in unreserve_picking_ids:
            pick.action_assign()
        return res

    #Reset to draft picking after cancel the picking
    @api.multi
    def set_to_draft(self):
        for picking_obj in self:
            picking_obj.state = 'draft'
            for move in picking_obj.move_lines:
                move.state = 'draft'