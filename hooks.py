import logging
from odoo import api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Create email template after module installation."""
    try:
        # Utiliser l'ID de l'utilisateur système
        uid = 1  # __system__ user
        env = api.Environment(cr, uid, {})

        # Get model
        model = env['ir.model']._get('intervention.management')

        # Check if template exists
        template = env['mail.template'].search([
            ('model_id', '=', model.id),
            ('name', '=', 'Affectation Intervention Technicien')
        ])

        if not template:
            template_vals = {
                'name': 'Affectation Intervention Technicien',
                'model_id': model.id,
                'subject': 'Nouvelle intervention : ${object.reference}',
                'email_from': '${user.email_formatted}',
                'email_to': '${object.technicien_id.email}',
                'body_html': """
                    <p>Bonjour ${object.technicien_id.name},</p>
                    <p>Une nouvelle intervention vous a été affectée.</p>
                    <p>Référence : ${object.reference}</p>
                    <p>Client : ${object.client_id.name}</p>
                    <p>Equipement : ${object.equipement_id.name}</p>
                    <p>Cordialement.</p>
                """,
            }
            env['mail.template'].create(template_vals)
            cr.commit()
            _logger.info("✅ Template email créé avec succès !")
        else:
            _logger.info("ℹ️ Template email existe déjà")

    except Exception as e:
        _logger.error(f"❌ Erreur lors de la création du template: {e}")


