# -*- coding: utf-8 -*-
# from odoo import http


# class StockCustomization(http.Controller):
#     @http.route('/stock_customization/stock_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_customization/stock_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_customization.listing', {
#             'root': '/stock_customization/stock_customization',
#             'objects': http.request.env['stock_customization.stock_customization'].search([]),
#         })

#     @http.route('/stock_customization/stock_customization/objects/<model("stock_customization.stock_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_customization.object', {
#             'object': obj
#         })
