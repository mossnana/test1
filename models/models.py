# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ac_order(models.Model):
	_name = 'ac_order.ac_order'
	_description = 'Test 1 Model'

	ac_order_name = fields.Char(string='Name')
	ac_order_customer = fields.Char(string='Customer')
	ac_date = fields.Date(string='Date')
	ac_order_line = fields.One2many('ac_order.ac_order_line', string='Order Lines')

class ac_order_line(models.Model):
	_name = 'ac_order.ac_order_line'
	_description = 'Test 1 Products Line Model'

	product = fields.Many2one('product.product', string='Product')
	description = fields.Text('Description')
	uom = fields.Many2one('product.uom', string='UoM')
	unit_price = fields.Float(string='Unit Price', default=0.00)
	discount =  fields.Float(string='Discount %', default=0.0)
	discount_amount = fields.Float(string='Discount Amount', default=0.00)
	final_price = fields.Float(string='Final Price', default=0.00)
	ac_order_id = fields.Many2one('ac_order.ac_order', string='AC Order Reference')

	@api.onchange('unit_price', 'discount', 'discount_amount')
	def _get_final_price(self):
		for product in self:
			if product.discount:
				if product.amount:
					product.final_price = product.unit_price - (product.discount * 100 / product.unit_price) - product.discount_amount
				else:
					product.final_price = product.unit_price - (product.discount * 100 / product.unit_price)
			elif product.discount_amount:
				if product.amount:
					product.final_price = product.unit_price - (product.discount * 100 / product.unit_price) - product.discount_amount
				else:
					product.final_price = product.unit_price - product.discount_amount
	