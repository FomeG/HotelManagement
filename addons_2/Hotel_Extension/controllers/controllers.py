# -*- coding: utf-8 -*-
# from odoo import http


# class Ss5(http.Controller):
#     @http.route('/ss5/ss5', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ss5/ss5/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ss5.listing', {
#             'root': '/ss5/ss5',
#             'objects': http.request.env['ss5.ss5'].search([]),
#         })

#     @http.route('/ss5/ss5/objects/<model("ss5.ss5"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ss5.object', {
#             'object': obj
#         })

