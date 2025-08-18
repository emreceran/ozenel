# ozenel_modul/models/product_template.py

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Ürün kartına maliyet çarpanı alanını ekliyoruz.
    # Buraya girilen değer, ürün satış siparişine eklendiğinde varsayılan olarak gelecektir.
    maliyet_carpani = fields.Float(
        string='Maliyet Çarpanı (Kg)',
        default=1.0,
        help="Bu ürün için varsayılan maliyet çarpanı. Örn: Demir direk için kilosu. Satış siparişinde bu değer değiştirilebilir."
    )