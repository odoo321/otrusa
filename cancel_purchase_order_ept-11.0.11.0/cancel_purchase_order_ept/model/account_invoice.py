from odoo import api, models, _

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    #  unreconcile the account_move_line.
    # cancel and unlink the account move. then cancel the invoice.
    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        for inv in self:
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_move_line_ids:
                inv.payment_move_line_ids.remove_move_reconcile() # unreconcile the account_move_line
            if inv.move_name:
                inv.move_name = False
        return super(account_invoice,self).action_cancel()