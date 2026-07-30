{
    'name': 'AI Lead Automation',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Telegram AI Automation & Custom CRM Fields for Lead Management',
    'description': """
        Custom Odoo Module for Telegram AI Lead Automation.
        Adds custom qualification fields, AI lead score, and AI summary tab to CRM Leads.
    """,
    'author': 'Apex Enterprise Solutions',
    'depends': ['crm'],
    'data': [
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
