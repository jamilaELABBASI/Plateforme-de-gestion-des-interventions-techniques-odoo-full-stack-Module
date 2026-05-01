from odoo import models, fields


class Competence(models.Model):
  _name='competence'
  _description='Competence'
  name=fields.Char(string='Name')
  description=fields.Text(string='Description')