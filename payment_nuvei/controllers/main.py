# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class NuveiController(http.Controller):

    @http.route(['/payment/nuvei/return'], type='http', auth='public', csrf=False)
    def nuvei_return(self, **post):
        _logger.info('nuvei: entering form_feedback with post data %s', pprint.pformat(post))
        return_url = '/shop/payment/validate'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'nuvei')
            return_url = '/shop/payment/validate'
        return werkzeug.utils.redirect(return_url)

    # Invoice transaction flow
    # Search for invoice with invoice unique id
    @http.route(['/payment/nuvei/invoice/<string:unique_invoice_number>'], type='http', auth='public', website=True, csrf=False)
    def nuvei_payment_invoice(self, unique_invoice_number, **post):
        invoice = request.env['account.invoice'].sudo().search([('unique_invoice_number', '=', unique_invoice_number)])
        values = {}
        if invoice:
            values.update({'invoice': invoice.sudo(), 'invoice_status': invoice.state})
        else:
            values.update({'errors': [['Invoice Not Found!', 'Please contact us, Invoice not found of your link to pay.']]})
        return request.render("payment_nuvei.invoice_payment", values)

    # Router for create transaction when user click pay button, It called from custom js and return rendered form with value
    @http.route('/invoice/payment/transaction/', type='json', auth="public", website=True)
    def payment_transaction(self, invoice_id=False, **kwargs):
        invoice = request.env['account.invoice'].browse(int(invoice_id)).sudo()
        acquirer = request.env['payment.acquirer'].search([('provider', '=', 'nuvei')])
        reference = request.env['payment.transaction'].get_next_reference(invoice.number)
        tx_values = {
            'acquirer_id': acquirer.id,
            'type': 'form',
            'amount': invoice.amount_total,
            'currency_id': invoice.currency_id.id,
            'partner_id': invoice.partner_id.id,
            'partner_country_id': invoice.partner_id.country_id.id,
            'reference': reference,
        }
        tx = request.env['payment.transaction'].sudo().create(tx_values)

        values = {
            'return_url': '/payment/invoice/nuvei/return',
            'partner_id': invoice.sudo().partner_id.id,
            'billing_partner_id': invoice.sudo().partner_id.id,
        }
        return tx.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt='Pay Now').sudo().render(
            reference,
            invoice.amount_total,
            invoice.currency_id.id,
            values=values)

    @http.route(['/payment/invoice/nuvei/return'], type='http', auth='public', csrf=False)
    def invoice_nuvei_return(self, **post):
        _logger.info('nuvei: entering form_feedback with post data %s', pprint.pformat(post))
        if post:
            tx = request.env['payment.transaction'].sudo()._nuvei_form_get_tx_from_data(post)
            if tx:
                tx._nuvei_form_validate(post)
                if tx.state == 'done':
                    invoice = request.env['account.invoice'].sudo().search([('number', '=', tx.reference.split('x')[0])])
                    invoice.action_invoice_open()
                    vals = {
                        'payment_type': 'inbound',
                        'payment_method_id': request.env.ref('payment.account_payment_method_electronic_in').id,
                        'partner_type': 'customer',
                        'partner_id': tx.partner_id.id,
                        'amount': tx.amount,
                        'journal_id': tx.acquirer_id.journal_id.id,
                        'communication': invoice.number,
                    }
                    account_payment_id = request.env['account.payment'].sudo().create(vals)
                    account_payment_id.write({'payment_transaction_id': tx.id, 'invoice_ids': [(4, invoice.id)]})
                    account_payment_id.post()
                    print("\n\n\n ____________ account_payment ______________", account_payment_id.state)
                    return werkzeug.utils.redirect('/payment/invoice/result?invoice_id=%s' % invoice.id)
                else:
                    return werkzeug.utils.redirect('/payment/invoice/result?error=1')
            else:
                return werkzeug.utils.redirect('/payment/invoice/result?error=1')
        return werkzeug.utils.redirect('/payment/invoice/result?error=1')

    @http.route(['/payment/invoice/result'], type='http', auth='public', website=True, csrf=False)
    def payment_invoice_result(self, **post):
        print("\n\n\n ------------- inveoice result post --------------", post)
        invoice_id = request.params.get('invoice_id', False)
        values = {}
        if invoice_id:
            invoice = request.env['account.invoice'].browse([int(invoice_id)])
            return request.render("payment_nuvei.invoice_payment_result", {'invoice': invoice.sudo()})
        else:
            values.update({'errors': [['Something went wrong!', 'Please contact us, Payment not done successfully.']]})
            return request.render("payment_nuvei.invoice_payment_result", values)
