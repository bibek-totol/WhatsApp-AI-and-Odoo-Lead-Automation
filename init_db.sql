

-- 1. Contacts Table (Customer Profile & State)
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(30) UNIQUE NOT NULL,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    company VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    ai_enabled BOOLEAN DEFAULT true,
    human_handoff BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Messages Table (Chat History Log)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    whatsapp_message_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(30) NOT NULL,
    direction VARCHAR(10) CHECK (direction IN ('incoming', 'outgoing')),
    message_text TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Conversations Table (Lead State & Summary)
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(30) NOT NULL,
    conversation_summary TEXT,
    collected_lead_data JSONB DEFAULT '{}'::jsonb,
    lead_score INT DEFAULT 0,
    odoo_lead_id INT,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

-- 4. Processed Messages Table (Idempotency & Webhook Deduplication)
CREATE TABLE IF NOT EXISTS processed_messages (
    whatsapp_message_id VARCHAR(255) PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Business Knowledge Base Table (Self-Hosted Knowledge Source)
CREATE TABLE IF NOT EXISTS business_knowledge (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Expanded Sample Business Knowledge
INSERT INTO business_knowledge (category, content) VALUES
('company_info', 'Apex Enterprise Solutions is a premier technology consulting firm specializing in Odoo ERP customization, CRM optimization, and self-hosted WhatsApp AI lead automation.'),
('contact_details', 'Contact us via Email: support@apexsolutions.com, Phone/WhatsApp: +1-555-0199, Website: https://apexsolutions.example.com. Headquarters: Tech Park Tower, Suite 400.'),
('services_odoo', 'Odoo ERP Services: Odoo Community & Enterprise deployment, custom module development, XML-RPC / REST API integrations, CRM workflow setup, and automated lead scoring ($500 - $2,500).'),
('services_whatsapp_ai', 'WhatsApp AI Automation: Custom n8n workflow integration, Meta WhatsApp Cloud API setup, local LLM/Ollama integration, intent classification, lead qualification, and automated CRM sync ($300 - $1,200).'),
('services_enterprise', 'Full Enterprise Automation Package: End-to-end integration including Odoo CRM, PostgreSQL database logging, human agent handoff system, custom dashboards, and 24/7 self-hosted AI chatbot ($2,000+).'),
('pricing_plans', 'Pricing Plans: 1. Starter AI Chatbot ($300 one-time), 2. Professional Odoo CRM + WhatsApp AI ($800 one-time), 3. Enterprise Custom Solution (Custom Quote upon consultation).'),
('faq_business_hours', 'Business Hours: Sunday through Thursday, 9:00 AM to 6:00 PM (GMT+6). Emergency technical support for Enterprise clients is available 24/7.'),
('faq_implementation_time', 'Implementation Timeline: Standard WhatsApp AI + Odoo lead automation deployment takes 3 to 7 business days. Complex enterprise customizations take 2 to 4 weeks.'),
('faq_languages', 'Multilingual Support: Our AI chatbot natively supports English, Spanish, French, German, Arabic, Bengali, and Hindi with automatic language detection.'),
('policies_support', 'Support Policy: All packages include 30 days of free post-deployment technical support, bug fixes, and workflow optimization.'),
('policies_payment', 'Payment Terms: 50% initial deposit prior to project initiation, and 50% final payment upon successful deployment and UAT acceptance.'),
('human_handoff_policy', 'Human Agent Handoff: Customers can request to speak with a human agent anytime by typing "agent", "human", or "support". The AI automatically flags the conversation for manual takeover.'),
('data_privacy', 'Data Privacy & Security: All customer data and chat histories are stored securely in self-hosted PostgreSQL databases. We do not sell or share third-party user data.');

-- Create Indexes for Faster Queries
CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone_number);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_number);
