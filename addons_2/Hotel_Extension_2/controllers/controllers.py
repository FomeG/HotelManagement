# -*- coding: utf-8 -*-
# from odoo import http


# class HotelExtension2(http.Controller):
#     @http.route('/hotel__extension_2/hotel__extension_2', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hotel__extension_2/hotel__extension_2/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hotel__extension_2.listing', {
#             'root': '/hotel__extension_2/hotel__extension_2',
#             'objects': http.request.env['hotel__extension_2.hotel__extension_2'].search([]),
#         })

#     @http.route('/hotel__extension_2/hotel__extension_2/objects/<model("hotel__extension_2.hotel__extension_2"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hotel__extension_2.object', {
#             'object': obj
#         })

