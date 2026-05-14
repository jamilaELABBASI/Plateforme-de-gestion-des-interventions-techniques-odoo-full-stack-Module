from odoo import models,fields


class Technicien(models.Model):
    _name = 'technicien.management'
    _description = 'technicien'

    name=fields.Char(string='Nom du technicien',required=True)
    email=fields.Char(string='Nom du technicien',required=True)
    phone=fields.Char(string='Nom du technicien',required=True)
    competences=fields.Many2many(
        "competence.management",
        "technicien_competence",
        "technicien_id",
        "competence_id",
        string='Competances')
    disponibilite=fields.Boolean(string="Disponibilite")
    interventions_ids=fields.One2many(
        "intervention.management",
        "technicien_id",
        "Interventions")
    score_performance=fields.Float(compute="_compute_score")
    intervention_count=fields.Float(compute="_compute_count")