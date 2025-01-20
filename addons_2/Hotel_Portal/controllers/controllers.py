# -*- coding: utf-8 -*-
# from odoo import http


# class HotelPortal(http.Controller):
#     @http.route('/hotel__portal/hotel__portal', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hotel__portal/hotel__portal/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hotel__portal.listing', {
#             'root': '/hotel__portal/hotel__portal',
#             'objects': http.request.env['hotel__portal.hotel__portal'].search([]),
#         })

#     @http.route('/hotel__portal/hotel__portal/objects/<model("hotel__portal.hotel__portal"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hotel__portal.object', {
#             'object': obj
#         })

