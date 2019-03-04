# -*- coding: utf-8 -*-

import hashlib
import xmltodict
import random
import logging
from lxml import etree
import pprint
import requests
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
_logger = logging.getLogger(__name__)


class PaymentAcquirerNuvei(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('nuvei', 'Nuvei')])
    nuvei_terminalid = fields.Char('TerminalID', required_if_provider='nuvei', groups='base.group_user')
    nuvei_secret = fields.Char('Secret', required_if_provider='nuvei', groups='base.group_user')

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(PaymentAcquirerNuvei, self)._get_feature_support()
        res['tokenize'].append('nuvei')
        # res['authorize'].append('nuvei')
        return res

    def _get_nuvei_urls(self, environment):
        if environment == 'prod':
            return {'nuvei_form_url': 'https://testpayments.globalone.me/merchant/paymentpage'}
        else:
            return {'nuvei_form_url': 'https://testpayments.globalone.me/merchant/paymentpage'}

    @api.multi
    def nuvei_get_form_action_url(self):
        self.ensure_one()
        return self._get_nuvei_urls(self.environment)['nuvei_form_url']

    @api.multi
    def nuvei_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        ORDERID = values.get("reference", False)
        CURRENCY = values['currency'] and values['currency'].name or ''
        AMOUNT = values['amount'] and values['amount'] or ''
        DATETIME_VALUE = datetime.now().strftime('%d-%m-%Y:%H:%M:%S:%f')[:-3]
        RECEIPTPAGEURL = base_url + (values.get('return_url', False) if 'invoice' in values['return_url'] else '/payment/nuvei/return')
        TERMINALID = self.nuvei_terminalid
        SECRET = self.nuvei_secret

        SECURECARDMERCHANTREF = ''.join(random.SystemRandom().choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for i in range(48))

        hash_value = str(TERMINALID) + ORDERID + CURRENCY + str(AMOUNT) + DATETIME_VALUE + RECEIPTPAGEURL + SECRET
        HASH = hashlib.md5(hash_value.encode('utf-8')).hexdigest()

        nuvei_values = dict(values,
                            ORDERID=ORDERID,
                            CURRENCY=CURRENCY,
                            AMOUNT=AMOUNT,
                            DATETIME_VALUE=DATETIME_VALUE,
                            RECEIPTPAGEURL=RECEIPTPAGEURL,
                            TERMINALID=TERMINALID,
                            HASH=HASH)
        tx = self.env['payment.transaction'].search([('reference', '=', values.get("reference", False))])
        if tx and tx.type == 'form_save':
            nuvei_values.update({'SECURECARDMERCHANTREF': SECURECARDMERCHANTREF})
        return nuvei_values


