# Comprehensive Step-by-Step Implementation Guide: Free Self-Hosted Telegram AI & Odoo Lead Automation

> **Target Audience:** Beginner to Intermediate Developers / Integration Engineers  
> **Goal:** Build, deploy, and verify a 100% self-hosted Telegram AI Lead Generation assistant integrated with Odoo CRM using Google Gemini 3.1 Flash-Lite AI.  
> **Key Constraint:** Zero paid middleware subscriptions, fully automated lead extraction into 13 custom Odoo CRM fields with real-time multi-turn conversation memory.

---

## Table of Contents
1. [Architecture Overview & Core Stack](#1-architecture-overview--core-stack)
2. [Phase 1: Environment & Infrastructure Setup](#2-phase-1-environment--infrastructure-setup)
   - [1.1 Software Prerequisites Installation](#11-software-prerequisites-installation)
   - [1.2 Docker & Docker Compose Deployment](#12-docker--docker-compose-deployment)
   - [1.3 Initializing Database Schemas & Knowledge Base](#13-initializing-database-schemas--knowledge-base)
   - [1.4 Google Gemini AI API Key Configuration](#14-google-gemini-ai-api-key-configuration)
3. [Phase 2: Telegram Bot API & Webhook Setup](#3-phase-2-telegram-bot-api--webhook-setup)
   - [2.1 Telegram Bot Creation via BotFather](#21-telegram-bot-creation-via-botfather)
   - [2.2 Obtaining Bot Token & Secret Token](#22-obtaining-bot-token--secret-token)
   - [2.3 Cloudflare Quick Tunnel & Webhook Registration](#23-cloudflare-quick-tunnel--webhook-registration)
4. [Phase 3: Odoo CRM Setup & 13 Custom Fields Configuration](#4-phase-3-odoo-crm-setup--13-custom-fields-configuration)
   - [3.1 Odoo Community Installation & CRM Module Setup](#31-odoo-community-installation--crm-module-setup)
   - [3.2 Creating Required Custom CRM Fields & UI Tab Injection](#32-creating-required-custom-crm-fields--ui-tab-injection)
5. [Phase 4: AI System Prompt & Automated Lead Qualification](#5-phase-4-ai-system-prompt--automated-lead-qualification)
   - [4.1 PostgreSQL Business Knowledge Base](#41-postgresql-business-knowledge-base)
   - [4.2 Structured 1-Question Qualification Flow & JSON Enforcement](#42-structured-1-question-qualification-flow--json-enforcement)
6. [Phase 5: n8n Master Workflow & Native Node Pipeline](#6-phase-5-n8n-master-workflow--native-node-pipeline)
   - [5.1 Importing the Workflow](#51-importing-the-workflow)
   - [5.2 Detailed Node Execution Pipeline](#52-detailed-node-execution-pipeline)
7. [Phase 6: Database Reset & End-to-End Testing Guide](#7-phase-6-database-reset--end-to-end-testing-guide)
   - [6.1 Resetting DB to Clean Initial State](#61-resetting-db-to-clean-initial-state)
   - [6.2 English & Bangla Qualification Test Scenarios](#62-english--bangla-qualification-test-scenarios)
   - [6.3 Human Handoff & High-Intent Triggers](#63-human-handoff--high-intent-triggers)
   - [6.4 Duplicate Webhook Protection & Fallback Verification](#64-duplicate-webhook-protection--fallback-verification)
8. [Phase 7: Maintenance, Backup & Recruiter Deliverables Checklist](#8-phase-7-maintenance-backup--recruiter-deliverables-checklist)
9. [Phase 8: Security Requirements & Production Hardening Guide](#9-phase-8-security-requirements--production-hardening-guide)

---

## 1. Architecture Overview & Core Stack

The system processes incoming Telegram customer messages in real-time on your local machine using the following pipeline:

```
[Customer Telegram] 
       │
       ▼ (Telegram Bot API Webhook)
[Cloudflare Quick Tunnel]
       │
       ▼ (POST Webhook)
[n8n Automation Engine (Docker Container)]
       ├──► [PostgreSQL] (Message History, Idempotency, Contacts & Knowledge)
       ├──► [Google Gemini 3.1 Flash-Lite API] (AI qualification & response generation)
       └──► [Odoo CRM (JSON-RPC)] (Lead Creation & Continuous 13-Field Updates)
```

### Core Technologies
- **OS:** Windows 10/11 or Ubuntu Linux
- **Containers:** Docker Desktop / Docker Compose
- **Automation:** n8n Community Edition (Self-Hosted)
- **AI Engine:** Google Gemini API (`gemini-3.1-flash-lite`)
- **CRM:** Odoo Community Edition 17 (On-Premise)
- **Database:** PostgreSQL 16
- **Public Tunnel:** Cloudflare Quick Tunnel (`cloudflared`)
- **Messaging:** Telegram Bot API (100% Free)

---

## 2. Phase 1: Environment & Infrastructure Setup

### 1.1 Software Prerequisites Installation

1. **Install Docker Desktop (Windows / Linux):**
   - Download Docker Desktop from [docker.com](https://www.docker.com/).
   - Follow standard installer steps and enable WSL2 backend.
   - Verify installation in Terminal / PowerShell:
     ```powershell
     docker --version
     docker compose version
     ```

2. **Install Cloudflared (Cloudflare Tunnel CLI):**
   - Windows: Install via winget:
     ```powershell
     winget install Cloudflare.cloudflared
     ```

---

### 1.2 Docker & Docker Compose Deployment

We provide a complete multi-container setup in `docker-compose.yml`.

1. Open PowerShell or Terminal in the project directory:
   `d:\Job Task\WhatsApp_AI_and_Odoo_Lead_Automation_Task`

2. Create your `.env` configuration file from template:
   ```powershell
   Copy-Item .env.example .env
   ```

   **.env Configuration Reference:**
   ```ini
   # PostgreSQL Settings
   POSTGRES_USER=n8n_user
   POSTGRES_PASSWORD=n8n_password
   POSTGRES_DB=telegram_ai_db

   # n8n Web Admin Credentials
   N8N_USER=admin
   N8N_PASSWORD=SmartSecure12!

   # Public Tunnel URL
   WEBHOOK_URL=https://your-cloudflare-subdomain.trycloudflare.com/

   # Telegram Bot Credentials
   TELEGRAM_BOT_TOKEN=1234565
   TELEGRAM_SECRET_TOKEN=my_secure_telegram

   # Gemini AI Settings
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   GEMINI_MODEL=gemini-3.1-flash-lite
   ENABLE_AI_ASSISTANT=true

   # Odoo CRM Credentials
   ODOO_URL=http://localhost:8069
   ODOO_DB=odoo_db1
   ODOO_USERNAME=admin@example.com
   ODOO_PASSWORD=admin_password
   ```

3. Launch all container services (n8n, PostgreSQL, Odoo, Odoo DB):
   ```powershell
   docker compose up -d
   ```

4. Verify all containers are running (`UP` status):
   ```powershell
   docker compose ps
   ```

   **Service Port Access:**
   - **n8n Web Interface:** [http://localhost:5678](http://localhost:5678)
   - **Odoo CRM Interface:** [http://localhost:8069](http://localhost:8069)
   - **PostgreSQL Database:** `localhost:5432`

---

### 1.3 Initializing Database Schemas & Knowledge Base

The PostgreSQL container runs `init_db.sql` on launch to create core tables:
- `contacts`: Customer profiles, language settings, and AI/human handoff status flags.
- `messages`: Full chat message log (incoming customer & outgoing AI replies).
- `conversations`: Summaries, extracted lead JSON, AI lead scores, and Odoo lead IDs.
- `processed_messages`: Telegram `message_id` tracking for duplicate request prevention.
- `business_knowledge`: Dynamic knowledge base table queried by n8n to feed context into the Gemini API prompt.

To re-run initialization manually:
```powershell
docker exec -i telegram_ai_postgres psql -U n8n_user -d telegram_ai_db < init_db.sql
```

---

### 1.4 Google Gemini AI API Key Configuration

1. Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Place the key in your `.env` file under `GEMINI_API_KEY`.
3. In `n8n_workflow.json`, line 89 uses model `gemini-3.1-flash-lite`:
   `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key=YOUR_GEMINI_API_KEY`

---

## 3. Phase 2: Telegram Bot API & Webhook Setup

### 2.1 Telegram Bot Creation via BotFather

1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` to create a new Telegram Bot.
3. Choose a bot name (e.g., `Apex Enterprise AI Assistant`).
4. Choose a unique username ending in `bot` (e.g., `ApexSalesLead_bot`).

---

### 2.2 Obtaining Bot Token & Secret Token

1. `@BotFather` will provide your Bot Access Token (e.g. `8171082982:AAF7H4hQadyhp...`).
2. Add this token to `.env` under `TELEGRAM_BOT_TOKEN`.
3. Set your custom secret token in `.env` under `TELEGRAM_SECRET_TOKEN`.

---

### 2.3 Cloudflare Quick Tunnel & Webhook Registration

1. Start Cloudflare Quick Tunnel in PowerShell:
   ```powershell
   cloudflared tunnel --url http://localhost:5678
   ```

2. Copy the public tunnel URL (e.g., `https://xxxx.trycloudflare.com`).

3. Register your webhook URL with Telegram via curl:
   ```powershell
   curl.exe -s "https://api.telegram.org/bot8171082982:AAF7H4hQadyhp0wiLwFLKVupMBKRmcplLjw/setWebhook?url=https://xxxx.trycloudflare.com/webhook/telegram&secret_token=my_secure_telegram_secret_token_2026"
   ```

4. Response must return `{"ok":true,"result":true,"description":"Webhook was set"}`.

---

## 4. Phase 3: Odoo CRM Setup & 13 Custom Fields Configuration

### 3.1 Odoo Community Installation & CRM Module Setup

1. Open [http://localhost:8069](http://localhost:8069).
2. Create database:
   - **Database Name:** `odoo_db1`
   - **Email:** `admin@example.com`
   - **Password:** `admin_password`
3. Log in and activate the **CRM** module.

---

### 3.2 Creating Required Custom CRM Fields & UI Tab Injection

Run the included python helper script:
```powershell
python odoo_custom_fields.py
```
*What this script accomplishes:*
1. Connects to Odoo XML-RPC API using credentials from `.env`.
2. Automatically creates all 13 custom fields on the `crm.lead` model.
3. Automatically creates an inherited XML form view (`crm.lead.form.telegram.ai.custom.fields`), adding a dedicated **"Telegram AI Info"** tab to the Odoo Lead Form interface!

#### Summary of 13 Custom CRM Fields Created:

| Field Technical Name | Field Label | Field Type | Purpose |
| :--- | :--- | :--- | :--- |
| `x_telegram_chat_id` | Telegram Chat ID | Char | Unique Telegram Chat identifier |
| `x_telegram_username` | Telegram Username | Char | Telegram handle or full user name |
| `x_telegram_message_id` | Telegram Message ID | Char | Last processed message ID |
| `x_product_interest` | Product Interest | Char | Interested service/product name |
| `x_customer_requirement` | Customer Requirement | Text | Full detailed requirement text |
| `x_customer_budget` | Customer Budget | Char | Budget range (e.g. 10,000 BDT / $500) |
| `x_required_timeline` | Required Timeline | Char | Project deadline/timeline |
| `x_customer_location` | Customer Location | Char | City or country location |
| `x_preferred_contact_time` | Preferred Contact Time | Char | Best time for a follow-up call |
| `x_ai_lead_score` | AI Lead Score | Integer | Lead qualification score (10–95) |
| `x_ai_summary` | AI Summary | Text | Summary generated by Gemini AI |
| `x_handoff_reason` | Handoff Reason | Text | Handoff trigger reason |
| `x_last_message_time` | Last Message Time | Datetime | Timestamp of latest Telegram message |

---

## 5. Phase 4: AI System Prompt & Automated Lead Qualification

### 4.1 PostgreSQL Business Knowledge Base

The system queries PostgreSQL table `business_knowledge` to feed accurate service info into the Gemini API.
You can update facts or pricing directly in database without restarting services:
```sql
INSERT INTO business_knowledge (category, content) VALUES
('company_info', 'Apex Enterprise Solutions specializes in custom Odoo ERP development, Telegram & WhatsApp AI automation, and business process engineering.'),
('pricing_plans', 'Starter Chatbot ($300), Professional Odoo CRM + AI ($800), Enterprise Custom Solution (Custom Quote).');
```

---

### 4.2 Structured 1-Question Qualification Flow & JSON Enforcement

The system prompt configures Gemini 3.1 Flash-Lite to act as a structured **Lead Qualification Specialist**.

#### Automated Question Sequence (Asked ONE at a time):
1. **Service Requirement** — What specific service do you need?
2. **Budget** — "To give you the most accurate proposal, could you share your approximate budget range?"
3. **Timeline** — "What is your preferred timeline or deadline for this project?"
4. **Location** — "May I know your location or country so we can plan accordingly?"
5. **Preferred Contact Time** — "When is the best time for our team to contact you?"
6. **Phone / Email** — Triggers immediate Human Handoff & Lead Ready state.

#### Required Output JSON Format:
```json
{
  "reply": "Thank you! I have noted your budget of 10,000 BDT. What is your preferred timeline for project delivery?",
  "lead_ready": true,
  "human_handoff": false,
  "handoff_reason": "",
  "lead_score": 60,
  "lead": {
    "name": "Bk Bh",
    "chat_id": "7031127239",
    "telegram_username": "Bk Bh",
    "phone": "",
    "email": "",
    "company": "",
    "product_interest": "AI Chatbot",
    "requirement": "24/7 Customer Support AI Chatbot",
    "budget": "10,000 BDT",
    "timeline": "Within 2-4 Weeks",
    "location": "Bangladesh",
    "preferred_contact_time": "Business Hours",
    "notes": ""
  }
}
```

---

## 6. Phase 5: n8n Master Workflow & Native Node Pipeline

### 6.1 Importing the Workflow

1. Open n8n at [http://localhost:5678](http://localhost:5678).
2. Go to **Workflows** → **Import from File**.
3. Select `n8n_workflow.json`.
4. Click **Save** and turn the workflow toggle to **Active (Green)**.

---

### 6.2 Detailed Node Execution Pipeline

```
[Webhook] ──► [Extract & Validate] ──► [IF Valid] ──► [Check Duplicate] ──► [IF Not Processed]
                                                                                  │
[Odoo Write] ◄── [Odoo Search] ◄── [Odoo Auth] ◄── [Build Odoo Payload] ◄── [Load History]
     │                                                                            │
[Done] ◄── [Mark DB Processed] ◄── [Save Log DB] ◄── [Send Telegram] ◄── [Parse AI] ◄── [Gemini AI]
```

| Node Name | Node Type | Purpose / Function |
| :--- | :--- | :--- |
| **Webhook - Incoming Telegram** | `n8n-nodes-base.webhook` | Listens for incoming POST webhooks at `/webhook/telegram`. |
| **Code - Extract & Validate Message Info** | `n8n-nodes-base.code` | Parses Telegram payload, chat ID, username, and message text. |
| **IF - Valid Text Message** | `n8n-nodes-base.if` | Ignores empty messages or non-text content. |
| **DB - Check Duplicate Message** | `n8n-nodes-base.postgres` | Queries `processed_messages` for duplicate `telegram_message_id`. |
| **IF - Not Already Processed** | `n8n-nodes-base.if` | Halts execution if message was already handled. |
| **DB - Load History & Knowledge** | `n8n-nodes-base.postgres` | Queries last 10 messages for conversation continuity. |
| **Code - Prepare Gemini Payload** | `n8n-nodes-base.code` | Builds system prompt and multi-turn message history for Gemini API. |
| **HTTP Request - Gemini AI** | `n8n-nodes-base.httpRequest` | Direct POST request to `gemini-3.1-flash-lite` generateContent endpoint. |
| **Code - Parse AI Response** | `n8n-nodes-base.code` | Parses Gemini JSON reply, extracts lead data & phone regex fallback. |
| **HTTP Request - Send Telegram Reply** | `n8n-nodes-base.httpRequest` | Sends response to customer via Telegram Bot API `sendMessage`. |
| **DB - Save Messages Log** | `n8n-nodes-base.postgres` | Logs incoming message and outgoing AI reply into PostgreSQL `messages`. |
| **DB - Mark Message Processed** | `n8n-nodes-base.postgres` | Inserts `telegram_message_id` into `processed_messages`. |
| **Code - Prepare Odoo Payload** | `n8n-nodes-base.code` | Formats authentication payload for Odoo JSON-RPC API (`common/authenticate`). |
| **HTTP - Odoo Auth** | `n8n-nodes-base.httpRequest` | Obtains session `uid` from Odoo Community instance. |
| **HTTP - Odoo Search Lead** | `n8n-nodes-base.httpRequest` | Searches existing lead by `x_telegram_chat_id` using `crm.lead.search`. |
| **Code - Build Odoo Write Payload** | `n8n-nodes-base.code` | Constructs JSON-RPC parameters for Odoo `create` or `write` call. |
| **HTTP - Odoo Create/Update Lead** | `n8n-nodes-base.httpRequest` | Synchronizes all 13 lead fields into Odoo CRM (`crm.lead`). |

---

## 7. Phase 6: Database Reset & End-to-End Testing Guide

### 7.1 Resetting DB to Clean Initial State

To clear all test history and test from scratch:
```powershell
docker exec -i telegram_ai_postgres psql -U n8n_user -d telegram_ai_db -c "TRUNCATE TABLE messages, processed_messages, conversations, contacts RESTART IDENTITY CASCADE;"
docker exec -i odoo_postgres psql -U odoo -d odoo_db1 -c "DELETE FROM crm_lead;"
```

---

### 7.2 English & Bangla Qualification Test Scenarios

#### Scenario A: English AI Chatbot Lead Qualification
1. **Customer:** "Hi, I need an AI chatbot for 24/7 customer support."
   - *AI Reply:* "Hello! An AI chatbot for 24/7 support is our specialty. To provide an accurate proposal, could you share your approximate budget range?"
2. **Customer:** "My budget is around 10,000 BDT."
   - *AI Reply:* "Thank you! I have noted your budget of 10,000 BDT. What is your preferred timeline or deadline for project completion?"
3. **Customer:** "Within 2-4 weeks. My location is Dhaka, Bangladesh."
   - *AI Reply:* "Great! When is the best time for our team to contact you for a follow-up call?"
4. **Customer:** "01776569120 or bibektotol@gmail.com. Call me during business hours."
   - *AI Reply:* "Thank you Bk Bh! Our senior consultant will reach out to you shortly at 01776569120 during business hours."
   - *Result in Odoo:* Lead updated with **Score 90**, **Phone:** `01776569120`, **Email:** `bibektotol@gmail.com`, **Budget:** `10,000 BDT`, **Timeline:** `Within 2-4 weeks`, **Location:** `Bangladesh`, **Preferred Contact Time:** `Business Hours`.

---

### 7.3 Human Handoff & High-Intent Triggers

1. **High Intent Triggers (`lead_ready = true`):**
   - Customer provides phone number / email OR requests a call / quotation.
2. **Human Handoff Triggers (`human_handoff = true`):**
   - Customer types "agent", "call me", or "talk to representative".
   - *Result:* AI notifies user that a senior consultant will reach out and sets `human_handoff = true` in Odoo lead.

---

### 7.4 Duplicate Webhook Protection & Fallback Verification

1. **Duplicate Message Test:** Resending duplicate message payload produces no double reply.
2. **Fallback Verification:** If Gemini API key is missing or model fails, `Code - Parse AI Response` catches the error and provides a polite multilingual fallback response.

---

## 8. Phase 7: Maintenance, Backup & Recruiter Deliverables Checklist

### 8.1 Automated Database Backup Script

Run the included backup script:
```powershell
.\backup_databases.ps1
```
Exports timestamped `.sql` database dumps to `./backups/` with 30-day retention cleanup.

---

### 8.2 Deliverables Checklist

- [x] `INSTRUCTION.md` (This complete step-by-step implementation guide)
- [x] `docker-compose.yml` (Docker configuration for all 4 containers)
- [x] `.env.example` (Template environment configuration file)
- [x] `init_db.sql` (PostgreSQL schema initialization script)
- [x] `n8n_workflow.json` (Exported n8n workflow with native HTTP Odoo nodes)
- [x] `odoo_custom_fields.py` (Automated XML-RPC script for Odoo custom fields & "Telegram AI Info" tab view creation)
- [x] `backup_databases.ps1` (Automated daily database backup PowerShell script)

---

## 9. Phase 8: Security Requirements & Production Hardening Guide

1. **Token Privacy:** Tokens and passwords are defined in `.env` and excluded from git via `.gitignore`.
2. **Port Security:** Only n8n is exposed to Cloudflare Tunnel (`5678`). Odoo (`8069`) and Postgres (`5432`) remain internal to Docker bridge network.
3. **Secret Token Check:** Telegram secret header `x-telegram-bot-api-secret-token` is validated in `Code - Extract & Validate Message Info`.
4. **Duplicate Protection:** Idempotency enforced via PostgreSQL `processed_messages`.

---
*Created for Job Applicant Submission — Self-Hosted Telegram AI & Odoo Lead Automation.*
