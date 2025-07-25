from odoo import fields, models, api
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tedarikci_currency_id = fields.Many2one(
        'res.currency',
        string='Ted. PB ',
        help='Tedarikçi fiyatı için geçerli para birimi.'
    )

    tedarikci_fiyat = fields.Float(
        string='Ted. Fiyatı',
        digits='Product Price',
        help='Tedarikçi tarafından verilen fiyat.'
    )

    tedarikci_indirim_yuzdesi = fields.Float(
        string='İskonto (%)',
        digits='Discount',
        help='Tedarikçi fiyatına uygulanacak iskonto yüzdesi.'
    )

    tedarikci_maliyet_para_birimli = fields.Float(
        string='İndirimli Maliyet',
        compute='_compute_maliyet_para_birimli',
        store=True,
        help='İskonto sonrası maliyet, seçilen para biriminde.'
    )

    purchase_price_currency_id = fields.Many2one(
        'res.currency',
        string='Teklifs PB',
        compute='_compute_purchase_price_currency',
        store=True,
        help='Satın alma fiyatının para birimi (fiyat listesinden alınır).'
    )

    @api.depends('order_id.pricelist_id.currency_id')
    def _compute_purchase_price_currency(self):
        for line in self:
            line.purchase_price_currency_id = line.order_id.pricelist_id.currency_id

    @api.depends('tedarikci_fiyat', 'tedarikci_indirim_yuzdesi')
    def _compute_maliyet_para_birimli(self):
        for line in self:
            if line.tedarikci_fiyat > 0.0:
                discounted = line.tedarikci_fiyat * (1 - line.tedarikci_indirim_yuzdesi / 100.0)
                line.tedarikci_maliyet_para_birimli = discounted
            else:
                line.tedarikci_maliyet_para_birimli = 0.0

    @api.onchange('tedarikci_maliyet_para_birimli', 'tedarikci_currency_id', 'order_id.usd_rate', 'order_id.eur_rate')
    def _onchange_set_purchase_price(self):
        rate = 1.0
        if self.tedarikci_currency_id.name == 'USD':
            rate = self.order_id.usd_rate or 1.0
        elif self.tedarikci_currency_id.name == 'EUR':
            rate = self.order_id.eur_rate or 1.0
        else:
            rate = 1.0  # TL varsayılan

        self.purchase_price = self.tedarikci_maliyet_para_birimli * rate
