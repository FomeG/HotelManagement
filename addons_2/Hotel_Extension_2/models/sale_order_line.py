from odoo import models, fields, api

class SaleOrderLineExtend(models.Model):
    _inherit = 'sale.order.line'
    
    def write(self, vals):
        # Nếu thay đổi price_unit
        if 'price_unit' in vals:
            for line in self:
                # Kiểm tra  product có phải là hotel service
                hotel_service = self.env['hotel.service'].search([
                    ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)
                ], limit=1)
                
                if hotel_service and line.order_id.state in ['draft', 'sent']:
                    # Cập nhật giá trong hotel service
                    hotel_service.write({
                        'price': vals['price_unit']
                    })
                    
        return super().write(vals)