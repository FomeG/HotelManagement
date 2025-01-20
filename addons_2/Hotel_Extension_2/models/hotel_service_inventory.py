from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelServiceInventory(models.Model):
    _name = 'hotel.service.inventory'
    _description = 'Hotel Service Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Reference', required=True, copy=False, readonly=True, 
                      default=lambda self: ('New'))
    date = fields.Date('Date', default=fields.Date.today, required=True)
    service_id = fields.Many2one('hotel.service', string='Service', required=True,
                                ondelete='restrict') 
    quantity = fields.Float('Quantity', required=True)
    unit_price = fields.Float('Unit Price', related='service_id.price', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', ('New')) == ('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hotel.service.inventory') or ('New')
        return super().create(vals_list)

    def action_confirm(self):
        for record in self:
            # Update quantity in product
            if record.service_id.product_tmpl_id:
                stock_quant = self.env['stock.quant'].sudo()
                stock_quant._update_available_quantity(
                    record.service_id.product_tmpl_id.product_variant_id,
                    self.env.ref('stock.warehouse0').lot_stock_id,
                    record.quantity
                )
            record.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})