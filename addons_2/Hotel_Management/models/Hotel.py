from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelManagement(models.Model):
    _name = 'hotel.management'
    _description = 'Quản Lý Khách Sạn'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Mã KS', required=True, tracking=True)
    address = fields.Text('Địa Chỉ', tracking=True)
    floor_count = fields.Integer('Số Tầng', tracking=True)
    room_count = fields.Integer('Tổng Số Phòng', compute='_compute_room_count', store=True)
    room_ids = fields.One2many('hotel.room', 'hotel_id', 'DS Phòng')

    manager_id = fields.Many2one(
        'hr.employee',
        string='Quản Lý',
        required=True,
        tracking=True,
    )
    
    
    employee_ids = fields.Many2many(
        'hr.employee',
        'hotel_employee_rel',
        'hotel_id',
        'employee_id',
        string='Nhân Viên',
        tracking=True,
    )  


    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Mã KS phải là duy nhất!')
    ]

    # @api.constrains('manager_id')
    # def _check_manager(self):
    #     for hotel in self:
    #         if hotel.manager_id and not hotel.manager_id.child_ids:
    #             raise ValidationError("Quản lý được chọn phải có nhân viên dưới quyền")
            
            
    @api.depends('room_ids')
    def _compute_room_count(self):
        for rec in self:
            rec.room_count = len(rec.room_ids)



    @api.onchange('manager_id')
    def _onchange_manager_id(self):
        # Khi thay đổi manager, tự động cập nhật danh sách nhân viên có thể chọn
        if self.manager_id:
            return {'domain': {
                'employee_ids': [('parent_id', '=', self.manager_id.id), 
                            ('id', '!=', self.manager_id.id)]
            }}
    
    
    
    @api.constrains('manager_id', 'employee_ids')
    def _check_employees(self):
        for record in self:
            if record.manager_id and record.employee_ids:
                # Kiểm tra xem tất cả nhân viên có thuộc quyền quản lý của manager không
                invalid_employees = record.employee_ids.filtered(
                    lambda emp: emp.parent_id != record.manager_id
                )
                if invalid_employees:
                    raise ValidationError(
                        'Các nhân viên sau không thuộc quyền quản lý của %s: %s'
                     % (record.manager_id.name, ', '.join(invalid_employees.mapped('name'))))
            
            
    # @api.onchange('manager_id')
    # def _onchange_manager_id(self):
    #     group_hotel_manager = self.env.ref('Hotel_Management.group_hotel_manager')
    #     users_with_manager_group = self.env['res.users'].search([
    #         ('groups_id', 'in', [group_hotel_manager.id])
    #     ])
    #     employees = self.env['hr.employee'].search([
    #         ('user_id', 'in', users_with_manager_group.ids)
    #     ])
    #     return {
    #         'domain': {
    #             'manager_id': [('id', 'in', employees.ids)]
    #         }
    #     }
