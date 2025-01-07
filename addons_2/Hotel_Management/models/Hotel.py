from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelManagement(models.Model):
    # Setup info cơ bản
    _name = 'hotel.management'  # Tên technical
    _description = 'Quản Lý Khách Sạn'  # Title hiển thị
    
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Kế thừa mail.thread và mail.activity.mixin

    # Define các field cần thiết
    name = fields.Char('Mã KS', required=True, tracking=True)  # Mã KS (bắt buộc)
    
    
    
    address = fields.Text('Địa Chỉ', tracking=True)  # Địa chỉ KS
    floor_count = fields.Integer('Số Tầng', tracking=True)  # Số tầng của KS
    room_count = fields.Integer('Tổng Số Phòng', compute='_compute_room_count', store=True)  # Count tổng phòng (tự tính)
    room_ids = fields.One2many('hotel.room', 'hotel_id', 'DS Phòng')  # List phòng trong KS (o2m)

    # Constraint SQL: Mã KS phải unique
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Mã KS phải là duy nhất!')
    ]



    @api.depends('room_ids')
    def _compute_room_count(self):
        for rec in self:
            rec.room_count = len(rec.room_ids)
