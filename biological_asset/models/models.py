# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class biological_asset(models.Model):
#     _name = 'biological_asset.biological_asset'
#     _description = 'biological_asset.biological_asset'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
