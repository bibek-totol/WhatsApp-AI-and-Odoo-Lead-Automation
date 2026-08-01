# Comprehensive Step-by-Step Implementation Guide: Free Self-Hosted Telegram AI & Odoo Lead Automation

> **Target Audience:** Beginner to Intermediate Developers / Integration Engineers  
> **Goal:** Build, deploy, and verify a 100% self-hosted Telegram AI Lead Generation assistant integrated with Odoo CRM using Google Gemini 3.1 Flash-Lite AI.  
> **Key Constraint:** Zero paid middleware subscriptions, fully automated lead extraction into 13 custom Odoo CRM fields with real-time multi-turn conversation memory.

> [!CAUTION]
> **⚠️ Production Limitations — Read Before Deploying**  
> This system is designed and validated as a **self-hosted MVP for local/testing use**. Several architectural constraints will directly cause failures or degraded service in a real production environment. Key pain points include: no uptime guarantee (host-PC dependency), ephemeral Cloudflare tunnel URLs that break after every restart, Google Gemini free-tier rate limits under concurrent load, text-only message processing (no media/voice support) and no direct in-Odoo reply-to-Telegram capability after human handoff.  

> See [Section 10: Production Limitations & Known Gaps](#10-phase-9-production-limitations--known-gaps) for the full breakdown with recommended upgrades.

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
10. [Phase 9: Production Limitations & Known Gaps](#10-phase-9-production-limitations--known-gaps)

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

### 3.2 Custom Addon Module (`custom_addons/ai_lead`) & UI Tab Injection

The 13 custom fields and the CRM GUI layout are managed natively via the custom Odoo module `ai_lead` located in `custom_addons/ai_lead`.

#### How `custom_addons/ai_lead` Works:
1. **Directory Mounting:** The `custom_addons` directory is automatically mounted to `/mnt/extra-addons` inside the Odoo Docker container via `docker-compose.yml`.
2. **Model Field Definition (`models/crm_lead.py`):** Inherits `crm.lead` and defines all 13 custom fields (`x_telegram_chat_id`, `x_telegram_username`, `x_customer_budget`, etc.).
3. **Form View Inheriting (`views/crm_lead_views.xml`):** Automatically injects a dedicated **"Telegram AI Info"** tab into the Odoo CRM Lead Form layout.

#### Activating the `ai_lead` Module in Odoo:
1. Go to **Settings** → Scroll down and click **Activate Developer Mode**.
2. Go to **Apps** menu → Click **Update Apps List** in the top navigation bar.
3. Remove the default `Apps` search filter, type `AI Lead Automation` or `ai_lead`, and click **Search**.
4. Click **Activate** on the **AI Lead Automation** module.

#### Summary of 13 Custom CRM Fields Created by `ai_lead`:

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
- [x] `custom_addons/ai_lead` (Custom Odoo addon module with models, fields, & XML views)
- [x] `backup_databases.ps1` (Automated daily database backup PowerShell script)

---

## 9. Phase 8: Security Requirements & Production Hardening Guide

1. **Token Privacy:** Tokens and passwords are defined in `.env` and excluded from git via `.gitignore`.
2. **Port Security:** Only n8n is exposed to Cloudflare Tunnel (`5678`). Odoo (`8069`) and Postgres (`5432`) remain internal to Docker bridge network.
3. **Secret Token Check:** Telegram secret header `x-telegram-bot-api-secret-token` is validated in `Code - Extract & Validate Message Info`.
4. **Duplicate Protection:** Idempotency enforced via PostgreSQL `processed_messages`.

---

## 10. Phase 9: Production Limitations & Known Gaps

> [!CAUTION]
> The following limitations are **not theoretical** — they will directly cause service interruptions, data loss, or poor user experience if this system is promoted to a real production environment without the recommended mitigations.

---

### 10.1 🔴 Zero Uptime Guarantee — Host PC Dependency

**Severity: Critical**

The entire system runs on Docker Desktop installed on a local Windows PC. If the machine:
- Is **shut down or restarted** (e.g., Windows Update)
- Goes into **sleep or hibernate mode**
- Suffers a **hardware failure or power cut**

...the chatbot becomes completely unavailable. Telegram will queue incoming messages for up to ~5 minutes before dropping them, meaning customers receive **no response and no error notice**.

| What Breaks | Impact |
|:---|:---|
| n8n webhook stops accepting requests | All incoming Telegram messages are silently lost |
| PostgreSQL database goes offline | Conversation history and idempotency checks fail |
| Odoo CRM goes offline | Lead sync fails silently — n8n error log only |

**Recommended Fix:** Deploy all Docker containers on a VPS/cloud VM (e.g., DigitalOcean, Hetzner, AWS EC2) with a process manager (`systemd` or Docker `restart: always`) and server uptime monitoring.

---

### 10.2 🔴 Cloudflare Quick Tunnel — Not Production-Grade

**Severity: Critical**

The Cloudflare Quick Tunnel (`cloudflared tunnel --url http://localhost:5678`) used to expose the n8n webhook to Telegram has fundamental production flaws:

- **New random subdomain on every restart** — Every time the tunnel command is run, Cloudflare assigns a different `xxxx.trycloudflare.com` URL. You must manually re-run `setWebhook` with the new URL each time or messages stop arriving.
- **No uptime SLA** — Quick Tunnels are Cloudflare's free, ephemeral, best-effort service. Cloudflare can terminate the tunnel at any time without notice.
- **Single point of failure** — There is no failover tunnel or health-check mechanism.

**Recommended Fix:** Register a **Cloudflare Named Tunnel** tied to a custom domain (free with Cloudflare account), OR use a reverse proxy (nginx + Let's Encrypt SSL) on a VPS with a static IP address. This provides a static, permanent webhook URL.

```bash
# Example: Named Tunnel setup (stable URL)
cloudflared tunnel create my-bot-tunnel
cloudflared tunnel route dns my-bot-tunnel bot.yourdomain.com
cloudflared tunnel run my-bot-tunnel
```

---

### 10.3 🟠 Google Gemini Free Tier — Rate Limits Under Load

**Severity: High**

The system uses the **Google AI Studio free tier** for `gemini-3.1-flash-lite`. This tier enforces strict rate limits:

| Limit Type | Free Tier Threshold |
|:---|:---|
| Requests Per Minute (RPM) | 15 RPM |
| Tokens Per Day (TPD) | 1,000,000 tokens/day |
| Requests Per Day (RPD) | 1,500 requests/day |

**Production Impact:** If more than ~10–12 customers chat simultaneously, requests will receive HTTP `429 Too Many Requests` errors. The n8n `Code - Parse AI Response` node catches this and sends the polite fallback message — but the customer receives **no intelligent reply and loses context**.

**Recommended Fix:** Upgrade to a **Google AI Studio paid tier** (pay-per-use) or switch to direct **Vertex AI** for enterprise-grade rate limits. Add exponential backoff retry logic inside `Code - Prepare Gemini Payload`.

---

### 10.4 🟠 Text-Only Message Processing — No Media Support

**Severity: High**

The `IF - Valid Text Message` node ignores everything that is not a plain text `message.text`. The following Telegram message types are **silently dropped** with no response to the customer:

- 📷 Photos and images
- 🎤 Voice messages and audio clips
- 📹 Video notes
- 📁 Documents and PDF files
- 📍 Location pins
- 🖼️ Stickers and GIFs
- ✍️ Forwarded messages (when original sender info conflicts)

**Production Impact:** A customer who sends a photo of their requirement document, a voice note explaining their project, or shares their location receives **absolute silence** — indistinguishable from a broken bot.

**Recommended Fix:** Add a handler node after `IF - Valid Text Message` for the `false` branch that sends a polite auto-reply: *"I can only process text messages. Please type your question or requirement."*


---

### 10.5 🟡 Human Handoff — No In-Odoo Reply Capability

**Severity: Medium**

When `human_handoff = true`, the AI stops responding and the Odoo lead is flagged. However, the sales agent **cannot reply to the customer directly from within Odoo CRM**. There is no Telegram ↔ Odoo Discuss channel bridge. The agent must:
1. Leave Odoo
2. Open Telegram manually (or Telegram Web)
3. Find the customer's chat thread
4. Type a reply manually

**Production Impact:** Response latency increases significantly. Agent workflow is broken across two separate tools, causing missed follow-ups and poor customer experience.

**Recommended Fix:** Integrate an Odoo partner channel module or build a simple n8n sub-workflow that polls a designated Odoo note/chatter field and relays its content to the customer's Telegram `chat_id` via the Bot API `sendMessage` endpoint.

---


### 10.6 🟡 No End-to-End Error Alerting

**Severity: Medium**

When n8n workflow nodes fail (e.g., Gemini API 429, Odoo offline, PostgreSQL timeout), errors are logged to the n8n execution history UI only. There is:

- No email alert to the system administrator
- No Telegram message to a designated admin chat
- No SMS or PagerDuty notification
- No automatic retry mechanism for failed Odoo sync attempts

**Production Impact:** Failures can go unnoticed for hours. Failed lead syncs mean CRM data is incomplete with no recovery mechanism.

**Recommended Fix:** Add an n8n **Error Workflow** (`Settings > Error Workflow`) that sends a Telegram message to an admin `chat_id` containing the failed node name, error message, and timestamp.

---


*Created for Job Applicant Submission — Self-Hosted Telegram AI & Odoo Lead Automation.*
