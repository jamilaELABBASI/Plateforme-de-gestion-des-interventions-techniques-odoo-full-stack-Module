import base64
from io import BytesIO

import qrcode

from odoo import models, fields, api


class Equipement(models.Model):
    _name = "equipement.management"
    _description = "Équipement"

    name = fields.Char(string="Nom", required=True)
    description=fields.Char(string="Description")
    numero_serie = fields.Char(string="Numéro de série")
    reference = fields.Char(
        string="Référence",
        required=True,
        readonly=True,
        copy=False,
        default="Nouveau"
    )
    client_id = fields.Many2one(
        "res.partner",
        string="Client",
        required=True
    )

    marque = fields.Char(string="Marque")
    modele = fields.Char(string="Modèle")

    date_achat = fields.Date(string="Date d'achat")

    date_fin_garantie = fields.Date(
        string="Fin de garantie"
    )

    intervention_ids = fields.One2many(
        "intervention.management",
        "equipement_id",
        string="Interventions"
    )

    intervention_count = fields.Integer(
        compute="_compute_intervention_count"
    )

    categorie = fields.Selection([
        ('ordinateur', 'Ordinateur'),
        ('imprimante', 'Imprimante'),
        ('serveur', 'Serveur'),
        ('reseau', 'Équipement réseau'),
        ('autre', 'Autre'),
    ], string="Catégorie", default='autre')

    date_fin_garantie = fields.Date(string="Fin de garantie")
    garantie_active = fields.Boolean(
        string="Garantie active",
        compute="_compute_garantie_active",
        store=True
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'equipement_attachment_rel',
        'equipement_id',
        'attachment_id',
        string="Documents"
    )


    qr_code=fields.Binary(string="QR Code",compute="_compute_qr_code",store=True)
    photo=fields.Image()

    def _compute_intervention_count(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)

    @api.depends("date_fin_garantie")
    def _compute_garantie_active(self):
        today = fields.Date.today()
        for rec in self:
            rec.garantie_active = bool(
                rec.date_fin_garantie and
                rec.date_fin_garantie >= today
            )

    @api.depends("reference")
    def _compute_qr_code(self):
        for rec in self:
            if rec.reference:
                qr = qrcode.QRCode(
                    version=1,
                    box_size=8,
                    border=2,
                )

                qr.add_data(rec.reference)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                buffer = BytesIO()
                img.save(buffer, format="PNG")

                rec.qr_code = base64.b64encode(buffer.getvalue())
            else:
                rec.qr_code = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "Nouveau") == "Nouveau":
                vals["reference"] = self.env["ir.sequence"].next_by_code(
                    "equipement.management"
                ) or "Nouveau"

        return super().create(vals_list)

