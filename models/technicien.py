from odoo import models,fields


class Technicien(models.Model):
    _name = 'technicien'
    _description = 'technicien'

    name=fields.Char(string='Nom du technicien',required=True)
    competences=fields.Many2many("competence","intervention_competence","intervention_id","competence_id",string='Competances')
    disponibilite=fields.Boolean(string="Disponibilite")
    interventions_ids=fields.One2many("intervention","technicien_id","Interventions")