odoo.define("payment_nuvei.custom_payment_form", function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var website = require('website.website');
    var _t = core._t;


    $(document).ready(function() {

        $('button#o_custom_payment_form_pay').on('click', function(ev) {
            var invoice_id = $('input#custom_invoice_id').val()

            ajax.jsonRpc('/invoice/payment/transaction/', 'call', {
                'invoice_id': parseInt(invoice_id),
            }).then(function(result) {
                if (result) {
                    // if the server sent us the html form, we create a form element
                    var newForm = document.createElement('form');
                    newForm.setAttribute("method", "post"); // set it to post
                    newForm.setAttribute("provider", 11);
                    newForm.hidden = true; // hide it
                    newForm.innerHTML = result; // put the html sent by the server inside the form
                    var action_url = $(newForm).find('input[name="data_set"]').data('actionUrl');
                    newForm.setAttribute("action", action_url); // set the action url
                    $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                    $(newForm).find('input[data-remove-me]').remove(); // remove all the input that should be removed
                    if (action_url) {
                        newForm.submit(); // and finally submit the form
                    }
                } else {
                    self.displayError(
                        _t('Server Error'),
                        _t("We are not able to redirect you to the payment form.")
                    );
                }
            }).fail(function(message, data) {
                self.displayError(
                    _t('Server Error'),
                    _t("We are not able to redirect you to the payment form. ") +
                    message.data.message
                );
            });

        });
    });
});