# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ac_order_id = fields.Many2one('ac_order.ac_order', string='AC Order Reference', copy=False)

class ac_order(models.Model):
        _name = 'ac_order.ac_order'
        _description = 'Test 1 Model'

        ac_order_name = fields.Char(string='Name')
        ac_order_customer = fields.Many2one('res.partner', string='Customer')
        ac_date = fields.Date(string='Date')
        ac_order_line = fields.One2many('ac_order.ac_order_line',  'ac_order_id', string='Order Lines')
        state = fields.Selection([
                ('draft', 'Draft'),
                ('confirm', 'Confirm'),
                ('cancel', 'Cancelled'),
                ], string='AC Order Status', readonly=True, copy=False, store=True, default='draft', track_visibility='onchange')
        sale_order = fields.One2many('sale.order', 'ac_order_id', string='Sale Order Reference')
        sale_count = fields.Integer(string='Sale Count', compute='get_sale_order')

        # Comfirm button : copy to sale order
        def create_sale_order(self):
            if len(self.ac_order_line) is 0:
                raise UserError('Please Select Products')
            else:
                order_ids = self.env['sale.order']
                vals = {
                    'partner_id': self.ac_order_customer.id,
                    'ac_order_id': self.id,
                    }
                order = self.env['sale.order'].create(vals)
                if order:
                    order_ids += order
                    order.onchange_partner_id()
                    for line in self.ac_order_line:
                        vals = {
                            'order_id': order.id,
                            'product_id': line.product.id,
                            'name': line.description,
                            'product_uom': line.uom.id,
                            'product_uom_qty': line.qty,
                            'price_unit': line.unit_price,
                            }
                        self.env['sale.order.line'].create(vals)
                return order_ids

        @api.multi
        def confirm_order(self):
            self.create_sale_order()
            self.write({
                "state": "confirm"
            })
            return True

        def to_draft_order(self):
            self.write({
                "state": "draft"
            })

        @api.depends('sale_order')
        def get_sale_order(self):
            for order in self:
                order.sale_count = len(order.sale_order)

        @api.multi
        def action_view_sale(self):
            action = self.env.ref('sale.action_orders').read()[0]
            action['domain']=[('ac_order_id', '=', self.id)]
            action['context'] = {'default_partner_id':self.ac_order_customer.id,'default_ac_order_id':self.id, 'default_validity_date': self.ac_date}
            return action

class ac_order_line(models.Model):
        _name = 'ac_order.ac_order_line'
        _description = 'Test 1 Products Line Model'

        product = fields.Many2one('product.product', string='Product')
        description = fields.Text('Description')
        uom = fields.Many2one('product.uom', string='UoM')
        qty = fields.Float(string='Qty', default=1.00)
        unit_price = fields.Float(string='Unit Price', default=0.00)
        discount =  fields.Float(string='Discount %', default=0.0)
        discount_amount = fields.Float(string='Discount Amount', default=0.00)
        final_price = fields.Float(string='Final Price', default=0.00)
        ac_order_id = fields.Many2one('ac_order.ac_order', string='AC Order Reference')

        @api.onchange('unit_price', 'discount', 'qty')
        def _get_final_price(self):
            for product in self:
                if product.discount:
                    product.final_price = product.unit_price * product.qty - (product.unit_price * product.discount / 100) if product.unit_price >= (product.unit_price * product.discount / 100) else 0.00
                    product.discount_amount = product.unit_price * product.discount / 100 * product.qty
                else:
                    product.final_price = product.unit_price * product.qty

        @api.onchange('unit_price', 'discount_amount', 'qty')
        def _get_final_price_with_amount(self):
            for product in self:
                if product.discount_amount:
                    product.final_price = product.unit_price * product.qty - product.discount_amount if product.unit_price >= product.discount_amount else 0.00
                    product.discount = product.final_price * 100 / product.unit_price * product.qty
                else:
                    product.final_price = product.unit_price * product.qty

        @api.onchange('product')
        def _get_product_unit_price(self):
            for product in self:
                product.unit_price = product.product.lst_price
                product.final_price = product.unit_price * product.qty
