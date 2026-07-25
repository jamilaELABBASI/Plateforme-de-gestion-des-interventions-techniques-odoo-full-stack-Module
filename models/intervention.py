from urllib.parse import quote
import requests
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError



class Intervention(models.Model):
    _name = 'intervention.management'
    _description = 'Intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date_creation_intervention desc"

    reference = fields.Char(
        string="Référence",
        readonly=True,
        copy=False,
        default="Nouveau",
        tracking=True
    )
    name = fields.Char(string='Name', required=True, tracking=True)
    description = fields.Text(string='Description')
    client_id = fields.Many2one('res.partner', string='Client', required=True)  # is a contact
    address = fields.Char(string='Adresse', required=True)
    date_creation_intervention = fields.Datetime(string="Date de demande", default=fields.Datetime.now, readonly=True)
    date_resolution_intervention = fields.Datetime(string='Date de l\'intervention')
    state = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ], default='nouveau', tracking=True)
    priorite = fields.Selection([
        ("basse", "Basse"),
        ("moyenne", "Moyenne"),
        ("haute", "Haute")
    ], string='Priorit de l\'intervention', default='moyenne', tracking=True)

    technicien_id = fields.Many2one(
        'technicien.management',
        string="Technicien")  # user of system has a login and pwd and access rights
    comment = fields.Text(string='Commentaire')
    start_date = fields.Datetime(string="Date debut", default=fields.Datetime.now)
    end_date = fields.Datetime(string="Date fin")
    is_late = fields.Boolean(string="En retard", compute="_compute_is_late", store=True)
    estimated_time = fields.Float()
    resolution_time = fields.Float(compute="_compute_resolution_time", store=True)
    currency_id = fields.Many2one('res.currency', string="Devise", default=lambda self: self.env.company.currency_id)
    cost = fields.Monetary(currency_field='currency_id')
    before_picture = fields.Image()
    after_picture = fields.Image()
    total_interventions = fields.Integer(compute="_compute_kpis", store=True)
    interventions_nouveaus = fields.Integer()
    interventions_terminees = fields.Integer()
    interventions_en_cours = fields.Integer()
    interventions_annulee = fields.Integer()
    temps_moyen_resolution = fields.Float()
    cout_total = fields.Monetary(currency_field='currency_id')
    signature_client = fields.Binary(string="Signature du client")
    signature_technicien = fields.Binary(string="Signature du technicien ")

    sla = fields.Selection([
        ('24', '24 heures'),
        ('48', '48 heures'),
        ('72', '72 heures'),
    ], string="SLA", default='48', tracking=True)

    deadline = fields.Datetime(
        string="Date limite",
        compute="_compute_deadline",
        store=True
    )

    sla_respecte = fields.Boolean(
        string="SLA respecté",
        compute="_compute_deadline",
        store=True
    )

    equipement_id = fields.Many2one(
        "equipement.management",
        string="Équipement"
    )

    calendar_event_id=fields.Many2one("calendar.event",string="Evenement")

    @api.constrains("date_creation_intervention", "date_resolution_intervention")
    def _check_date_intervention(self):
        for rec in self:
            if (
                    rec.date_creation_intervention
                    and rec.date_resolution_intervention
                    and rec.date_resolution_intervention < rec.date_creation_intervention
            ):
                raise ValidationError(
                    "La date de résolution doit être supérieure ou égale à la date de création."
                )

    def action_in_progress(self):
        self.state = "en_cours"

    def action_done(self):
        self.state = "terminee"
        # if not self.rapport:
        #     raise ValidationError("le rapport est obligatoire")

    def action_cancel(self):
        self.state = "annulee"

    @api.onchange("end_date")
    def _compute_is_late(self):
        for rec in self:
            rec.is_late = (
                    rec.end_date
                    and rec.end_date < fields.Datetime.now()
                    and rec.state != "terminee")

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
            if rec.technicien_id.intervention_count > 3:
                raise ValidationError("Technicien surcharge")

    @api.model
    def create(self, vals):

        if vals.get('reference', 'Nouveau') == 'Nouveau':
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'intervention.management'
            )
        return super().create(vals)

    """
    @api.depends('start_date', 'end_date')
    def _compute_resolution_time(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.resolution_time = (rec.end_date - rec.start_date).total_seconds() / 3600

            else:
                rec.resolution_time = 0

    """

    @api.depends("date_creation_intervention", "date_resolution_intervention")
    def _compute_resolution_time(self):
        for rec in self:
            if rec.date_creation_intervention and rec.date_resolution_intervention:
                delta = rec.date_creation_intervention - rec.date_resolution_intervention
                rec.resolution_time = delta.total_seconds() / 3600
            else:
                rec.resolution_time = 0

    def _compute_kpis(self):
        for rec in self:
            rec.total_interventions = self.env['intervention.management'].search_count([])
            rec.interventions_nouveaus = self.env['intervention.management'].search_count(
                [('state', '=', 'nouveau')]
            )
            rec.interventions_terminees = self.env['intervention.management'].search_count(
                [('state', '=', 'terminee')]
            )
            rec.interventions_en_cours = self.env['intervention.management'].search_count(
                [('state', '=', 'en_cours')]
            )
            rec.interventions_annulee = self.env['intervention.management'].search_count(
                [('state', '=', 'annulee')]
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

    @api.depends("date_creation_intervention", "sla", "date_resolution_intervention")
    def _compute_deadline(self):
        for rec in self:
            rec.deadline = False
            rec.sla_respecte = False

            if rec.date_creation_intervention:
                heures = int(rec.sla or 48)

                rec.deadline = fields.Datetime.add(
                    rec.date_creation_intervention,
                    hours=heures
                )

                if rec.date_resolution_intervention:
                    rec.sla_respecte = (
                            rec.date_resolution_intervention <= rec.deadline
                    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            # Envoyer l'email au technicien si assigné
            if record.technicien_id and record.technicien_id.email:
                template_technicien = self.env.ref('intervention_management.intervention_email_technicien',
                                        raise_if_not_found=False)

                template_client = self.env.ref(
                        "intervention_management.intervention_email_client",
                        raise_if_not_found=False)

                if template_technicien:
                    template_technicien.send_mail(record.id, force_send=True)
                    record.message_post(
                        body=f"📧 Email envoyé à {record.technicien_id.name} ({record.technicien_id.email})",
                        message_type='notification'
                    )
                if template_client:
                    template_client.send_mail(record.id, force_send=True)
                    record.message_post(
                        body=f"📧 Email envoyé à {record.client_id.name} ({record.client_id.email})",
                        message_type='notification'
                    )
        return records

    @api.model_create_multi
    def create(self, vals_list):
        """Créer une intervention et envoyer l'email automatiquement"""
        records = super().create(vals_list)
        for record in records:
            # Envoyer l'email automatiquement
            record._send_email_notification()
        return records

    def write(self, vals):
        """Mettre à jour une intervention et envoyer l'email si le technicien change"""
        result = super().write(vals)

        # Si le technicien a été modifié, envoyer l'email
        if 'technicien_id' in vals:
            for record in self:
                if record.technicien_id and record.technicien_id.email:
                    record._send_email_notification()

        return result

    def _send_email_notification(self):
        """Envoyer l'email au technicien et au client (méthode interne)"""
        self.ensure_one()

        # 1. Envoyer au technicien
        if self.technicien_id and self.technicien_id.email:
            try:
                mail = self.env['mail.mail'].create({
                    'subject': f'Nouvelle intervention : {self.reference}',
                    'body_html': f"""
                        <h2>Nouvelle intervention</h2>
                        <p>Bonjour {self.technicien_id.name},</p>
                        <p>Une nouvelle intervention vous a été affectée.</p>
                        <ul>
                            <li><b>Référence :</b> {self.reference}</li>
                            <li><b>Client :</b> {self.client_id.name if self.client_id else 'Non spécifié'}</li>
                            <li><b>Description :</b> {self.description or 'Aucune description'}</li>
                        </ul>
                        <p>Cordialement,<br/>Service Gestion des Interventions</p>
                    """,
                    'email_to': self.technicien_id.email,
                    'email_from': 'mega.cours.jamila@gmail.com',
                })
                mail.send()
                self.message_post(
                    body=f"📧 Email envoyé au technicien {self.technicien_id.name} ({self.technicien_id.email})",
                    message_type='notification'
                )
            except Exception as e:
                self.message_post(
                    body=f"❌ Erreur technicien: {str(e)}",
                    message_type='notification'
                )

        # 2. Envoyer au client
        if self.client_id and self.client_id.email:
            try:
                mail = self.env['mail.mail'].create({
                    'subject': f'Confirmation d\'intervention : {self.reference}',
                    'body_html': f"""
                        <h2>Confirmation d'intervention</h2>
                        <p>Bonjour {self.client_id.name},</p>
                        <p>Votre demande d'intervention a bien été enregistrée.</p>
                        <ul>
                            <li><b>Référence :</b> {self.reference}</li>
                            <li><b>Technicien :</b> {self.technicien_id.name if self.technicien_id else 'Non assigné'}</li>
                            <li><b>Description :</b> {self.description or 'Aucune description'}</li>
                        </ul>
                        <p>Nous vous contacterons dès que possible.</p>
                        <p>Cordialement,<br/>Service Gestion des Interventions</p>
                    """,
                    'email_to': self.client_id.email,
                    'email_from': 'mega.cours.jamila@gmail.com',
                })
                mail.send()
                self.message_post(
                    body=f"📧 Email envoyé au client {self.client_id.name} ({self.client_id.email})",
                    message_type='notification'
                )
            except Exception as e:
                self.message_post(
                    body=f"❌ Erreur client: {str(e)}",
                    message_type='notification'
                )

    def action_create_calendar_event(self):
        for intervention in self:
            event=self.env['calendar.event'].create({
                'name': intervention.name,
                'start': intervention.start_date,
                'stop': intervention.end_date,
                'partner_ids':[
                    (4,intervention.client_id.id),
                ]
            })

            intervention.calendar_event_id=event.id





    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super().create(vals_list)
    #
    #     template_client = self.env.ref(
    #         "intervention_management.email_template_intervention_client",
    #         raise_if_not_found=False
    #     )
    #
    #     template_technicien = self.env.ref(
    #         "intervention_management.email_template_intervention_technicien",
    #         raise_if_not_found=False
    #     )
    #
    #     for record in records:
    #
    #         # Email client
    #         if (
    #                 template_client
    #                 and record.client_id
    #                 and record.client_id.email
    #         ):
    #             template_client.send_mail(record.id, force_send=True)
    #
    #         # Email technicien
    #         if (
    #                 template_technicien
    #                 and record.technicien_id
    #                 and record.technicien_id.email
    #         ):
    #             template_technicien.send_mail(record.id, force_send=True)
    #
    #     return records