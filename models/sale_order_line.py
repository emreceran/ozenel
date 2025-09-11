# ozenel_modul/models/sale_order_line.py

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tedarikci_currency_id = fields.Many2one(
        'res.currency',
        string='Para Birimi',
        help='Tedarikçi fiyatı için geçerli para birimi.',
        copy=True,
        default=lambda self: self.env.ref('base.TRY').id
    )

    tedarikci_fiyat = fields.Float(
        string='Ted. Fiyatı',
        digits='Product Price',
        copy=True,
        help='Tedarikçi tarafından verilen fiyat (örn: kg başına fiyat).'
    )

    @api.onchange('product_id')
    def _onchange_product_id_set_tedarikci_bilgileri(self):
        for line in self:
            product = line.product_id
            if product:
                line.tedarikci_fiyat = product.tedarikci_maliyet
                line.tedarikci_currency_id = product.tedarikci_para_birimi

    tedarikci_indirim_yuzdesi = fields.Float(
        string='İskonto (%)',
        digits='Discount',
        copy=True,
        help='Tedarikçi fiyatına uygulanacak iskonto yüzdesi.'
    )

    maliyet_carpani = fields.Float(
        string='Maliyet Çarpanı (Kg)',
        digits='Product Unit of Measure',
        copy=True,
        help='Maliyet hesaplamasında kullanılacak çarpan (örn: demir direk için kilo). Standart ürünler için bu değer 1 olmalıdır.'
    )

    tedarikci_maliyet_para_birimli = fields.Float(
        string='İndirimli Birim Maliyet',
        compute='_compute_maliyet_para_birimli',
        store=False,
        help='İskonto sonrası birim maliyet (örn: kg başına maliyet), seçilen para biriminde.'
    )

    @api.depends('tedarikci_fiyat', 'tedarikci_indirim_yuzdesi', 'maliyet_carpani')
    def _compute_maliyet_para_birimli(self):
        for line in self:
            if line.tedarikci_fiyat > 0.0:
                discounted = line.tedarikci_fiyat * (1 - line.tedarikci_indirim_yuzdesi / 100.0)
                line.tedarikci_maliyet_para_birimli = discounted * line.maliyet_carpani
            else:
                line.tedarikci_maliyet_para_birimli = 0.0

    son_maliyet = fields.Float(
        string='Son Maliyet',
        digits='Product Price',
        copy=True,
        help='İndirimli ve dönüştürülmüş nihai maliyet. Şimdilik manuel olarak girilir.'
    )




    @api.onchange('product_id')
    def _onchange_product_id_set_carpani(self):
        if self.product_id:
            self.maliyet_carpani = self.product_id.product_tmpl_id.maliyet_carpani

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('product_id') and not vals.get('maliyet_carpani'):
                product = self.env['product.product'].browse(vals['product_id'])
                if product.product_tmpl_id.maliyet_carpani:
                    vals['maliyet_carpani'] = product.product_tmpl_id.maliyet_carpani
        return super(SaleOrderLine, self).create(vals_list)