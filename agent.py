"""
Finance Credit Follow-Up Email Agent
Task 2 — AI Enablement Internship
"""

import os
import json
import re
import logging
from datetime import datetime, date
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()


# CONFIGURATIOn
DRY_RUN = os.getenv("DRY_RUN", "true").lower() != "false"

# Create folders if they don't exist
Path("logs").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)

AUDIT_LOG = Path("logs/audit_log.json")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/agent.log", encoding="utf-8"),
    ],
)

log = logging.getLogger("finance-agent")

# Claude client
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


# ESCALATION LOGIC
def get_stage(days_overdue: int, follow_up_count: int) -> dict:

    if days_overdue <= 0:
        return {
            "stage": 0,
            "label": "Not Overdue",
            "tone": None,
            "escalate": False,
        }

    elif days_overdue <= 7:
        return {
            "stage": 1,
            "label": "1st Follow-Up",
            "tone": "warm and friendly",
            "cta": "Pay now using the payment link below",
            "escalate": False,
        }

    elif days_overdue <= 14:
        return {
            "stage": 2,
            "label": "2nd Follow-Up",
            "tone": "polite but firm",
            "cta": "Please confirm a payment date by replying to this email",
            "escalate": False,
        }

    elif days_overdue <= 21:
        return {
            "stage": 3,
            "label": "3rd Follow-Up",
            "tone": "formal and serious",
            "cta": "Please respond within 48 hours to avoid further action",
            "escalate": False,
        }

    elif days_overdue <= 30:
        return {
            "stage": 4,
            "label": "4th Follow-Up - FINAL NOTICE",
            "tone": "stern and urgent",
            "cta": "Pay immediately or call us to avoid escalation",
            "escalate": False,
        }

    else:
        return {
            "stage": 5,
            "label": "Escalation Flag",
            "tone": None,
            "cta": None,
            "escalate": True,
        }

# INPUT SANITISATION
INJECTION_PATTERNS = [
    r"ignore (previous|all|above|prior) instructions",
    r"system prompt",
    r"you are now",
    r"act as",
    r"jailbreak",
    r"<\s*script",
    r"```",
]

def sanitise(value: str) -> str:

    if not isinstance(value, str):
        return str(value)

    cleaned = value.strip()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise ValueError(
                f"Suspicious content detected: {cleaned[:50]}"
            )

    cleaned = re.sub(r"<[^>]+>", "", cleaned)

    return cleaned

def mask_email(email: str) -> str:

    if "@" not in email:
        return "***"

    local, domain = email.split("@", 1)

    return f"{local[:2]}***@{domain}"


# EMAIL GENERATION
SYSTEM_PROMPT = """
You are a professional finance assistant.

Write ONLY the email.

Required format:

SUBJECT: ...
BODY:
...

Rules:
- Use professional tone
- No emojis
- No hallucinations
- Use only provided invoice details
"""

