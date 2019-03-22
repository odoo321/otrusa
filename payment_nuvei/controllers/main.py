# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug
from datetime import datetime, date

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

    @http.route(['/payment/nuvei/payment/validation'], type='http', auth='none', csrf=False)
    def nuvei_payment_validation(self, **post):
        _logger.info('nuvei: payment validation response %s', pprint.pformat(post))
        acquirer_id = request.env['payment.acquirer'].search([('provider', '=', 'nuvei')])

        if post.get('UNIQUEREF', False) and post.get('RESPONSECODE', False) == 'A':
            transaction = request.env['payment.transaction'].sudo().search([('reference', 'in', [post['UNIQUEREF'], post['ORDERID']])])
            if not transaction:
                res = {
                    'reference': post.get('UNIQUEREF', False),
                    'acquirer_reference': post.get('UNIQUEREF', False),
                    'acquirer_id': acquirer_id.id,
                    'amount': post.get('AMOUNT'),
                    'x_payment_channel': 'gop_cc',
                    'x_card_type': 'ach',
                    'x_order_trans_id': post.get('ORDERID', False),
                    'x_card_holder_name': '',
                    'x_card_ach_num': post.get('CARDNUMBER', False),
                    'x_exp_month': post.get('CARDEXPIRY', False) and post['CARDEXPIRY'][:2] or '',
                    'x_exp_year': post.get('CARDEXPIRY', False) and post['CARDEXPIRY'][-2:] or '',
                    'x_order_trans_date': datetime.strptime(post.get('DATETIME', False), '%Y-%m-%dT%H:%M:%S'),
                    'state': 'draft',
                    'x_note': post.get('RESPONSETEXT') + '\n\n' + str(post),
                }
                transaction_id = request.env['payment.transaction'].sudo().create(res)

                transaction_id.auto_reconciliation_id = request.env['auto.reconciliation'].sudo().create({
                    'transaction_id': transaction_id.id,
                    'partner_id': transaction_id.partner_id and transaction_id.partner_id.id,
                    'amount': transaction_id.amount})

                domain = [('amount_total', '=', transaction_id.amount)]
                if transaction_id.x_sb_wo_n:
                    domain.append(('x_qb', '=', transaction_id.x_qb))
                invoice = request.env['account.invoice'].sudo().search(domain)
                if len(invoice) == 1:
                    transaction_id.auto_reconciliation_id.write({
                        'invoice_ids': [(6, 0, [invoice.id])],
                        'state': 'invoice'
                    })

                domain = [('amount', '=', transaction_id.amount)]
                if transaction_id.x_sb_wo_n:
                    domain.append(('x_sb_wo_n', '=', transaction_id.x_sb_wo_n))
                if transaction_id.x_qb:
                    domain.append(('x_qb_inv_num', '=', transaction_id.x_qb))
                payment = request.env['account.payment'].sudo().search(domain)
                if len(payment) == 1:
                    transaction_id.auto_reconciliation_id.write({
                        'payment_id': invoice.payment_ids and invoice.payment_ids[0].id,
                        'state': 'payment'
                    })

                if len(invoice) == 1 and len(payment) == 1:
                    transaction_id.auto_reconciliation_id.state = 'matched'
                    transaction_id.auto_reconciliation_id.matched_date = date.today()

        return "OK"

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
                    return werkzeug.utils.redirect('/payment/invoice/result?invoice_id=%s' % invoice.id)
                else:
                    return werkzeug.utils.redirect('/payment/invoice/result?error=1')
            else:
                return werkzeug.utils.redirect('/payment/invoice/result?error=1')
        return werkzeug.utils.redirect('/payment/invoice/result?error=1')

    @http.route(['/payment/invoice/result'], type='http', auth='public', website=True, csrf=False)
    def payment_invoice_result(self, **post):
        invoice_id = request.params.get('invoice_id', False)
        values = {}
        if invoice_id:
            invoice = request.env['account.invoice'].browse([int(invoice_id)])
            return request.render("payment_nuvei.invoice_payment_result", {'invoice': invoice.sudo()})
        else:
            values.update({'errors': [['Something went wrong!', 'Please contact us, Payment not done successfully.']]})
            return request.render("payment_nuvei.invoice_payment_result", values)
