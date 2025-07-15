# -*- coding: utf-8 -*-
# from odoo import http


# class Ozenel(http.Controller):
#     @http.route('/ozenel/ozenel', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ozenel/ozenel/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ozenel.listing', {
#             'root': '/ozenel/ozenel',
#             'objects': http.request.env['ozenel.ozenel'].search([]),
#         })

#     @http.route('/ozenel/ozenel/objects/<model("ozenel.ozenel"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ozenel.object', {
#             'object': obj
#         })

