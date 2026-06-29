from email.policy import default
from urllib.parse import quote

import requests

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class Intervention(models.Model):
    _name = 'intervention.management'
    _description = 'Intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date_creation_intervention desc"

    reference=fields.Char(string='Reference de l\'intervention',required=True)
    name=fields.Char(string='Name',required=True,tracking=True)
    description=fields.Text(string='Description')
    client_id=fields.Many2one('res.partner',string='Client',required=True) # is a contact
    address=fields.Char(string='Adresse',required=True)
    date_creation_intervention=fields.Datetime(string="Date de demande",default=fields.Datetime.now,readonly=True)
    date_resolution_intervention=fields.Datetime(string='Date de l\'intervention')
    statut = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ],default='nouveau',tracking=True)
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
    estimated_time=fields.Float()
    resolution_time=fields.Float(compute="_compute_resolution_time",store=True)
    currency_id = fields.Many2one('res.currency', string="Devise" , default=lambda self: self.env.company.currency_id)
    cost = fields.Monetary(currency_field='currency_id')
    before_picture=fields.Image()
    after_picture=fields.Image()
    total_interventions=fields.Integer(compute="_compute_kpis",store=True)
    interventions_nouveaus=fields.Integer()
    interventions_terminees=fields.Integer()
    interventions_en_cours=fields.Integer()
    interventions_annulee=fields.Integer()
    temps_moyen_resolution = fields.Float()
    cout_total = fields.Monetary(currency_field='currency_id')
    signature_client=fields.Binary(string="Signature du client")
    signature_technicien=fields.Binary(string="Signature du technicien ")

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

    def statut_annulee(self):
        self.statut="annulee"

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
    def _compute_resolution_time(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.resolution_time = (rec.end_date - rec.start_date).total_seconds() / 3600

            else:
                rec.resolution_time = 0

    """   """

   
    @api.depends("date_creation_intervention","date_resolution_intervention")
    def _compute_resolution_time(self):
        for rec in self:
            if rec.date_creation_intervention and rec.date_resolution_intervention:
                delta=rec.date_creation_intervention - rec.date_resolution_intervention
                rec.resolution_time = delta.total_seconds() / 3600
            else:
                rec.resolution_time = 0

    def _compute_kpis(self):
        for rec in self:
            rec.total_interventions = self.env['intervention.management'].search_count([])
            rec.interventions_nouveaus = self.env['intervention.management'].search_count(
                [('statut', '=', 'nouveau')]
            )
            rec.interventions_terminees = self.env['intervention.management'].search_count(
                [('statut', '=', 'terminee')]
            )
            rec.interventions_en_cours = self.env['intervention.management'].search_count(
                [('statut', '=', 'en_cours')]
            )
            rec.interventions_annulee = self.env['intervention.management'].search_count(
                [('statut', '=', 'annulee')]
            )

    def ouvrir_maps(self):
        self.ensure_one()

        if not self.client_id:
            raise UserError("Veuillez sélectionner un client.")

        address = self.client_id.contact_address

        if not address:
            raise UserError("Le client ne possède pas d'adresse.")

        return {
            "type": "ir.actions.act_url",
            "url": f"https://www.google.com/maps/search/?api=1&query={quote(address)}",
            "target": "new",
        }


    def action_localiser(self):
        self.ensure_one()

        if not self.address:
            raise UserError("Veuillez saisir une adresse.")

        url = "https://nominatim.openstreetmap.org/search"

        params = {
            "q": self.address,
            "format": "json",
            "limit": 1
        }

        headers = {
            "User-Agent": "Odoo"
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if not data:
            raise UserError("Adresse introuvable.")

        self.latitude = float(data[0]["lat"])
        self.longitude = float(data[0]["lon"])

