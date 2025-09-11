# ozenel_modul/models/product_product.py

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    tedarikci_maliyet = fields.Float(
        string='Tedarikçi Maliyeti (En Pahalı)',
        digits='Product Price',
        compute='_compute_tedarikci_maliyet',
        store=True,
        help='Bu varyant için en pahalı tedarikçi fiyatı.'
    )

    tedarikci_para_birimi = fields.Many2one(
        'res.currency',
        string='Tedarikçi Para Birimi',
        compute='_compute_tedarikci_maliyet',
        store=True,
        help='Bu varyant için en pahalı tedarikçi fiyatının para birimi.'
    )

    @api.depends('seller_ids.price', 'seller_ids.currency_id')
    def _compute_tedarikci_maliyet(self):
        for product in self:
            max_price = 0.0
            currency = False

            for seller in product.seller_ids:
                if seller.price > max_price:
                    max_price = seller.price
                    currency = seller.currency_id

            product.tedarikci_maliyet = max_price
            product.tedarikci_para_birimi = currency
