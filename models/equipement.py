from odoo import models, fields

class Equipement(models.Model):
    _name = "equipement.management"
    _description = "Équipement"

    name = fields.Char(string="Nom", required=True)
    reference = fields.Char(string="Référence", required=True)
    serial_number = fields.Char(string="Numéro de série")

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

    def _compute_intervention_count(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)