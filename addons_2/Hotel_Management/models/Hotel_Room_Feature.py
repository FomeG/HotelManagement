from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelRoomFeature(models.Model):
    _name = 'hotel.room.feature'
    _description = 'Room Features'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Feature Name', required=True, tracking=True)
    description = fields.Text('Feature Description', required=True, tracking=True)
    feature_type = fields.Selection(
        [('comfort', 'Comfort'), 
         ('luxury', 'Luxury'), 
         ('basic', 'Basic')],
        string='Feature Type',
        tracking=True,
    )