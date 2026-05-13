# 💳 Finance Credit Follow-Up Email Agent

An AI-powered finance automation system that generates intelligent payment reminder emails based on invoice overdue stages.

Built using **Python**, **Pandas**, and **Anthropic Claude AI** with secure prompt handling, audit logging, escalation workflows, and dry-run email simulation.

---

# 🚀 Project Overview

Managing overdue invoices manually is repetitive, time-consuming, and error-prone.

This project automates the complete credit follow-up workflow by:

- analyzing invoice overdue duration
- determining escalation stages
- generating professional AI-powered follow-up emails
- maintaining audit logs
- protecting against prompt injection attacks
- supporting secure dry-run execution

The system simulates how modern finance teams automate receivable collection workflows using AI.

---

# ✨ Features

## 📌 Intelligent Multi-Stage Follow-Ups

The system automatically categorizes invoices into escalation stages:

| Stage | Days Overdue | Tone |
|---|---|---|
| Stage 1 | 1–7 days | Friendly reminder |
| Stage 2 | 8–14 days | Polite but firm |
| Stage 3 | 15–21 days | Formal warning |
| Stage 4 | 22–30 days | Final notice |
| Stage 5 | 30+ days | Escalation to finance/legal |

---

## 🤖 AI Email Generation

Uses **Claude Sonnet 4** to generate:

- professional subject lines
- personalized payment reminders
- escalation-stage specific messaging
- structured business communication

---

## 🛡 Prompt Injection Protection

The system sanitizes invoice fields before sending prompts to the LLM.

Protection includes detection of:

- instruction override attempts
- script injection
- jailbreak patterns
- malicious prompt manipulation

---

## 📋 Audit Logging

Every action is logged securely:

- invoice details
- escalation stage
- generated subject line
- timestamps
- dry-run/live status
- escalation events

---

## 🔒 Dry-Run Safety Mode

By default:

- emails are NOT actually sent
- the system safely simulates delivery
- ideal for testing and demos

---

## 📂 Output Generation

Generated emails are automatically stored inside:

```text
output/
```

Each invoice creates its own email output file.

---

# 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core backend logic |
| Pandas | Invoice data processing |
| Anthropic Claude API | AI email generation |
| python-dotenv | Environment variable management |
| JSON | Audit logging |
| Logging Module | Runtime logging |

---

# 📁 Project Structure


```text
finance-followup-agent/
│
├── .env.example
├── .gitignore
├── README.md
├── agent.py
├── demo.py
├── invoices.csv
└── requirements.txt
```


---

# ⚙ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/Anchita29Sharma/finance-followup-agent.git
```

---

## 2️⃣ Move into Project Folder

```bash
cd finance-followup-agent
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Setup

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_api_key_here
DRY_RUN=true
```

---

# ▶ Running the Project

## Demo Mode (No API Required)

```bash
python demo.py
```

Runs a fully simulated workflow with mock-generated emails.

---

## AI Agent Mode

```bash
python agent.py
```

Uses Claude AI to generate real finance follow-up emails.

---

# 📊 Example Workflow

## Input Invoice

```csv
invoice_no,company,amount,due_date
INV-2024-001,Sharma Enterprises,45000,2026-05-01
```

---

## Generated Output

```text
Subject: Payment Reminder - Invoice #INV-2024-001

Dear Client,

This is a friendly reminder regarding your pending invoice...
```

---

# 🧠 AI Prompt Engineering

The project uses:

- strict system prompts
- controlled user prompts
- structured output formatting
- tone-based escalation logic

This ensures:

- professional consistency
- reduced hallucination
- safe enterprise-style responses

---

# 🔒 Security Considerations

## Prompt Injection Protection

The agent sanitizes all user-controlled invoice fields before they are inserted into prompts.

Blocked patterns include:

- `ignore previous instructions`
- `system prompt`
- `act as`
- HTML/script injection
- markdown/code block injection

---

## Hallucination Risk

The system prompt explicitly restricts the model from inventing:
- payment details
- invoice numbers
- dates
- discounts
- legal threats

Only provided invoice data is allowed in responses.

---

## Unauthorised Access

The project currently runs as a local CLI application.

If converted into an API service:
- API key authentication
- rate limiting
- HTTPS
- request validation

should be added before deployment.

---

## Email Spoofing Protection

If live email sending is enabled:
- SPF
- DKIM
- DMARC

should be configured for the sender domain.

The system defaults to `DRY_RUN=true` to prevent accidental email delivery during development.

---

# 📌 Deliverables Checklist

- [x] GitHub repository with complete source code
- [x] `.env.example`
- [x] `requirements.txt`
- [x] `README.md`
- [x] AI-powered follow-up generation
- [x] Escalation workflow
- [x] Dry-run email simulation
- [x] Audit logging system
- [x] Security mitigations documented
- [x] Demo workflow included

---

# ▶ Running the Demo

```bash
python demo.py
```

This generates all follow-up stages using mock invoice data.

Generated email files will automatically be created inside:

```text
output/
```

Audit logs will automatically be created inside:

```text
logs/
```

No API key is required for demo mode.
# 🔄 Agent Flow Diagram

```text
CSV/Excel
    │
    ▼
load_invoices()
    │
    ▼
compute_days_overdue()
    │
    ▼
get_stage()
    │
    ├── stage 0 → skip
    │
    ├── stage 1–4
    │       │
    │       ▼
    │ sanitise()
    │       │
    │       ▼
    │ generate_email()
    │       │
    │       ▼
    │ send_email()
    │       │
    │       ▼
    │ log_to_audit()
    │
    └── stage 5
            │
            ▼
      Escalation flag
```

---

# 🎯 Use Cases

- Finance departments
- Accounts receivable teams
- Credit collection workflows
- Invoice reminder automation
- AI-powered business communication systems

---

# 🚀 Future Improvements

- SMTP email integration
- Web dashboard
- Analytics panel
- Database integration
- PDF invoice attachment support
- Multi-language support
- Admin portal

---

# 👩‍💻 Author

### Anchita Sharma

Computer Science student passionate about:

- AI systems
- Cybersecurity
- Automation
- Practical backend development

GitHub:
https://github.com/Anchita29Sharma

---

# ⭐ Project Highlights

This project demonstrates:

- AI integration in business workflows
- secure backend automation
- prompt engineering
- audit logging systems
- escalation workflow design
- production-style Python architecture

---

# 📄 License

This project is built for educational and internship evaluation purposes.
