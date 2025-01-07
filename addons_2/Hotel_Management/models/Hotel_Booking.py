from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelBooking(models.Model):
    # Setup info cơ bản của model nè
    _name = 'hotel.booking'  # Tên technical của model
    _description = 'Hotel Booking'  # Title hiển thị

    # Define các field cần thiết nè
    name = fields.Char('Booking Description', required=True)               # Mã book phòng (bắt buộc)
    customer_name = fields.Char('Customer Name')                           # Tên khách book
    booking_date = fields.Date('Booking Date', default=fields.Date.today)  # Ngày đky, auto là today
    hotel_id = fields.Many2one('hotel.management', 'Hotel')                # Link tới hotel (kiểu many2one)
    room_type = fields.Selection([
        ('single', 'Single'),  # Giường đơn
        ('double', 'Double')   # Giường đôi
    ], string='Room Type', required=True)  # Type giường (bắt buộc)
    
    
    room_id = fields.Many2one(
        'hotel.room', 
        'Room',
        domain="[('hotel_id', '=', hotel_id), ('state', '=', 'available'), ('bed_type', '=', room_type)]"
    )
    
    check_in = fields.Date('Check-in Date')  # Ngày vào
    check_out = fields.Date('Check-out Date')  # Ngày out
    state = fields.Selection([
        ('draft', 'New'),      # Status mới book
        ('confirmed', 'Confirmed')  # Status đã xác nhận
    ], string='Status', default='draft')  # Mặc định là draft khi mới tạo

    
    # Check valid date check-in/out
    @api.constrains('check_in', 'check_out')
    def _check_dates(self):
        for rec in self:
            # Check nếu date in > date out -> báo lỗi
            if rec.check_in and rec.check_out and rec.check_in > rec.check_out:
                raise ValidationError('Ngày check in không được lớn hơn ngày check out!')
            
            
    # Validate giá không được nhỏ hơn 0
    @api.constrains('price')
    def _check_price(self):
        for rec in self:
            if rec.price < 0:
                raise ValidationError('Giá không đượcn nhỏ hơn 0')
            
    
    # Validate không được book trùng phòng trong cùng thời gian
    @api.constrains('room_id', 'check_in', 'check_out', 'state')
    def _check_room_availability(self):
        for rec in self:
            if rec.room_id and rec.check_in and rec.check_out and rec.state == 'confirmed':
                # Tìm các booking khác của cùng phòng đó (trừ booking hiện tại)
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
            'guest_name': record.customer_name,  # Sử dụng guest_name từ bản ghi hiện tại
            'hotel_id': record.hotel_id.id,
            'room_id': record.room_id.id,
            'check_in': record.check_in,
            'check_out': record.check_out,
        })
    
        
        
    # Func xác nhận book phòng
    def action_confirm(self):
        for record in self.sudo(): 
            # Check nếu status = draft
            if record.state == 'draft':
                # Update status thành confirmed
                record.state = 'confirmed'
                if record.room_id:
                    # self._create_booking_history(record)
                    record.room_id.state = 'booked'
        return True

    
    
    
    
     # Override phương thức unlink để xử lý khi xóa booking
    def unlink(self):
        for record in self:
            # Nếu booking đã confirmed và có phòng được đặt
            if record.state == 'confirmed' and record.room_id:
                # Set trạng thái phòng về available
                record.room_id.state = 'available'
        # Gọi phương thức unlink của lớp cha để xóa bản ghi
        return super(HotelBooking, self).unlink()
    
    