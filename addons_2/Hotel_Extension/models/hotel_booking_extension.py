from odoo import models, api

class HotelBookingExtend(models.Model):
    _inherit = 'hotel.booking'

    def action_confirm(self):
        # Call parent method first
        result = super(HotelBookingExtend, self).action_confirm()
        
        # Create history only after confirmation
        for record in self:
            if record.state == 'confirmed':  # Check if actually confirmed
                self._create_booking_history(record)
        return result

    def _create_booking_history(self, record):
        return self.env['hotel.booking.history'].create({
            'guest_name': record.customer_name,
            'hotel_id': record.hotel_id.id,
            'room_id': record.room_id.id,
            'check_in': record.check_in,
            'check_out': record.check_out,
        })