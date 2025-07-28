from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    usd_rate = fields.Float(
        string='USD Kuru',
        digits=(16, 5),
        default=lambda self: self._get_inverse_rate('USD'),
        help='1 USD kaç TL eder. Sistemden otomatik gelir, manuel değiştirilebilir.'
    )

    eur_rate = fields.Float(
        string='EUR Kuru',
        digits=(16, 5),
        default=lambda self: self._get_inverse_rate('EUR'),
        help='1 EUR kaç TL eder. Sistemden otomatik gelir, manuel değiştirilebilir.'
    )

    previous_currency_id = fields.Many2one(
        'res.currency',
        string='Önceki Para Birimi',
        help='Fiyat listesinden önceki para birimi.'
    )

    def _get_inverse_rate(self, currency_name):
        currency = self.env['res.currency'].search([('name', '=', currency_name)], limit=1)
        return round(1.0 / currency.rate, 5) if currency and currency.rate else 0.0

    def action_recalculate_price_units(self):
        for order in self:
            if not order.previous_currency_id:
                order.previous_currency_id = order.currency_id

            old_currency = order.previous_currency_id
            new_currency = order.pricelist_id.currency_id

            usd = order.usd_rate or 1.0
            eur = order.eur_rate or 1.0

            for line in order.order_line:
                price = line.price_unit

                if old_currency.name == 'USD' and new_currency.name == 'TRY':
                    converted = price * usd
                elif old_currency.name == 'TRY' and new_currency.name == 'USD':
                    converted = price / usd if usd else price
                elif old_currency.name == 'EUR' and new_currency.name == 'TRY':
                    converted = price * eur
                elif old_currency.name == 'TRY' and new_currency.name == 'EUR':
                    converted = price / eur if eur else price
                elif old_currency.name == 'USD' and new_currency.name == 'EUR':
                    converted = (price * usd) / eur
                elif old_currency.name == 'EUR' and new_currency.name == 'USD':
                    converted = (price * eur) / usd
                else:
                    converted = price

                line.price_unit = round(converted, 2)

            # Yeni para birimini kaydediyoruz
            order.previous_currency_id = new_currency
