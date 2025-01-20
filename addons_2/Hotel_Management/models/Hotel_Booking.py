from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelBooking(models.Model):
    _name = 'hotel.booking'
    _description = 'Hotel Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # Add new payment fields
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ], string='Payment Status', default='unpaid', readonly=True)
    
    payment_date = fields.Datetime('Payment Date', readonly=True)
    payment_amount = fields.Float('Payment Amount', readonly=True)

    name = fields.Char('Booking Description', required=True, tracking=True)
    # Thay đổi trường customer_name từ Char thành Many2one
    customer_name = fields.Many2one('res.partner', string='Customer', tracking=True, required=True)
    
    
    booking_date = fields.Date('Booking Date', default=fields.Date.today)
    hotel_id = fields.Many2one('hotel.management', 'Hotel')
    room_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double')
    ], string='Room Type', required=True)
    
    room_id = fields.Many2one(
        'hotel.room', 
        'Room',
        domain="[('hotel_id', '=', hotel_id), ('state', '=', 'available'), ('bed_type', '=', room_type)]"
    )
    
    check_in = fields.Date('Check-in Date')
    check_out = fields.Date('Check-out Date')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft')

    #region Booking Validate
    
    @api.constrains('check_in', 'check_out')
    def _check_dates(self):
        for rec in self:
            if rec.check_in and rec.check_out and rec.check_in > rec.check_out:
                raise ValidationError('Ngày check in không được lớn hơn ngày check out!')
            
    @api.constrains('price')
    def _check_price(self):
        for rec in self:
            if rec.price < 0:
                raise ValidationError('Giá không đượcn nhỏ hơn 0')
            
    @api.constrains('room_id', 'check_in', 'check_out', 'state')
    def _check_room_availability(self):
        for rec in self:
            if rec.room_id and rec.check_in and rec.check_out and rec.state == 'confirmed':
                domain = [
                    ('id', '!=', rec.id),
                    ('room_id', '=', rec.room_id.id),
                    ('state', '=', 'confirmed'),
                    '|',
                    '&', ('check_in', '<=', rec.check_in), ('check_out', '>=', rec.check_in),
                    '&', ('check_in', '<=', rec.check_out), ('check_out', '>=', rec.check_out)
                ]
                overlapping_bookings = self.search_count(domain)
                if overlapping_bookings:
                    raise ValidationError('Phòng này đã được đặt trong khoảng thời gian bạn chọn!')
            
    def _create_booking_history(self, record):
        self.env['hotel.booking.history'].create({
            'guest_name': record.customer_name,
            'hotel_id': record.hotel_id.id,
            'room_id': record.room_id.id,
            'check_in': record.check_in,
            'check_out': record.check_out,
        })
    
    #endregion
    
    # this action is to confirm a booking
    def action_confirm(self):
        for record in self.sudo(): 
            if record.state == 'draft' and record.payment_status == 'paid':
                record.state = 'confirmed'
                if record.room_id:
                    record.room_id.state = 'booked'
                    record.room_id._compute_last_booking_date()
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag' : 'display_notification',
                    'params': {
                        'title' : 'Lưu ý',
                        'message' : 'Chưa thanh toán!',
                        'sticky' : False,
                        'type': 'warning', # success: màu xanh lá
                                           # warning: màu vàng/cam
                                           # danger: màu đỏ
                                           # info: màu xanh dương (mặc định)
                    }
                }
        return True
    
    
    
    def unlink(self):
        for record in self:
            if record.state == 'confirmed' and record.room_id:
                record.room_id.state = 'available'
        return super(HotelBooking, self).unlink()
    
    def write(self, vals):
        result = super(HotelBooking, self).write(vals)
        if 'state' in vals and vals['state'] == 'confirmed':
            for record in self:
                if record.room_id:
                    record.room_id.state = 'booked'
        return result


    # this action is for server action (massc confirm booking orders)
    def action_mass_confirm(self):
        for record in self:
            if record.state == 'draft' and record.payment_status == 'paid':
                record.action_confirm()
        return True


    @api.onchange('room_id') 
    def _onchange_room_id(self):
        """Check if selected room is under maintenance"""
        if self.room_id and self.room_id.state == 'maintainance':
            raise ValidationError('Phòng này đang trong thời gian bảo trì, vui lòng chọn phòng khác!')

    def action_open_payment_wizard(self): # This one is to open the payment popup (target: 'new' is to open a new window (popup))
        """Open payment wizard"""
        return {
            'name': 'Thanh toán',
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.booking.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_booking_id': self.id,
                'default_hotel_id': self.hotel_id.id,
                'default_room_id': self.room_id.id,
            }
        }