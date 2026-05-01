from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Intervention(models.Model):
    _name = 'intervention'
    _description = 'Intervention'
    name=fields.Char(string='Name',required=True)
    description=fields.Text(string='Description')
    client_id=fields.Many2one('res.partner',string='Client',required=True) # is a contact
    date_demande=fields.Datetime(string="Date de demande",default=fields.Datetime.now)
    date_intervention=fields.Datetime(string='Date de l\'intervention')
    statut = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ], default='nouveau')
    priorite=fields.Selection([
        ("low", "Basse"),
        ("medium", "Moyenne"),
        ("high", "Haute")
    ],string='Priorit de l\'intervention',default='medium')
    technicien_id = fields.Many2one('technicien', string="Technicien")  # user of system has a login and pwd and access rights
    temps_passe=fields.Float(string='Temps passe de l\'intervention')
    rapport=fields.Text(string='Rapport')
    # date_creation = fields.Datetime(default=fields.Datetime.now)



    @api.constrains('date_intervention')
    def _check_date_intervention(self):
        for rec in self:
            if rec.date_intervention and rec.date_intervention < rec.date_demande:
                raise ValidationError(" Date invalide , vous ne pouvez pas rentrer une date passee")


    def statut_encours(self):
        self.statut="en_cours"

    def statut_terminee(self):
        self.statut="terminee"