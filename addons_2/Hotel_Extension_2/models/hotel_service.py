from odoo import _, models, fields, api
from odoo.exceptions import ValidationError

class HotelService(models.Model):
    _name = 'hotel.service'
    _description = 'Hotel Services'
    _inherits = {'product.template': 'product_tmpl_id'}  # hey we inherit from product.template!

    # Basic fields for service info
    name = fields.Char('Service Name', required=True) 
    description = fields.Text('Description')  # some details about service
    price = fields.Float('Price', required=True)  # price of service, need this too!
    service_type = fields.Selection([
        ('food', 'Foods'),
        ('drink', 'Drinks'),
        ('laundry', 'Laundry'), 
        ('self', 'Self Service'),
        ('other', 'Other Services'),
    ], string='Service Type', required=True)  # what kind of service is this?
    
    # Link to product template - rly important!
    product_tmpl_id = fields.Many2one(
        'product.template', 
        string='Product Template',
        ondelete='cascade'  # if service gone, product gone too
    )
    
    # Thêm vào class HotelService
    qty_available = fields.Float('Quantity On Hand', related='product_tmpl_id.qty_available', readonly=True)
    virtual_available = fields.Float('Forecasted Quantity', related='product_tmpl_id.virtual_available', readonly=True)
    
    category_id = fields.Many2one('hotel.service.category', string='Category')
    tracking_inventory = fields.Boolean('Track Inventory', default=True)
    qty_available = fields.Float('Quantity On Hand', related='product_tmpl_id.qty_available', readonly=True)
    virtual_available = fields.Float('Forecasted Quantity', related='product_tmpl_id.virtual_available', readonly=True)

    inventory_ids = fields.One2many('hotel.service.inventory', 'service_id', string='Inventory Movements')
    booking_line_ids = fields.One2many('hotel.booking.service.line', 'service_id', string='Booking Lines')
    
    @api.onchange('service_type')
    def _onchange_service_type(self):
        if self.service_type == 'self':
            self.price = 0.0

    @api.model_create_multi 
    def create(self, vals_list):
        # When creating new service:
        # 1. Make product template first with correct type based on service_type
        # 2. Link it to service
        # 3. Save everything
        
        ProductTemplate = self.env['product.template']
        services = []
        
        for vals in vals_list:
            # Determine product type based on service_type
            service_type = vals.get('service_type')
            
            # Set price to 0 for self service
            if service_type == 'self':
                vals['price'] = 0.0
            
            # Setup product vals
            product_vals = {
                'name': vals.get('name'),
                # For laundry, self service and other services use type='service'
                # For food and drinks use type='product' since they are countable
                'type': 'service' if service_type in ['laundry', 'self', 'other'] else 'consu',
                'sale_ok': True,  # can be sold
                'purchase_ok': False,  # but cant be purchased 
                'list_price': vals.get('price', 0.0),
            }
            
            # Enable inventory tracking for products (food and drinks)
            if service_type in ['food', 'drink']:
                product_vals.update({
                    'tracking': 'lot',  # Enable lot/serial tracking
                    'is_storable': True, 
                })
                
                
            product_tmpl = ProductTemplate.create(product_vals)
            vals['product_tmpl_id'] = product_tmpl.id
            
            service = super(HotelService, self).create([vals])
            services.append(service.id)
        
        return self.browse(services)
    

    def write(self, vals):
        # Update product price when service price changes
        if 'price' in vals:
            vals['list_price'] = vals['price']
            
            # Cập nhật giá trong các sale order line đang ở trạng thái draft/sent
            product_variant = self.product_tmpl_id.product_variant_id
            if product_variant:
                sale_lines = self.env['sale.order.line'].search([
                    ('product_id', '=', product_variant.id),
                    ('order_id.state', 'in', ['draft', 'sent'])
                ])
                if sale_lines:
                    sale_lines.write({'price_unit': vals['price']})
                    
        return super().write(vals)
    
    
    
    def unlink(self):
            # Collect all product templates and variants first
            product_tmpls = self.mapped('product_tmpl_id')
            product_variants = product_tmpls.mapped('product_variant_ids')
            
            for service in self:
                product_variant = service.product_tmpl_id.product_variant_id
                if product_variant:
                    # Check if the service is used in any confirmed sale orders
                    sale_lines = self.env['sale.order.line'].search([
                        ('product_id', '=', product_variant.id),
                        ('order_id.state', 'not in', ['draft', 'sent', 'cancel'])
                    ])
                    
                    if sale_lines:
                        raise ValidationError(_(
                            'Cannot delete service "%s" because it is being used in confirmed orders!', 
                            service.name
                        ))
            
            # Store template IDs before unlinking the service
            template_ids = product_tmpls.ids
            
            # First unlink the service records
            result = super(HotelService, self).unlink()
            
            if result:
                # Then manually delete the products and templates
                if product_variants:
                    product_variants.unlink()
                
                # Finally delete the templates
                self.env['product.template'].browse(template_ids).unlink()
                
            return result