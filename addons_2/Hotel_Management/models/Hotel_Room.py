from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelRoom(models.Model):
    # Setup info cơ bản
    _name = 'hotel.room'  # Tên technical
    _description = 'Hotel Room'  # Title hiển thị

    # Define các field quan trọng
    hotel_id = fields.Many2one('hotel.management', 'Hotel', required=True)  # Link tới KS (bắt buộc)
    
    
    hotel_address = fields.Text(related='hotel_id.address', string='Hotel Address')  # Địa chỉ KS (lấy từ hotel_id)
    
    name = fields.Char('Room Number', required=True)  # Số phòng (bắt buộc)
    
    bed_type = fields.Selection([
        ('single', 'Single'),  # Giường đơn
        ('double', 'Double')   # Giường đôi
    ], string='Bed Type', required=True)  # Type giường (bắt buộc)
    price = fields.Float('Price')  # Giá phòng
    state = fields.Selection([
        ('available', 'Available'),  # TT còn trống
        ('booked', 'Booked')        # TT đã book
    ], string='Status', default='available')  # TT phòng, mặc định = available
    feature_ids = fields.Many2many('hotel.room.feature', string='Features')  # List tính năng phòng (m2m)

    # Constraint SQL: Số phòng phải unique trong cùng 1 KS
    _sql_constraints = [
        ('room_hotel_uniq', 'unique(name, hotel_id)', 'Số phòng không được trùng trong cùng KS!')
    ]