from odoo import models, fields

class Intervention(models.Model):
    _name = 'intervention'
    _description = 'Intervention'
    name=fields.Char(string='Name',required=True)
    description=fields.Text(string='Description')
    client_id=fields.Many2one('res.partner',string='Client',required=True) # is a contact
    date_demande=fields.Datetime(string="Date de demande",default=fields.Datetime.now)
    date_intervention=fields.Datetime(string='Date de l\'intervention')
    statut = fields.Selection([
        ('draft', 'Brouillon'),
        ('assigned', 'Assignée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancel', 'Annulée')
    ], string="Statut de l'intervention", default='draft')
    priorite=fields.Selection([
        ("low", "Basse"),
        ("medium", "Moyenne"),
        ("high", "Haute")
    ],string='Priorit de l\'intervention',default='medium')
    technicien_id = fields.Many2one('res.users', string="Technicien")  # user of system has a login and pwd and access rights
    temps_passe=fields.Float(string='Temps passe de l\'intervention')
    rapport=fields.Text(string='Rapport')
    # date_creation = fields.Datetime(default=fields.Datetime.now)

