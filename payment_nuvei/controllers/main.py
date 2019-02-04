# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TwoctwopController(http.Controller):

    @http.route(['/payment/nuvei/return'], type='http', auth='public', csrf=False)
    def twoctwop_return(self, **post):
        _logger.info('nuvei: entering form_feedback with post data %s', pprint.pformat(post))
        return_url = '/shop/payment/validate'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'nuvei')
            return_url = '/shop/payment/validate'
        return werkzeug.utils.redirect(return_url)
