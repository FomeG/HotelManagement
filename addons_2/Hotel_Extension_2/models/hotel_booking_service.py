from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelBookingServiceLine(models.Model):
    _name = 'hotel.booking.service.line'
    _description = 'Hotel Booking Service Line'

    booking_id = fields.Many2one('hotel.booking', string='Booking')
    service_id = fields.Many2one('hotel.service', string='Service', required=True)
    quantity = fields.Float('Quantity', required=True, default=1.0)
    price_unit = fields.Float('Unit Price', related='service_id.price', readonly=True)
    price_total = fields.Float('Total', compute='_compute_price_total', store=True)
    
    
    # Thêm trường related để truy cập qty_available
    available_qty = fields.Float('Available Quantity', related='service_id.qty_available', readonly=True)
    
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_total(self):
        for line in self:
            line.price_total = line.quantity * line.price_unit

    @api.onchange('service_id', 'quantity')
    def _onchange_service_quantity(self):
        if self.service_id and self.quantity:
            # Kiểm tra nếu là dịch vụ có track inventory
            if self.service_id.service_type in ['food', 'drink']:
                qty_available = self.service_id.qty_available
                if qty_available <= 0:
                    return {
                        'warning': {
                            'title': 'Hết hàng!',
                            'message': f'Dịch vụ {self.service_id.name} đã hết hàng!'
                        }
                    }
                if self.quantity > qty_available:
                    return {
                        'warning': {
                            'title': 'Không đủ hàng!',
                            'message': f'Trong kho chỉ còn {qty_available} {self.service_id.name}!'
                        }
                    }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            service = self.env['hotel.service'].browse(vals.get('service_id'))
            quantity = vals.get('quantity', 0)
            
            if service.service_type in ['food', 'drink']:
                if service.qty_available <= 0:
                    raise ValidationError(f'Dịch vụ {service.name} đã hết hàng!')
                if quantity > service.qty_available:
                    raise ValidationError(f'Trong kho chỉ còn {service.qty_available} {service.name}!')
                
                # Cập nhật số lượng trong kho
                stock_quant = self.env['stock.quant'].sudo()
                stock_quant._update_available_quantity(
                    service.product_tmpl_id.product_variant_id,
                    self.env.ref('stock.warehouse0').lot_stock_id,
                    -quantity
                )
                
        return super().create(vals_list)

    def write(self, vals):
        if 'quantity' in vals:
            for line in self:
                if line.service_id.service_type in ['food', 'drink']:
                    old_qty = line.quantity
                    new_qty = vals['quantity']
                    diff_qty = new_qty - old_qty
                    
                    if diff_qty > 0:  # Nếu tăng số lượng
                        if line.service_id.qty_available <= 0:
                            raise ValidationError(f'Dịch vụ {line.service_id.name} đã hết hàng!')
                        if diff_qty > line.service_id.qty_available:
                            raise ValidationError(f'Trong kho chỉ còn {line.service_id.qty_available} {line.service_id.name}!')
                    
                    # Cập nhật số lượng trong kho
                    stock_quant = self.env['stock.quant'].sudo()
                    stock_quant._update_available_quantity(
                        line.service_id.product_tmpl_id.product_variant_id,
                        self.env.ref('stock.warehouse0').lot_stock_id,
                        -diff_qty
                    )
                    
        return super().write(vals)

    def unlink(self):
        for line in self:
            if line.service_id.service_type in ['food', 'drink']:
                # Hoàn lại số lượng vào kho khi xóa line
                stock_quant = self.env['stock.quant'].sudo()
                stock_quant._update_available_quantity(
                    line.service_id.product_tmpl_id.product_variant_id,
                    self.env.ref('stock.warehouse0').lot_stock_id,
                    line.quantity
                )
        return super().unlink()