def generate_email(record, stage_info, days_overdue):

    user_prompt = f"""
Write a stage {stage_info['stage']} payment follow-up email.

Tone: {stage_info['tone']}

Invoice Details:
- Invoice Number: {sanitise(record['invoice_no'])}
- Client Name: {sanitise(record['client_name'])}
- Company: {sanitise(record['company'])}
- Amount Due: {sanitise(record['currency'])} {sanitise(str(record['amount']))}
- Due Date: {sanitise(str(record['due_date']))}
- Days Overdue: {days_overdue}
- Payment Link: {sanitise(record['payment_link'])}
- Finance Contact: {sanitise(record['finance_contact'])}

CTA:
{stage_info['cta']}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ],
    )

    raw = response.content[0].text.strip()

    subject = ""
    body = ""

    lines = raw.split("\n")

    body_started = False
    body_lines = []

    for line in lines:

        if line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()

        elif line.startswith("BODY:"):
            body_started = True

        elif body_started:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    # Fallback handling
    if not subject:
        subject = f"Payment Reminder - Invoice {record['invoice_no']}"

    if not body:
        body = raw

    return {
        "subject": subject,
        "body": body,
        "raw": raw,
    }


# AUDIT LOGGING
def log_to_audit(
    record,
    stage_info,
    email_data,
    days_overdue,
    sent,
    error=None,
):

    entry = {
        "timestamp": datetime.now().isoformat(),
        "invoice_no": record.get("invoice_no"),
        "client_masked": mask_email(
            str(record.get("contact_email", ""))
        ),
        "company": record.get("company"),
        "amount": record.get("amount"),
        "currency": record.get("currency"),
        "days_overdue": days_overdue,
        "stage": stage_info.get("stage"),
        "stage_label": stage_info.get("label"),
        "tone_used": stage_info.get("tone"),
        "subject": email_data.get("subject", ""),
        "dry_run": DRY_RUN,
        "sent": sent,
        "error": error,
    }

    existing = []

    if AUDIT_LOG.exists():

        try:
            with open(AUDIT_LOG, "r", encoding="utf-8") as f:
                existing = json.load(f)

        except json.JSONDecodeError:
            existing = []

    existing.append(entry)

    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

# DATA LOADING
REQUIRED_COLS = {
    "invoice_no",
    "client_name",
    "client_formal_name",
    "company",
    "amount",
    "currency",
    "due_date",
    "contact_email",
    "follow_up_count",
    "payment_link",
    "finance_contact",
}

def load_invoices(filepath: str):

    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(
            f"Invoice file not found: {filepath}"
        )

    # Read CSV or Excel
    if path.suffix == ".csv":
        df = pd.read_csv(filepath)

    elif path.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath)

    else:
        raise ValueError(
            "Unsupported file type. Use CSV or Excel."
        )

    missing = REQUIRED_COLS - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Type conversions
    df["due_date"] = pd.to_datetime(df["due_date"])

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    df["follow_up_count"] = pd.to_numeric(
        df["follow_up_count"],
        errors="coerce"
    ).fillna(0).astype(int)

    return df

def compute_days_overdue(due_date):

    today = date.today()

    return (today - due_date.date()).days

# MOCK EMAIL SENDER
def send_email(to, subject, body):

    if DRY_RUN:

        log.info(f"[DRY RUN] Would send to: {mask_email(to)}")
        log.info(f"[DRY RUN] Subject: {subject}")

        return True

    log.warning(
        "Live email sending not configured yet."
    )

    return False

# MAIN AGENT LOOP
def run_agent(invoice_file="data/invoices.csv"):

    log.info("=" * 60)

    log.info(
        f"Finance Follow-Up Agent starting - {'DRY RUN' if DRY_RUN else 'LIVE MODE'}"
    )

    log.info(f"Date: {date.today()}")

    log.info("=" * 60)

    df = load_invoices(invoice_file)

    log.info(f"Loaded {len(df)} invoice records")

    results = []

    for _, row in df.iterrows():

        record = row.to_dict()

        invoice_no = record["invoice_no"]

        try:

            days_overdue = compute_days_overdue(
                record["due_date"]
            )

            stage_info = get_stage(
                days_overdue,
                record["follow_up_count"]
            )

            log.info(
                f"Processing {invoice_no} | {record['company']} | {days_overdue} days overdue"
            )

            # Skip if not overdue
            if stage_info["stage"] == 0:

                log.info("Skipping - invoice not overdue")

                continue

            # Escalation
            if stage_info["escalate"]:

                log.warning(
                    f"[ESCALATION FLAG] {invoice_no} is {days_overdue} days overdue - assigned to finance manager"
                )

                log_to_audit(
                    record,
                    stage_info,
                    {},
                    days_overdue,
                    sent=False,
                )

                results.append({
                    "invoice": invoice_no,
                    "company": record["company"],
                    "days_overdue": days_overdue,
                    "action": "[ESCALATED] Legal/Finance Review Required",
                    "subject": "-",
                })

                continue

            # Generate AI email
            log.info(
                f"Generating Stage {stage_info['stage']} email..."
            )

            email_data = generate_email(
                record,
                stage_info,
                days_overdue
            )

            # Send email
            sent = send_email(
                record["contact_email"],
                email_data["subject"],
                email_data["body"]
            )

            # Audit logging
            log_to_audit(
                record,
                stage_info,
                email_data,
                days_overdue,
                sent
            )

            # Save generated email
            output_path = Path(
                f"output/{invoice_no}_stage{stage_info['stage']}.txt"
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    f"TO: {record['contact_email']}\n"
                )

                f.write(
                    f"SUBJECT: {email_data['subject']}\n"
                )

                f.write(
                    f"STAGE: {stage_info['label']}\n"
                )

                f.write(
                    f"DAYS OVERDUE: {days_overdue}\n"
                )

                f.write(
                    f"GENERATED: {datetime.now().isoformat()}\n"
                )

                f.write("-" * 50 + "\n")

                f.write(email_data["body"])

            results.append({
                "invoice": invoice_no,
                "company": record["company"],
                "days_overdue": days_overdue,
                "action": f"Stage {stage_info['stage']} email generated",
                "subject": email_data["subject"],
            })

        except Exception as e:

            log.error(
                f"Error processing {invoice_no}: {e}"
            )

            log_to_audit(
                record,
                {},
                {},
                0,
                sent=False,
                error=str(e),
            )

   
    # SUMMARY
    print("\n" + "=" * 70)

    print("AGENT RUN SUMMARY")

    print("=" * 70)

    summary_df = pd.DataFrame(results)

    print(summary_df.to_string(index=False))

    print("=" * 70)

    print(f"\nAudit log: {AUDIT_LOG.resolve()}")

    print(
        f"Email outputs: {Path('output').resolve()}"
    )

    return results

# ENTRY POINT
if __name__ == "__main__":

    import sys

    invoice_file = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "data/invoices.csv"
    )

    run_agent(invoice_file)
