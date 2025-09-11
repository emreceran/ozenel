{
    'name': 'Ozenel Satış Siparişi Geliştirmeleri',
    'summary': 'Satış siparişi satırına tedarikçi fiyatı alanı ekler ve satır satın alma fiyatını günceller.',
    'description': """
        Bu modül, satış siparişi satırlarına tedarikçi fiyatı ve indirim yüzdesi alanları ekler.
        Girilen indirim yüzdesine göre satış satırının purchase_price (maliyet) alanı otomatik olarak güncellenir.
        Margin alanının düzenlenebilirliği için 'ozenel_sale_margin_editable' modülüne bakın.
    """,
    'author': 'Your Name/Company Name',
    'website': 'http://www.yourwebsite.com',
    'category': 'Sales',
    'version': '1.0',
    'depends': ['sale_management', 'product', 'sale_margin', 'margin_editable'], # sale_margin hala gerekli
    'data': [
        'views/sale_order_views.xml',
        'views/product_product_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}