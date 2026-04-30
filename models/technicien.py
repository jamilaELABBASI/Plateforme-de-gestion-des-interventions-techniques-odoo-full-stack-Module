from odoo import models,fields


class Technicien(models.Model):
    _name = 'technicien'
    _description = 'technicien'

    name=fields.Char(string='Technicien',required=True)
    competances=fields.Many2many("competence","intervention_competence","intervention_id","competence_id",string='Competances')
    disponibilite=fields.Boolean
    interventions_ids=fields.One2many("intervention","technicien_id","Interventions")