from odoo import models, fields, api, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    check_reserved_qty = fields.Boolean('Do Not Check Reserved Quantity When Cancel Purchase Order', default=False)
