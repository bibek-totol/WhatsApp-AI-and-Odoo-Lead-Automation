#!/usr/bin/env python3
"""
Odoo Custom Fields Creator & Lead Automator Helper Script
Creates required custom fields on the `crm.lead` model in Odoo Community Edition via XML-RPC.
"""

import os
import xmlrpc.client

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

missing_env = [var for var, val in [("ODOO_URL", ODOO_URL), ("ODOO_DB", ODOO_DB), ("ODOO_USERNAME", ODOO_USERNAME), ("ODOO_PASSWORD", ODOO_PASSWORD)] if not val]
if missing_env:
    raise EnvironmentError(f"Missing required environment variables in .env file: {', '.join(missing_env)}")

def main():
    print(f"Connecting to Odoo at {ODOO_URL} (DB: {ODOO_DB})...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    
    if not uid:
        print("ERROR: Authentication failed! Please check credentials.")
        return

    print(f"Authenticated successfully! User ID: {uid}")
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

   
    model_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.model', 'search', [[['model', '=', 'crm.lead']]])
    if not model_ids:
        print("ERROR: Could not find 'crm.lead' model in Odoo. Is CRM module installed?")
        return
    model_id = model_ids[0]

  
    custom_fields = [
        {"name": "x_telegram_chat_id", "field_description": "Telegram Chat ID", "ttype": "char"},
        {"name": "x_telegram_username", "field_description": "Telegram Username", "ttype": "char"},
        {"name": "x_telegram_message_id", "field_description": "Telegram Message ID", "ttype": "char"},
        {"name": "x_product_interest", "field_description": "Product Interest", "ttype": "char"},
        {"name": "x_customer_requirement", "field_description": "Customer Requirement", "ttype": "text"},
        {"name": "x_customer_budget", "field_description": "Customer Budget", "ttype": "char"},
        {"name": "x_required_timeline", "field_description": "Required Timeline", "ttype": "char"},
        {"name": "x_customer_location", "field_description": "Customer Location", "ttype": "char"},
        {"name": "x_preferred_contact_time", "field_description": "Preferred Contact Time", "ttype": "char"},
        {"name": "x_ai_lead_score", "field_description": "AI Lead Score", "ttype": "integer"},
        {"name": "x_ai_summary", "field_description": "AI Summary", "ttype": "text"},
        {"name": "x_handoff_reason", "field_description": "Handoff Reason", "ttype": "text"},
        {"name": "x_last_message_time", "field_description": "Last Message Time", "ttype": "datetime"},
    ]

    for field in custom_fields:
        existing = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD, 'ir.model.fields', 'search',
            [[['model_id', '=', model_id], ['name', '=', field["name"]]]]
        )
        if existing:
            print(f"Field {field['name']} already exists. Skipping.")
        else:
            field_data = {
                'name': field['name'],
                'field_description': field['field_description'],
                'model_id': model_id,
                'ttype': field['ttype'],
                'state': 'manual'
            }
            new_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.model.fields', 'create', [field_data])
            print(f"Created custom field {field['name']} (ID: {new_id})")

    print("All custom CRM fields processed successfully!")

if __name__ == "__main__":
    main()
