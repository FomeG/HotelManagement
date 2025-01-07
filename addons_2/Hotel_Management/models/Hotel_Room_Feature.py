from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelRoomFeature(models.Model):
    _name = 'hotel.room.feature'
    _description = 'Room Features'

    name = fields.Char('Feature Name', required=True)
    description = fields.Text('Feature Description', required=True)
    feature_type = fields.Selection(
        [('comfort', 'Comfort'), 
         ('luxury', 'Luxury'), 
         ('basic', 'Basic')],
        string='Feature Type',
    )