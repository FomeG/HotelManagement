from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelRoomExtended(models.Model):
    _inherit = 'hotel.room'

    room_size = fields.Float('Room Size (m2)')
    max_p_room = fields.Integer('Maximum People')
    allow_smoking = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Smoking Allowed?', default='no')
    
    
    @api.constrains('room_size', 'max_p_room')
    def _check_room_details(self):
        for rec in self:
            if rec.room_size <= 0:
                raise ValidationError('Kích thước phòng phải lớn hơn 0')
            if rec.max_p_room <= 0:
                raise ValidationError('Số lượng tối đa phải lớn hơn 0')