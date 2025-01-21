from odoo import models, fields, api

class HotelPOSOrder(models.Model):
    _inherit = 'pos.order'
    
    hotel_booking_id = fields.Many2one('hotel.booking', string='Hotel Booking')
    
    def _prepare_invoice_vals(self):
        # Kế thừa method tạo hóa đơn từ POS
        vals = super()._prepare_invoice_vals()
        if self.hotel_booking_id:
            vals['hotel_booking_id'] = self.hotel_booking_id.id
        return vals