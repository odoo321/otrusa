# -*- coding: utf-8 -*-

import pprint
import hashlib
import xmltodict
import logging
import requests
from lxml import etree
from datetime import datetime
from odoo import models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AuthorizeAndCaptureWizard(models.TransientModel):
    _name = 'authorize.and.capture.wizard'

    order_id = fields.Many2one('sale.order', 'Order')
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id',)
    amount = fields.Monetary("Amount", related='order_id.amount_total')
    partner_id = fields.Many2one('res.partner', "Customer")
    card_number = fields.Char("Card Number", required=True, size=16)
    expiry_month = fields.Selection(
        [('01', '01-Jan'), ('02', '02-Feb'), ('03', '03-Mar'), ('04', '04-Apr'), ('05', '05-May'), ('06', '06-Jun'),
         ('07', '07-Jul'), ('08', '08-Aug'), ('09', '09-Sep'), ('10', '10-Oct'), ('11', '11-Nov'), ('12', '12-Dec')], string='Expiry Month', required=True)
    expiry_year = fields.Selection(
        [('19', '2019'), ('20', '2020'), ('21', '2021'), ('22', '2022'), ('23', '2023'), ('24', '2024'), ('25', '2025'),
         ('26', '2026'), ('27', '2027'), ('28', '2028'), ('29', '2029'), ('30', '2030'), ('31', '2031'), ('32', '2032'),
         ('33', '2033'), ('34', '2034'), ('35', '2035'), ('36', '2036'), ('37', '2037'), ('38', '2038'), ('39', '2039'),
         ('40', '2040')],
        string='Expiry Year', required=True)

    def authorize_and_capture(self):
        if self.amount <= 0.0:
            raise ValidationError(_("Payment amount is not proper."))
        elif len(self.card_number) < 16:
            raise ValidationError(_("Card Number is not with proper length(16)."))
        elif not self.card_number.isdigit():
            raise ValidationError(_("Card number is not in digit, Please enter proper card details."))

        acquirer_id = self.env['payment.acquirer'].search([('provider', '=', 'nuvei')])

        if acquirer_id:
            ORDERID = self.order_id.name
            TERMINALID = acquirer_id.nuvei_terminalid
            AMOUNT = self.order_id.amount_total
            DATETIME_VALUE = datetime.now().strftime('%d-%m-%Y:%H:%M:%S:%f')[:-3]
            CARDNUMBER = self.card_number
            CARDTYPE = "VISA"
            CARDEXPIRY = self.expiry_month + self.expiry_year
            CARDHOLDERNAME = self.partner_id.name
            CURRENCY = self.order_id.currency_id.name
            SECRET = acquirer_id.nuvei_secret

            hash_value = str(TERMINALID) + ORDERID + CURRENCY + str(AMOUNT) + DATETIME_VALUE + SECRET
            HASH = hashlib.md5(hash_value.encode('utf-8')).hexdigest()
            payment = etree.Element('PAYMENT')
            etree.SubElement(payment, 'ORDERID').text = ORDERID
            etree.SubElement(payment, 'TERMINALID').text = TERMINALID
            etree.SubElement(payment, 'AMOUNT').text = str(AMOUNT)
            etree.SubElement(payment, 'DATETIME').text = DATETIME_VALUE
            etree.SubElement(payment, 'CARDNUMBER').text = CARDNUMBER
            etree.SubElement(payment, 'CARDTYPE').text = CARDTYPE
            etree.SubElement(payment, 'CARDEXPIRY').text = CARDEXPIRY
            etree.SubElement(payment, 'CARDHOLDERNAME').text = CARDHOLDERNAME
            etree.SubElement(payment, 'HASH').text = HASH
            etree.SubElement(payment, 'CURRENCY').text = CURRENCY
            etree.SubElement(payment, 'TERMINALTYPE').text = "1"
            etree.SubElement(payment, 'TRANSACTIONTYPE').text = "7"

            xml = '<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(payment).decode("utf-8")

            url = 'https://testpayments.globalone.me/merchant/xmlpayment'
            headers = {'Content-Type': 'application/xml'}
            response = requests.post(url, data=xml, headers=headers).text
            _logger.info('nuvei: Authorize & Capture wizard response %s', pprint.pformat(response))

            tx = self.env['payment.transaction'].create({'reference': self.order_id.name,
                                                         'acquirer_id': acquirer_id.id,
                                                         'sale_order_id': self.order_id.id,
                                                         'amount': self.order_id.amount_total,
                                                         'currency_id': self.order_id.currency_id.id,
                                                         'partner_id': self.partner_id.id})

            doc = xmltodict.parse(response, dict_constructor=dict)
            data = doc.get("PAYMENTRESPONSE", doc)
            status = data.get('RESPONSECODE', False)
            res = {
                'acquirer_reference': data.get('UNIQUEREF', False),
                'x_order_trans_id': data.get('ORDERID'),
                'date_validate': fields.Datetime.now(),
                'x_note': data.get('RESPONSETEXT', '') + '\n\n' + str(response)
            }
            if status == 'A':
                _logger.info('Validated Nuvei payment for reference %s: set as done' % pprint.pformat(tx.reference))
                res.update(state='done')
                tx.write(res)
                tx.x_payment_channel = 'gop_cc'
                tx._confirm_so()
                if tx and tx.sale_order_id.invoice_status == 'to invoice':
                    tx.sale_order_id._create_invoices()
                    invoice = self.env['account.invoice'].search([('origin', '=', tx.sale_order_id.name)])
                    if invoice:
                        invoice.action_invoice_open()
                        vals = {
                            'payment_type': 'inbound',
                            'payment_method_id': self.env.ref('payment.account_payment_method_electronic_in').id,
                            'partner_type': 'customer',
                            'partner_id': tx.partner_id.id,
                            'amount': tx.amount,
                            'journal_id': tx.acquirer_id.journal_id.id,
                            'communication': invoice.number,
                        }
                        account_payment_id = self.env['account.payment'].create(vals)
                        account_payment_id.write({'payment_transaction_id': tx.id, 'invoice_ids': [(4, invoice.id)]})
                        account_payment_id.post()
                return True
            elif status == 'D':
                _logger.info('Received notification for Nuvei payment %s: set as cancel' % (tx.reference))
                res.update(state='cancel')
                tx.write(res)
                raise ValidationError(_('Received notification for Nuvei payment %s: set as cancel' % (tx.reference, response)))
            else:
                if doc.get('ERROR', False):
                    response = doc['ERROR']['ERRORSTRING']
                error = 'Received unrecognized status/error for Nuvei payment %s: "%s", set as error' % (tx.reference, response)
                _logger.info(error)
                res.update(state='error', state_message=error)
                tx.write(res)
                raise ValidationError(_(error))
        else:
            raise ValidationError(_("No payment acquire found for nuvei"))
