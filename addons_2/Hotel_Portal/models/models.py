# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class hotel__portal(models.Model):
#     _name = 'hotel__portal.hotel__portal'
#     _description = 'hotel__portal.hotel__portal'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

