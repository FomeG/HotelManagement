from odoo import models, fields, api

class BookingHistory(models.Model):
    _name = 'hotel.booking.history'
    _description = 'Hotel Booking History'
    _rec_name = 'guest_name'
    _order = 'hotel_id, check_in desc'  # Add ordering
     
    guest_name = fields.Char('Guest Name', required=True)
    hotel_id = fields.Many2one('hotel.management', 'Hotel', required=True)
    room_id = fields.Many2one('hotel.room', 'Room', required=True)
    check_in = fields.Date('Check-in Date')
    check_out = fields.Date('Check-out Date')
    
    
    
    
    room_name = fields.Char(related='room_id.name') 
    hotel_name = fields.Char(related='hotel_id.name') 
    
    
    

# class HotelManagementExtended(models.Model):
#     _inherit = 'hotel.management'

#     booking_history_ids = fields.One2many('hotel.booking.history', 'hotel_id', 'Booking History')

    
class HotelManagementExtended(models.Model):
    _inherit = 'hotel.management'

    booking_history_ids = fields.One2many('hotel.booking', 'hotel_id', string='Booking History')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # def action_view_booking_history(self):
    #     self.ensure_one()
    #     return {
    #         'name': 'Booking History',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'hotel.booking',
    #         'domain': [('hotel_id', '=', self.id)],
    #         'context': {'default_hotel_id': self.id},
    #     }
