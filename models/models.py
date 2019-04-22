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
        ac_coupon = fields.Many2many('wizard_ac_order', string='Coupon Ref')
        total_price = fields.Float(string="Total Order Price", compute="get_total_price")

        @api.depends('ac_order_line','ac_coupon')
        def get_total_price(self):
            for order in self:
                total_coupon = 0.00
                total_price = 0.00
                for line in order.ac_order_line:
                    total_price += line.final_price
                for coupon in order.ac_coupon:
                    total_coupon += coupon.coupon_sale
                order.total_price = total_price - total_coupon

        # Copy AC Order to Sale Order
        def create_sale_order(self):
            # Check : Product Line
            if len(self.ac_order_line) is 0:
                raise UserError('Please Select Products')
            else:
                # Call to Sale Order Model
                order_ids = self.env['sale.order']
                # College Data to transfer
                # Partner ID & AC Order Ref ID
                vals = {
                    'partner_id': self.ac_order_customer.id,
                    'ac_order_id': self.id,
                    }
                # Call Create Function in Sale Order Model with Values
                order = self.env['sale.order'].create(vals)
                # Create Order Line by loop data
                if order:
                    order_ids += order
                    # Call Sale Order Function
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

        @api.multi
        def to_cancel_order(self):
            for order in self:
                if order.sale_count is not 0:
                    raise UserError('This Order is related with Sale Order')
            self.write({
                "state": "cancel"
            })

        @api.multi
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

        @api.multi
        def unlink(self):
            for order in self:
                if order.state not in ('draft', 'cancel'):
                    raise UserError('Order is Confirmed')
            return super(ac_order, self).unlink()

class ac_order_line(models.Model):
        _name = 'ac_order.ac_order_line'
        _description = 'Test 1 Products Line Model'

        product = fields.Many2one('product.product', string='Product')
        description = fields.Text('Description')
        uom = fields.Many2one('product.uom', string='UoM')
        qty = fields.Float(string='Qty', default=1.00)
        unit_price = fields.Float(string='Unit Price', default=0.00)
        discount =  fields.Float(string='Discount %', default=0.0)
        discount_amount = fields.Float(string='Discount Amount', default=0.00, readonly=True)
        final_price = fields.Float(string='Final Price', default=0.00)
        ac_order_id = fields.Many2one('ac_order.ac_order', string='AC Order Reference')

        @api.onchange('unit_price', 'discount', 'qty')
        def _get_final_price(self):
            for product in self:
                if product.discount:
                    product.discount_amount = (product.unit_price * product.qty) * product.discount / 100
                    if product.discount_amount >= (product.unit_price * product.qty):
                        product.final_price = 0
                    else:
                        product.final_price = (product.unit_price * product.qty) - product.discount_amount
                else:
                    product.final_price = product.unit_price * product.qty

        @api.onchange('product')
        def _get_product_unit_price(self):
            for product in self:
                product.unit_price = product.product.lst_price
                product.final_price = product.unit_price * product.qty

class ac_order_wizard(models.TransientModel):
        _name = 'wizard_ac_order'
        _description = "Special Coupon"

        coupon_name = fields.Char('Coupon Name')
        coupon_code = fields.Char('Coupon Code')
        coupon_sale = fields.Float('Coupon Sale Amount')
        ac_order_id = fields.Many2many('ac_order.ac_order', string='AC Order Ref')

        def generate_code(self):
            self.create()
