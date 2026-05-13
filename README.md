# Finance Credit Follow-Up Email Agent

AI agent that automates payment follow-up emails for overdue invoices. Reads pending credit records, figures out how overdue each one is, and generates a personalised email at the right tone for that stage — or flags it for human review if it's gone past 30 days.

Built for the AI Enablement Internship — Task 2.

---

## What it does

- Ingests invoice data from CSV or Excel
- Computes days overdue automatically from today's date
- Routes each invoice to the correct escalation stage (1–4, or legal flag)
- Calls Claude to generate a personalised email with all invoice fields populated
- Logs every action to an audit trail (with PII masked)
- Saves each generated email as a text file
- Defaults to dry-run mode — nothing actually sends unless you explicitly flip the flag

---

## Escalation stages

| Stage | Trigger | Tone |
|-------|---------|------|
| 1 | 1–7 days overdue | Warm, friendly |
| 2 | 8–14 days overdue | Polite but firm |
| 3 | 15–21 days overdue | Formal, serious |
| 4 | 22–30 days overdue | Stern, final notice |
| Escalation | 30+ days | No email — flagged for legal/finance |

---

## Project structure

```
finance-agent/
├── agent.py            # Main agent — run this with your API key
├── demo.py             # Demo with mock data — no API key needed
├── data/
│   └── invoices.csv    # Sample invoice data
├── output/             # Generated emails saved here (gitignored)
├── logs/
│   ├── agent.log       # Console log
│   └── audit_log.json  # Full audit trail
├── .env.example        # Copy to .env and add your key
├── .gitignore
└── requirements.txt
```

---

## Setup

```bash
git clone <your-repo-url>
cd finance-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run demo (no API key needed)
python demo.py

# Run the actual agent
python agent.py

# Point to a different invoice file
python agent.py data/my_invoices.xlsx
```

---

## CSV format

Your invoice file needs these columns:

| Column | Description |
|--------|-------------|
| `invoice_no` | Unique invoice ID |
| `client_name` | First name (used in casual emails) |
| `client_formal_name` | Formal name e.g. "Mr. Sharma" |
| `company` | Company name |
| `amount` | Amount due (numeric) |
| `currency` | e.g. INR, USD |
| `due_date` | YYYY-MM-DD format |
| `contact_email` | Debtor's email |
| `follow_up_count` | How many follow-ups already sent |
| `payment_link` | Direct payment URL |
| `finance_contact` | Your finance team's email |

---

## Technical Stack & Decision Log

### LLM: Claude claude-sonnet-4-20250514 (Anthropic)

Chose Sonnet over GPT-4o for a few reasons. First, the structured output behaviour is more consistent — the SUBJECT/BODY format held up across all test runs without needing retry logic. Second, cost: Sonnet is cheaper per token than GPT-4o for the same quality on a text-generation task like this. Third, I'm already using the Anthropic SDK which keeps the dependency footprint small.

Alternatives considered: GPT-4o would also work well here. Gemini 1.5 Flash is the cheapest option but tone adherence was less reliable in informal testing. Llama 3 local would eliminate API costs and data-privacy concerns entirely — worth considering for a production deployment.

### Agent Framework: None (intentional)

Task 2 doesn't need a full agent framework like LangChain or CrewAI. Those frameworks add value when you need multi-step reasoning loops, tool use, or multiple agents collaborating. Here the logic is:

1. Load data
2. Compute days overdue
3. Pick a stage
4. Generate email
5. Log it

That's a pipeline, not an agent loop. Adding LangChain here would mean importing a heavy dependency to do what five functions already do clearly. The code is easier to read, test, and debug without it.

If this were extended (e.g. agent autonomously checking payment status via bank API, then deciding whether to send), a framework would make sense.

### Prompt design

Two-part prompt: a system prompt that locks the LLM to email-only output with a fixed SUBJECT/BODY format, and a user prompt that injects all invoice data plus the stage context.

The system prompt is deliberately restrictive — it tells the model exactly what it can and can't do (no discounts, no legal threats except stage 4, no generic emails). This reduces hallucination risk significantly.

The user prompt uses f-strings with explicit field labels rather than passing raw CSV values. This makes injection harder because each field has a declared purpose before the value appears.

---

## Security mitigations

### Prompt injection

All CSV field values are passed through `sanitise()` before going into the prompt. The function checks for known injection patterns (`ignore previous instructions`, `act as`, `system prompt`, etc.) and raises a `ValueError` to skip the record rather than process it. HTML tags are stripped as well.

The system prompt is structured and restrictive — it tells the model it only writes emails and specifies the exact output format. An injection attempt in a client name field would land inside a tightly scoped context with a fixed job description, which limits what it could do even if it got through.

### Data privacy / PII

Emails (the most sensitive field) are masked in all log output using `mask_email()` — `rajesh@sharmaent.com` becomes `ra***@sharmaent.com`. The audit log stores masked emails only, never full addresses.

Invoice data goes to the Anthropic API. For a production deployment where PII cannot leave your network, the right call is to either use a locally hosted model (Llama 3 via Ollama) or strip personally identifying fields before the API call and re-inject them after generation.

### API key handling

Key lives in `.env` only. `.env` is in `.gitignore`. The code loads it with `python-dotenv` and never references it directly. `.env.example` shows the structure with a placeholder value.

### Hallucination risk

The system prompt bans the model from inventing information. The user prompt provides all required fields explicitly. Pydantic validation wasn't added here (the output format is simple enough to parse with basic string splits), but for a production system, wrapping the output in a Pydantic model and retrying on parse failure would be the next step.

### Unauthorised access

The agent currently runs as a CLI script — no exposed HTTP endpoint. If you add a FastAPI wrapper, add API key authentication and rate limiting before exposing it.

### Email spoofing (if live sending is enabled)

Configure SPF, DKIM, and DMARC for your sender domain. Use a verified sender address in your SMTP/SendGrid config. The agent defaults to dry-run mode precisely to prevent accidental sends during development — flip `DRY_RUN=false` only when you've verified your sender setup.

---

## Deliverables checklist

- [x] GitHub repo with source code, `.env.example`, `requirements.txt`, `README.md`
- [x] Agent flow: data ingestion → escalation logic → LLM generation → dry-run send → audit log
- [x] Sample outputs in `output/` (run `demo.py`)
- [x] Audit trail in `logs/audit_log.json`
- [x] Security mitigations documented above
- [x] LLM choice justified
- [x] Framework choice justified (and why none was the right call here)

---

## Running the demo

```bash
python demo.py
```

This generates all 5 stages of emails (stages 1–4 + escalation flag) using mock data, no API key needed. Output files land in `output/`, audit log in `logs/`.

---

## Agent flow diagram

```
CSV/Excel
    │
    ▼
load_invoices()
    │  validate columns, parse dates
    ▼
compute_days_overdue()
    │
    ▼
get_stage()
    │
    ├── stage 0 (not overdue) ────────────► skip
    │
    ├── stage 1–4 ──► sanitise() ──► generate_email() ──► send_email()
    │                                      │                    │
    │                               Claude API call         dry-run log
    │                                      │                or SMTP send
    │                                      ▼
    │                               parse subject/body
    │                                      │
    │                               save to output/
    │                                      │
    │                               log_to_audit()
    │
    └── stage 5 (30+ days) ───────────────► flag for legal review
                                            log_to_audit()
                                            no email sent
```
