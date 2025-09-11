from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    active = fields.Boolean(copy=False, default=True)

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
        string='Kaynak Para Birimi',
        help='Dönüştürmeden önceki para birimi.',
        readonly=True
    )

    target_currency_id = fields.Many2one(
        'res.currency',
        string='Hedef Para Birimi',
        help='Dönüştürmeden sonraki para birimi.'
    )

    # @api.onchange('target_currency_id')
    # def _onchange_target_currency(self):
    #     for order in self:
    #         if order.target_currency_id and order.currency_id:
    #             order.previous_currency_id = order.currency_id

    def _get_inverse_rate(self, currency_name):
        currency = self.env['res.currency'].search([('name', '=', currency_name)], limit=1)
        return round(1.0 / currency.rate, 5) if currency and currency.rate else 0.0

    # def action_recalculate_price_units(self):
    #     for order in self:
    #         new_currency = order.target_currency_id
    #         if not new_currency:
    #             continue
    #
    #         for line in order.order_line:
    #             line.currency_id = new_currency  # Satırın hedef para birimi
    #
    #         order.previous_currency_id = new_currency

    def action_recalculate_price_units(self):
        for order in self:
            usd = order.usd_rate
            eur = order.eur_rate
            target_currency = order.target_currency_id
            target_name = target_currency.name

            for line in order.order_line:

                base_cost = line.tedarikci_maliyet_para_birimli or 0.0
                source_name = line.tedarikci_currency_id.name

                if source_name == target_name or not source_name or not target_name:
                    converted = base_cost
                elif source_name == 'USD' and target_name == 'TRY':
                    converted = base_cost * usd
                elif source_name == 'TRY' and target_name == 'USD':
                    converted = base_cost / usd if usd else base_cost
                elif source_name == 'EUR' and target_name == 'TRY':
                    converted = base_cost * eur
                elif source_name == 'TRY' and target_name == 'EUR':
                    converted = base_cost / eur if eur else base_cost
                elif source_name == 'USD' and target_name == 'EUR':
                    converted = (base_cost * usd) / eur if eur else base_cost
                elif source_name == 'EUR' and target_name == 'USD':
                    converted = (base_cost * eur) / usd if usd else base_cost
                else:
                    converted = base_cost

                line.son_maliyet = round(converted, 2)
                line.price_unit = line.son_maliyet * (1 + line.margin_yeni / 100.0)

                line.currency_id = target_currency.id
