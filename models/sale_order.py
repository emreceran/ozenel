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

    # def action_generate_rfq_by_need(self):
    #     for order in self:
    #         supplier_po_map = {}
    #
    #         for line in order.order_line:
    #             if line.product_id.type != 'product':
    #                 continue  # Stoklanabilir olmayan ürünler pas geçilir
    #
    #             needed_qty = line.product_uom_qty - line.free_qty_today
    #             if needed_qty <= 0:
    #                 continue  # Stok yeterliyse RFQ'ya gerek yok
    #
    #             supplierinfo = line.product_id._select_seller(
    #                 quantity=needed_qty,
    #                 uom_id=line.product_uom,
    #                 date=fields.Date.today()
    #             )
    #
    #             partner = supplierinfo.partner_id
    #             purchase_order = supplier_po_map.get(partner.id)
    #             if not purchase_order:
    #                 purchase_order = self.env['purchase.order'].search([
    #                     ('partner_id', '=', partner.id),
    #                     ('state', '=', 'draft'),
    #                     ('company_id', '=', line.company_id.id),
    #                 ], limit=1)
    #                 if not purchase_order:
    #                     purchase_order = self.env['purchase.order'].create({
    #                         'partner_id': partner.id,
    #                         'date_order': fields.Date.today(),
    #                         'origin': order.name,
    #                         'company_id': line.company_id.id,
    #                     })
    #                 supplier_po_map[partner.id] = purchase_order
    #
    #             purchase_qty = line.product_uom._compute_quantity(needed_qty, line.product_id.uom_po_id)
    #             self.env['purchase.order.line'].create({
    #                 'order_id': purchase_order.id,
    #                 'product_id': line.product_id.id,
    #                 'product_qty': purchase_qty,
    #                 'product_uom': line.product_id.uom_po_id.id,
    #                 'price_unit': supplierinfo.price,
    #                 'date_planned': fields.Date.today(),
    #                 'name': line.name,
    #                 'sale_line_id': line.id,
    #             })
