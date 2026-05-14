from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.orm.decorators import readonly


class Intervention(models.Model):
    _name = 'intervention.management'
    _description = 'Intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Name',required=True)
    description=fields.Text(string='Description')
    client_id=fields.Many2one('res.partner',string='Client',required=True) # is a contact
    date_demande=fields.Datetime(string="Date de demande",default=fields.Datetime.now,readonly=True)
    date_intervention=fields.Datetime(string='Date de l\'intervention')
    statut = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ], default='nouveau')
    priorite=fields.Selection([
        ("basse", "Basse"),
        ("moyenne", "Moyenne"),
        ("haute", "Haute")
    ],string='Priorit de l\'intervention',default='moyenne')
    technicien_id = fields.Many2one(
        'technicien.management',
        string="Technicien")  # user of system has a login and pwd and access rights
    temps_passe=fields.Float(string='Temps passe de l\'intervention')
    rapport=fields.Text(string='Rapport')
    start_date = fields.Datetime(string="Date debut",default=fields.Datetime.now)
    end_date = fields.Datetime(string="Date fin")
    is_late=fields.Boolean(string="En retard",compute="_compute_is_late",store=True)
    estimated_duration=fields.Float()
    actual_duration=fields.Float()
    cost=fields.Float()

    @api.constrains('date_intervention', 'date_demande')
    def _check_date_intervention(self):
        now = fields.Datetime.now()

        for rec in self:

            if rec.date_intervention and rec.date_intervention < now:
                raise ValidationError("La date d'intervention ne peut pas être dans le passé.")

            if (rec.date_intervention and rec.date_demande and rec.date_intervention < rec.date_demande):
                raise ValidationError("La date d'intervention doit être supérieure ou égale à la date de demande.")

    def statut_encours(self):
        self.statut="en_cours"

    def statut_terminee(self):
        self.statut="terminee"
        # if not self.rapport:
        #     raise ValidationError("le rapport est obligatoire")


    @api.onchange("end_date")
    def _compute_is_late(self):
        now=fields.Datetime.now()
        for rec in self:
            rec.is_late=rec.end_date and rec.end_date < now



    @api.depends("is_late")
    def _notify_if_late(self):
        for rec in self:
            if rec.is_late:
                rec.message_post(body="cette intervention est en retard")


