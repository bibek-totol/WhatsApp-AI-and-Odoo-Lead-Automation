from odoo import models, fields  # type: ignore

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_telegram_chat_id = fields.Char(string='Telegram Chat ID')
    x_telegram_username = fields.Char(string='Telegram Username')
    x_telegram_message_id = fields.Char(string='Telegram Message ID')
    x_product_interest = fields.Char(string='Product Interest')
    x_customer_requirement = fields.Text(string='Customer Requirement')
    x_customer_budget = fields.Char(string='Customer Budget')
    x_required_timeline = fields.Char(string='Required Timeline')
    x_customer_location = fields.Char(string='Customer Location')
    x_preferred_contact_time = fields.Char(string='Preferred Contact Time')
    x_ai_lead_score = fields.Integer(string='AI Lead Score')
    x_ai_summary = fields.Text(string='AI Summary')
    x_handoff_reason = fields.Text(string='Handoff Reason')
    x_last_message_time = fields.Datetime(string='Last Message Time')
