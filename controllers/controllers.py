# -*- coding: utf-8 -*-
from odoo import http

# class AcOrder(http.Controller):
#     @http.route('/ac_order/ac_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ac_order/ac_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ac_order.listing', {
#             'root': '/ac_order/ac_order',
#             'objects': http.request.env['ac_order.ac_order'].search([]),
#         })

#     @http.route('/ac_order/ac_order/objects/<model("ac_order.ac_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ac_order.object', {
#             'object': obj
#         })