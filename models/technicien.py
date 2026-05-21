from odoo import models, fields, api


class Technicien(models.Model):
    _name = 'technicien.management'
    _description = 'technicien'

    name=fields.Char(string='Nom du technicien',required=True)
    email=fields.Char(string='Nom du technicien')
    phone=fields.Char(string='Nom du technicien',required=True)
    competences=fields.Many2many(
        "competence.management",
        "technicien_competence",
        "technicien_id",
        "competence_id",
        string='Competances')
    disponibilite=fields.Boolean(string="Disponibilite")
    intervention_ids=fields.One2many(
        "intervention.management",
        "technicien_id",
        "Interventions")
    score_performance=fields.Float(compute="_compute_score")
    intervention_count=fields.Integer(compute="_compute_intervention_count")

    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)


