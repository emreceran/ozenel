# ozenel_modul/models/sale_order_line.py

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tedarikci_currency_id = fields.Many2one(
        'res.currency',
        string='Para Birimi',
        help='Tedarikçi fiyatı için geçerli para birimi.',
        default=lambda self: self.env.ref('base.TRY').id
    )

    tedarikci_fiyat = fields.Float(
        string='Ted. Fiyatı',
        digits='Product Price',
        help='Tedarikçi tarafından verilen fiyat (örn: kg başına fiyat).'
    )

    tedarikci_indirim_yuzdesi = fields.Float(
        string='İskonto (%)',
        digits='Discount',
        help='Tedarikçi fiyatına uygulanacak iskonto yüzdesi.'
    )

    maliyet_carpani = fields.Float(
        string='Maliyet Çarpanı (Kg)',
        digits='Product Unit of Measure',
        help='Maliyet hesaplamasında kullanılacak çarpan (örn: demir direk için kilo). Standart ürünler için bu değer 1 olmalıdır.'
    )

    tedarikci_maliyet_para_birimli = fields.Float(
        string='İndirimli Birim Maliyet',
        compute='_compute_maliyet_para_birimli',
        store=True,
        help='İskonto sonrası birim maliyet (örn: kg başına maliyet), seçilen para biriminde.'
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

    @api.onchange('product_id')
    def _onchange_product_id_set_carpani(self):
        if self.product_id:
            self.maliyet_carpani = self.product_id.product_tmpl_id.maliyet_carpani

    @api.onchange('tedarikci_maliyet_para_birimli', 'tedarikci_currency_id', 'order_id.usd_rate', 'order_id.eur_rate',
                  'maliyet_carpani')
    def _onchange_set_purchase_price(self):
        if not self.product_id:
            return

        rate = 1.0
        if self.tedarikci_currency_id.name == 'USD':
            rate = self.order_id.usd_rate or 1.0
        elif self.tedarikci_currency_id.name == 'EUR':
            rate = self.order_id.eur_rate or 1.0
        else:
            rate = 1.0

        self.purchase_price = self.tedarikci_maliyet_para_birimli * self.maliyet_carpani * rate

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('product_id') and not vals.get('maliyet_carpani'):
                product = self.env['product.product'].browse(vals['product_id'])
                if product.product_tmpl_id.maliyet_carpani:
                    vals['maliyet_carpani'] = product.product_tmpl_id.maliyet_carpani
        return super(SaleOrderLine, self).create(vals_list)