from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"

    #update the quants in source and destinition location for a product
    @api.multi
    def stock_quant_update_ept(self):
        context={}
        for move in self:
            if move.state == "done" and move.product_id.type == "product":
                for line in move.move_line_ids:
                    qty = line.product_uom_id._compute_quantity(line.qty_done, line.product_id.uom_id)
                    self.env['stock.quant']._update_available_quantity(line.product_id, line.location_id, qty)
                    self.env['stock.quant']._update_available_quantity(line.product_id, line.location_dest_id, qty * -1)
            context.update(self._context)
            context.update({'from_stock_quant_update_ept':True})
            move.with_context(context)._action_cancel()
        return True

    def _action_cancel(self):
        # if any(move.state == 'done' for move in self):
        #     raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
        for move in self:
            if move.state == 'cancel':
                continue
            move._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
        self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        self.update_remaining_value(place='action_cancel')
        for move in self:
            account_move = self.env['account.move'].search([('stock_move_id', '=', move.id)])
            if account_move:
                for am in account_move:
                    am.button_cancel()
                    am.unlink()
        return True

    def _do_unreserve(self) :
        # if any(move.state in ('done', 'cancel') for move in self):
        #     raise UserError(_('Cannot unreserve a done move'))
        for move in self:
            for line in move.move_line_ids:#for unlink the stock move line
                line.state = 'draft'
            move.move_line_ids.unlink()
            if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                move.state = 'waiting'
            elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                move.state = 'waiting'
            else:
                move.state = 'confirmed'
        return True

    @api.multi
    def update_remaining_value(self,place):
        in_moves = self.env['stock.move']
        out_moves = self.env['stock.move']
        for move in self:
            if place == 'action_cancel':#or place == 'return_from_sale'
                if move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal':
                    in_moves = self.env['stock.move'].search(
                        [('product_id', '=', move.product_id.id), ('state', '=', 'done'),  # ('date', '>=', move.date),
                         ('location_id.usage', '!=', 'internal'), ('location_dest_id.usage', '=', 'internal'),
                         ('id', '!=', move.id), ('location_dest_id', '=', move.location_id.id)], order='date')

                    out_moves = self.env['stock.move'].search(
                        [('product_id', '=', move.product_id.id), ('state', '=', 'done'),  # ('date', '>=', move.date),
                         ('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '!=', 'internal'),
                         ('id', '!=', move.id), ('location_id', '=', move.location_id.id)], order='date')
                if move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal':
                    in_moves = self.env['stock.move'].search(
                        [('product_id', '=', move.product_id.id), ('state', '=', 'done'),  # ('date', '>=', move.date),
                         ('location_id.usage', '!=', 'internal'), ('location_dest_id.usage', '=', 'internal'),
                         ('id', '!=', move.id), ('location_dest_id', '=', move.location_dest_id.id)], order='date')

                    out_moves = self.env['stock.move'].search(
                        [('product_id', '=', move.product_id.id), ('state', '=', 'done'),  # ('date', '>=', move.date),
                         ('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '!=', 'internal'),
                         ('id', '!=', move.id), ('location_id', '=', move.location_dest_id.id)], order='date')

            out_qty_total = 0
            for out_move in out_moves:
                out_move_qty = out_move.product_uom._compute_quantity(out_move.product_uom_qty, move.product_id.uom_id)
                out_qty_total += out_move_qty
            remaining_qty = 0
            for record in in_moves:
                check_in_move_qty = self.env['stock.move'].search([('origin_returned_move_id', '=', record.id)])
                if check_in_move_qty:
                    # if move have return moves then return moves is been subtracted from move
                    qty = record.product_uom._compute_quantity(record.product_uom_qty, move.product_id.uom_id)
                    for move in check_in_move_qty:
                        record_qty = move.product_uom._compute_quantity(record.product_uom_qty,
                                                                        move.product_id.uom_id)
                        qty -= record_qty
                    if qty == 0:
                        continue
                    in_move_qty = record.product_uom._compute_quantity(qty, move.product_id.uom_id)
                else:
                    in_move_qty = record.product_uom._compute_quantity(record.product_uom_qty, move.product_id.uom_id)

                if in_move_qty <= out_qty_total:
                    out_qty_total = abs(out_qty_total - in_move_qty)
                    record.remaining_qty = 0
                else:
                    remaining_qty = abs(out_qty_total - in_move_qty)
                    out_qty_total = 0
                    record.remaining_qty = remaining_qty
                    record.remaining_value = remaining_qty * record.price_unit
