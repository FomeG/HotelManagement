from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import timedelta

class HotelRoomProduct(models.Model):
    _inherit = 'hotel.room'
    _description = 'Hotel Room Product Extension'

    # Link to product template and variant
    product_tmpl_id = fields.Many2one(
        'product.template', 
        string='Product Template',
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Product Variant',
        related='product_tmpl_id.product_variant_id',
        readonly=True
    )

    state = fields.Selection(selection_add=[
        ('reserved', 'Reserved'),
    ])
    
    
    weekend_price = fields.Float('Weekend Price')

            
            
            
    @api.model_create_multi
    def create(self, vals_list):
        # When creating new room:
        # 1. Create product template first
        # 2. Link it to room
        # 3. Save everything
        ProductTemplate = self.env['product.template']
        rooms = []
        
        for vals in vals_list:
            # Setup product vals
            product_vals = {
                'name': vals.get('name'),
                'type': 'service',
                'sale_ok': True,
                'purchase_ok': False,
                'list_price': vals.get('price', 0.0),
            }
            product_tmpl = ProductTemplate.create(product_vals)
            
            vals['product_tmpl_id'] = product_tmpl.id
            
            room = super(HotelRoomProduct, self).create([vals])
            rooms.append(room.id)
        
        return self.browse(rooms)

    def write(self, vals):
        # Update product price when room price changes
        if 'price' in vals:
            for room in self:
                if room.product_tmpl_id:
                    room.product_tmpl_id.list_price = vals['price']
        return super().write(vals)

    def unlink(self):
        # Store products to delete
        product_tmpls = self.mapped('product_tmpl_id')
        
        # Delete rooms first
        res = super().unlink()
        
        # Then delete associated products
        if product_tmpls:
            product_tmpls.unlink()
            
        return res
    
    
    
    def cron_check_maintaining_rooms(self):
        """Automatically change room state from maintenance to available after 1 day"""
        maintenance_rooms = self.search([
            ('state', '=', 'maintenance')
        ])
        
        if maintenance_rooms:
            maintenance_rooms.write({
                'state': 'available'
            })
            # Log message for tracking
            for room in maintenance_rooms:
                room.message_post(
                    body=f"Room {room.name} state automatically changed from maintenance to available by system",
                    message_type='notification'
                )