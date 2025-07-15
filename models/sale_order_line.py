from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tedarikci_fiyat = fields.Float(
        string='Tedarikçi Fiyatı',
        digits='Product Price',
        help="Ürünün tedarikçi satış fiyatı. Manuel olarak değiştirilebilir. Ürün seçildiğinde otomatik dolar.",
    )

    tedarikci_fiyat_indirim_yuzdesi = fields.Float(
        string='Tedarikçi İndirim Yüzdesi (%)',
        digits='Discount',
        default=0.0,
        help="Tedarikçi fiyatına uygulanacak indirim yüzdesi."
    )

    tedarikci_fiyat_indirimli_maliyet = fields.Float(
        string='İndirimli Maliyet (Satır Satın Alma Fiyatı)',
        compute='_compute_tedarikci_fiyat_indirimli_maliyet',
        store=True,
        help="Tedarikçi indirim yüzdesi uygulandıktan sonraki maliyet, satış satırının purchase_price'ı ile aynı olacak."
    )

    # product_id değiştiğinde tedarikci_fiyat'ı otomatik doldurmak için onchange metodu
    @api.onchange('product_id')
    def _onchange_product_id_set_tedarikci_fiyat(self):
        if self.product_id:
            supplier_price = 0.0
            supplier_info = self.product_id.seller_ids.filtered(lambda s: s.min_qty == 0.0)
            if not supplier_info:
                supplier_info = self.product_id.seller_ids[:1]

            if supplier_info:
                supplier_price = supplier_info[0].price

            if not supplier_price:
                supplier_price = self.product_id.standard_price

            self.tedarikci_fiyat = supplier_price

            # Bu modül sadece tedarikçi fiyatı ve indirimli maliyetle ilgilenir.
            # Margin veya price_unit'i burada sıfırlamıyoruz, ilgili modül yapmalı.
        else:
            self.tedarikci_fiyat = 0.0

    # tedarikci_fiyat_indirimli_maliyet alanının hesaplama metodu
    @api.depends('tedarikci_fiyat', 'tedarikci_fiyat_indirim_yuzdesi', 'purchase_price')
    def _compute_tedarikci_fiyat_indirimli_maliyet(self):
        for line in self:
            if line.tedarikci_fiyat is not None and line.tedarikci_fiyat > 0 and line.tedarikci_fiyat_indirim_yuzdesi is not None:
                discount_factor = (100.0 - line.tedarikci_fiyat_indirim_yuzdesi) / 100.0
                if discount_factor > 0:
                    line.tedarikci_fiyat_indirimli_maliyet = line.tedarikci_fiyat * discount_factor
                else:
                    line.tedarikci_fiyat_indirimli_maliyet = 0.0
            else:
                line.tedarikci_fiyat_indirimli_maliyet = line.purchase_price

    # tedarikci_fiyat veya tedarikci_fiyat_indirim_yuzdesi değiştiğinde satırın purchase_price'ını güncelleyen onchange
    @api.onchange('tedarikci_fiyat_indirim_yuzdesi', 'tedarikci_fiyat')
    def _onchange_tedarikci_fiyat_update_purchase_price(self):
        if self.product_id and self.tedarikci_fiyat is not None and self.tedarikci_fiyat > 0 and self.tedarikci_fiyat_indirim_yuzdesi is not None:
            new_purchase_price_for_line = self.tedarikci_fiyat * (1 - self.tedarikci_fiyat_indirim_yuzdesi / 100.0)
            if new_purchase_price_for_line < 0:
                raise UserError(
                    _("İndirim yüzdesi, satın alma fiyatını negatif yapamaz. Lütfen geçerli bir yüzde girin."))

            self.purchase_price = new_purchase_price_for_line
        elif self.product_id:
            self.purchase_price = self.product_id.standard_price
        else:
            self.purchase_price = 0.0