from odoo import models, fields, api


class Technicien(models.Model):
    _name = 'technicien.management'
    _description = 'technicien'

    name=fields.Char(string='Nom du technicien',required=True)
    email=fields.Char(string='Email du technicien')
    address = fields.Char(string="Address", required=False, default="")
    phone = fields.Char(string="Phone", required=False, default="")
    competences=fields.Many2many(
        "competence.management",
        "technicien_competence",
        "technicien_id",
        "competence_id",
        string='Competances')
    disponibilite=fields.Boolean(string="Disponibilite")
    picture=fields.Image()
    intervention_ids=fields.One2many(
        "intervention.management",
        "technicien_id",
        "Interventions")
    score_performance=fields.Float(compute="_compute_score")
    intervention_count=fields.Integer(compute="_compute_intervention_count")
    user_id = fields.Many2one('res.users', string="User", help="Linked user account")
    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)

    def action_assign(self):
        self.state = 'assigned'

        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary='Nouvelle intervention',
            note='Une intervention vous a été assignée'
        )