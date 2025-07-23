from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    usd_rate = fields.Float(
        string='USD Kuru (1 USD = ? TL)',
        digits=(16, 5),
        default=lambda self: self._get_inverse_rate('USD'),
        help='1 USD kaç TL eder. Sistemden otomatik gelir, manuel değiştirilebilir.'
    )

    eur_rate = fields.Float(
        string='EUR Kuru (1 EUR = ? TL)',
        digits=(16, 5),
        default=lambda self: self._get_inverse_rate('EUR'),
        help='1 EUR kaç TL eder. Sistemden otomatik gelir, manuel değiştirilebilir.'
    )

    def _get_inverse_rate(self, currency_name):
        currency = self.env['res.currency'].search([('name', '=', currency_name)], limit=1)
        return round(1.0 / currency.rate, 5) if currency and currency.rate else 0.0
