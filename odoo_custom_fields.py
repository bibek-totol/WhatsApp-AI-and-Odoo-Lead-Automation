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

ODOO_URL = os.getenv("ODOO_URL", "").rstrip("/")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

missing_env = [var for var, val in [("ODOO_URL", ODOO_URL), ("ODOO_DB", ODOO_DB), ("ODOO_USERNAME", ODOO_USERNAME), ("ODOO_PASSWORD", ODOO_PASSWORD)] if not val]
if missing_env:
    raise EnvironmentError(f"Missing required environment variables in .env file: {', '.join(missing_env)}")

def main():
    print(f"Connecting to Odoo at {ODOO_URL} (DB: {ODOO_DB})...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    try:
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    except Exception as err:
        print(f"ERROR: Could not connect to Odoo server at {ODOO_URL}: {err}")
        return

    if not uid:
        print(f"ERROR: Authentication failed for user '{ODOO_USERNAME}' on database '{ODOO_DB}'!")
        print("Please ensure Odoo CRM is running on port 8069 and the database name matches your Odoo database.")
        return
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

    # Now create or update the Form View inheritance so fields are visible on the Lead Form in Odoo UI
    print("Updating Odoo Lead Form View layout to display custom fields...")
    view_name = "crm.lead.form.telegram.ai.custom.fields"
    existing_views = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search',
        [[['name', '=', view_name]]]
    )

    view_arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//notebook" position="inside">
        <page string="Telegram AI Info">
            <group>
                <group string="Telegram Profile">
                    <field name="x_telegram_chat_id"/>
                    <field name="x_telegram_username"/>
                    <field name="x_telegram_message_id"/>
                    <field name="x_last_message_time"/>
                </group>
                <group string="AI Qualification">
                    <field name="x_ai_lead_score"/>
                    <field name="x_product_interest"/>
                    <field name="x_customer_budget"/>
                    <field name="x_required_timeline"/>
                    <field name="x_customer_location"/>
                    <field name="x_preferred_contact_time"/>
                </group>
            </group>
            <group string="Requirements &amp; AI Summary">
                <field name="x_customer_requirement"/>
                <field name="x_ai_summary"/>
                <field name="x_handoff_reason"/>
            </group>
        </page>
    </xpath>
</data>"""

    # Get parent view ID for crm.crm_lead_view_form
    parent_view_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search',
        [[['key', '=', 'crm.crm_lead_view_form']]]
    )
    if not parent_view_ids:
        parent_view_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search',
            [[['model', '=', 'crm.lead'], ['type', '=', 'form']]]
        )

    if parent_view_ids:
        parent_id = parent_view_ids[0]
        if existing_views:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write',
                [existing_views, {'arch': view_arch}]
            )
            print("Successfully updated Lead Form View in Odoo!")
        else:
            view_data = {
                'name': view_name,
                'model': 'crm.lead',
                'inherit_id': parent_id,
                'arch': view_arch,
                'priority': 99
            }
            v_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'create', [view_data])
            print(f"Successfully created Lead Form View tab (View ID: {v_id})!")
    else:
        print("Warning: Could not locate parent lead form view to auto-inject layout.")

    print("All custom CRM fields and Form View layout processed successfully!")

if __name__ == "__main__":
    main()

