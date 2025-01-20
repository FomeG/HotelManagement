from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelServiceCategory(models.Model):
    _name = 'hotel.service.category'
    _description = 'Hotel Service Category'

    name = fields.Char('Category Name', required=True)
    code = fields.Char('Category Code')
    parent_id = fields.Many2one('hotel.service.category', string='Parent Category')
    child_ids = fields.One2many('hotel.service.category', 'parent_id', string='Child Categories')
    service_ids = fields.One2many('hotel.service', 'category_id', string='Services')
    
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    
    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError('Error! You cannot create recursive categories.')