class PaymentTransactionNuvei(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _nuvei_form_get_tx_from_data(self, data):
        """ Given a data dict coming from twoctwop, verify it and find the related
        transaction record. """
        reference = data.get('ORDERID')
        if not reference:
            raise ValidationError(
                _('nuvei: received data with missing reference (%s)') % (reference))

        transaction = self.search([('reference', '=', reference)])

        if not transaction:
            error_msg = (
                _('nuvei: received data for reference %s; no order found') % (reference))
            raise ValidationError(error_msg)
        elif len(transaction) > 1:
            error_msg = (
                _('nuvei: received data for reference %s; multiple orders found') % (reference))
            raise ValidationError(error_msg)

        return transaction

    @api.multi
    def _nuvei_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if self.acquirer_reference and data.get('ORDERID') != self.acquirer_reference:
            invalid_parameters.append(('Transaction Id', data.get('ORDERID'), self.acquirer_reference))
        if float_compare(float(data.get('AMOUNT', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('Amount', data.get('AMOUNT', '0.0'), '%.2f' % self.amount))
        return invalid_parameters

    @api.multi
    def _nuvei_form_validate(self, data):
        status = data.get('RESPONSECODE')
        res = {
            'acquirer_reference': data.get('ORDERID'),
            'date_validate': fields.Datetime.now(),
            'state_message': data.get('RESPONSETEXT') + '\n\n' + str(data)
        }
        if status == 'A':
            _logger.info('Validated Nuvei payment for reference %s: set as done' % pprint.pformat(self.reference))
            res.update(state='done')
            self.write(res)
            self.x_payment_channel = 'gop_cc'
            if self.partner_id and not self.payment_token_id and (self.type == 'form_save' or self.acquirer_id.save_token == 'always'):
                token_id = self.env['payment.token'].create({
                    'name': data.get('UNIQUEREF', False),
                    'acquirer_ref': data.get('CARDREFERENCE', False),
                    'card_expiry': data.get('CARDEXPIRY', False),
                    'card_type': data.get('CARDTYPE', False),
                    'acquirer_id': self.acquirer_id.id,
                    'partner_id': self.partner_id.id,
                })
                self.payment_token_id = token_id
            if self.payment_token_id:
                self.payment_token_id.verified = True
            return True
        elif status == 'E':
            _logger.info('Received notification for Nuvei payment %s: set as pending' % (self.reference))
            res.update(state='pending')
            return self.write(res)
        elif status == 'D':
            _logger.info('Received notification for Nuvei payment %s: set as cancel' % (self.reference))
            res.update(state='cancel')
            return self.write(res)
        else:
            error = 'Received unrecognized status for Nuvei payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            res.update(state='error', state_message=error)
            return self.write(res)

    @api.multi
    def nuvei_s2s_do_transaction(self, **data):
        self.ensure_one()
        ORDERID = self.reference
        TERMINALID = self.acquirer_id.nuvei_terminalid
        AMOUNT = self.amount
        DATETIME_VALUE = datetime.now().strftime('%d-%m-%Y:%H:%M:%S:%f')[:-3]
        CURRENCY = self.currency_id.name
        SECRET = self.acquirer_id.nuvei_secret
        hash_value = str(TERMINALID) + ORDERID + CURRENCY + str(AMOUNT) + DATETIME_VALUE + SECRET
        HASH = hashlib.md5(hash_value.encode('utf-8')).hexdigest()

        payment = etree.Element('PAYMENT')
        etree.SubElement(payment, 'ORDERID').text = ORDERID
        etree.SubElement(payment, 'TERMINALID').text = TERMINALID
        etree.SubElement(payment, 'AMOUNT').text = str(AMOUNT)
        etree.SubElement(payment, 'DATETIME').text = DATETIME_VALUE
        etree.SubElement(payment, 'CARDNUMBER').text = self.payment_token_id.acquirer_ref
        etree.SubElement(payment, 'CARDTYPE').text = "SECURECARD"
        etree.SubElement(payment, 'HASH').text = HASH
        etree.SubElement(payment, 'CURRENCY').text = CURRENCY
        etree.SubElement(payment, 'TERMINALTYPE').text = "2"
        etree.SubElement(payment, 'TRANSACTIONTYPE').text = "7"

        xml = '<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(payment).decode("utf-8")

        url = 'https://testpayments.globalone.me/merchant/xmlpayment'
        headers = {'Content-Type': 'application/xml'}
        res = requests.post(url, data=xml, headers=headers).text
        return self._nuvei_s2s_validate_tree(res)

    @api.multi
    def _nuvei_s2s_validate_tree(self, tree):
        return self._nuvei_s2s_validate(tree)

    @api.multi
    def _nuvei_s2s_validate(self, tree):
        doc = xmltodict.parse(tree, dict_constructor=dict)
        data = doc.get("PAYMENTRESPONSE", doc)
        status = data.get('RESPONSECODE', False)
        res = {
            'x_payment_channel': 'gop_cc',
            'acquirer_reference': data.get('UNIQUEREF', False),
            'date_validate': fields.Datetime.now(),
            'state_message': data.get('RESPONSETEXT', False) + '\n\n' + str(data)
        }
        if status == 'A':
            _logger.info('Validated Nuvei payment for reference %s: set as done' % pprint.pformat(self.reference))
            res.update(state='done')
            self.write(res)
            return True
        elif status == 'D':
            _logger.info('Received notification for Nuvei payment %s: set as cancel' % (self.reference))
            res.update(state='cancel')
            return self.write(res)
        else:
            error = 'Received unrecognized status for Nuvei payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            res.update(state='error', state_message=error)
            return self.write(res)

    # Create invoice if sale order is confirmed for front-end payment method
    @api.model
    def form_feedback(self, data, acquirer_name):
        res = super(PaymentTransactionNuvei, self).form_feedback(data, acquirer_name)

        # fetch the tx
        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(data)
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
        return res

    # Create invoice if sale order is confirmed for s2s payment method
    def confirm_sale_token(self):
        res = super(PaymentTransactionNuvei, self).confirm_sale_token()
        if self.sale_order_id and self.sale_order_id.invoice_status == 'to invoice':
            self.sale_order_id._create_invoices()
            invoice = self.env['account.invoice'].search([('origin', '=', self.sale_order_id.name)])
            if invoice:
                invoice.action_invoice_open()
                vals = {
                    'payment_type': 'inbound',
                    'payment_method_id': self.env.ref('payment.account_payment_method_electronic_in').id,
                    'partner_type': 'customer',
                    'partner_id': self.partner_id.id,
                    'amount': self.amount,
                    'journal_id': self.acquirer_id.journal_id.id,
                    'communication': invoice.number,
                }
                account_payment_id = self.env['account.payment'].create(vals)
                account_payment_id.write({'payment_transaction_id': self.id,
                                          'payment_token_id': self.payment_token_id.id,
                                          'invoice_ids': [(4, invoice.id)]})
                account_payment_id.post()
        return res

    # Remove send email functionality
    def _confirm_so(self):
        """ Check tx state, confirm the potential SO """
        self.ensure_one()
        if self.sale_order_id.state not in ['draft', 'sent', 'sale']:
            _logger.warning('<%s> transaction STATE INCORRECT for order %s (ID %s, state %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id, self.sale_order_id.state)
            return 'pay_sale_invalid_doc_state'
        if not float_compare(self.amount, self.sale_order_id.amount_total, 2) == 0:
            _logger.warning(
                '<%s> transaction AMOUNT MISMATCH for order %s (ID %s): expected %r, got %r',
                self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id,
                self.sale_order_id.amount_total, self.amount,
            )
            self.sale_order_id.message_post(
                subject=_("Amount Mismatch (%s)") % self.acquirer_id.provider,
                body=_("The sale order was not confirmed despite response from the acquirer (%s): SO amount is %r but acquirer replied with %r.") % (
                    self.acquirer_id.provider,
                    self.sale_order_id.amount_total,
                    self.amount,
                )
            )
            return 'pay_sale_tx_amount'

        if self.state == 'authorized' and self.acquirer_id.capture_manually:
            _logger.info('<%s> transaction authorized, auto-confirming order %s (ID %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
            if self.sale_order_id.state in ('draft', 'sent'):
                self.sale_order_id.with_context(send_email=True).action_confirm()
        elif self.state == 'done':
            _logger.info('<%s> transaction completed, auto-confirming order %s (ID %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
            if self.sale_order_id.state in ('draft', 'sent'):
                self.sale_order_id.with_context().action_confirm()
        elif self.state not in ['cancel', 'error'] and self.sale_order_id.state == 'draft':
            _logger.info('<%s> transaction pending/to confirm manually, sending quote email for order %s (ID %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
            self.sale_order_id.force_quotation_send()
        else:
            _logger.warning('<%s> transaction MISMATCH for order %s (ID %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
            return 'pay_sale_tx_state'
        return True


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    provider = fields.Selection(string='Provider', related='acquirer_id.provider')
    card_expiry = fields.Char("Card Expiry")
    card_type = fields.Char("Card Type")
