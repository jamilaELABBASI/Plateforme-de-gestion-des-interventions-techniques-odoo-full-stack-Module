from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Intervention(models.Model):
    _name = 'intervention.management'
    _description = 'Intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference=fields.Char(string='Reference de l\'intervention',required=True)
    name=fields.Char(string='Name',required=True,tracking=True)
    description=fields.Text(string='Description')
    client_id=fields.Many2one('res.partner',string='Client',required=True) # is a contact
    address=fields.Char(string='Adresse',required=True)
    date_demande=fields.Datetime(string="Date de demande",default=fields.Datetime.now,readonly=True)
    date_intervention=fields.Datetime(string='Date de l\'intervention')
    statut = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ], default='nouveau',tracking=True)
    priorite=fields.Selection([
        ("basse", "Basse"),
        ("moyenne", "Moyenne"),
        ("haute", "Haute")
    ],string='Priorit de l\'intervention',default='moyenne',tracking=True)
    technicien_id = fields.Many2one(
        'technicien.management',
        string="Technicien")  # user of system has a login and pwd and access rights
    comment=fields.Text(string='Commentaire')
    start_date = fields.Datetime(string="Date debut",default=fields.Datetime.now)
    end_date = fields.Datetime(string="Date fin")
    is_late=fields.Boolean(string="En retard",compute="_compute_is_late",store=True)
    actual_estimated=fields.Float()
    actual_duration=fields.Float(compute="_compute_actual_duration",store=True)
    cost=fields.Float()
    before_picture=fields.Image()
    after_picture=fields.Image()

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
        for rec in self:
            rec.is_late = (
                    rec.end_date
                    and rec.end_date < fields.Datetime.now()
                    and rec.statut != "terminee")


    @api.depends("is_late")
    def _notify_if_late(self):
        for rec in self:
            if rec.is_late:
                rec.message_post(body="cette intervention est en retard")


    @api.constrains('technicien_id')
    def _check_disponibilite(self):
        for rec in self:
            if not rec.technicien_id:
                continue
            if rec.technicien_id.intervention_count >= 3:
                raise ValidationError("Technicien surcharge")



    @api.depends('start_date', 'end_date')
    def _compute_actual_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.actual_duration = (rec.end_date - rec.start_date).total_seconds() / 3600

            else:
                rec.actual_duration = 0
