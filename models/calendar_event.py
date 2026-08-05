from odoo import models,fields


class CalendarEvent(models.Model):
    _inherit = "calendar.event"


    intervention_id=fields.Many2one("intervention.management",string="Intervention",ondelete="cascade")
    technicien_id=fields.Many2one("technicien.management",string="Technicien")
    client_id=fields.Many2one("res.partner",string="Client")
    calendar_event_ids=fields.One2many("calendar.event","intervention_id",string="Evenements")


def action_planifier(self):
    for intervention in self:
        event = self.env["calendar.event"].create({
            "name": intervention.name,
            "start": intervention.start_date,
            "end": intervention.end_date,
            "stop": fields.Datetime.add(intervention.date_creation_intervention,hours=2),
            "intervention_id": intervention.id,
            "technicien_id": intervention.technicien_id.id,
            "client_id": intervention.client_id.id,
        })
        intervention.calendar_event_id=event.id
