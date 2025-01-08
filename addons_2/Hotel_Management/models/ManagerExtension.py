from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hotel_ids = fields.One2many(
        'hotel.management',
        'manager_id',
        string='Khách Sạn Quản Lý'
    )
