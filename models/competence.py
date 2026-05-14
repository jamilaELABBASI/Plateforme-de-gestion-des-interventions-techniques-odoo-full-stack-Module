from odoo import models, fields


class Competence(models.Model):
  _name='competence.management'
  _description='Competence'
  name=fields.Char(string='Name',required=True)
  description=fields.Text(string='Description')
  technicien_ids=fields.Many2many(
    'technicien.management',
    'technicien_competence',
    'competence_id',
    'technicien_id',
    'Techniciens',
  )