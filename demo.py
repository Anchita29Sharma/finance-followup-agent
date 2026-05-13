"""
demo.py — Run this to see sample outputs without an API key.
Shows all follow-up stages using mock AI-generated emails.
When your API key is ready, run agent.py instead.
"""

import json
from datetime import date
from pathlib import Path

# ============================================================
# CREATE REQUIRED FOLDERS
# ============================================================

Path("output").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# ============================================================
# MOCK INVOICE DATA
# ============================================================

MOCK_INVOICES = [
    {
        "invoice_no": "INV-2024-001",
        "client_name": "Rajesh",
        "client_formal_name": "Mr. Sharma",
        "company": "Sharma Enterprises",
        "amount": 45000,
        "currency": "INR",
        "days_overdue": 4,
        "stage": 1,
        "contact_email": "rajesh.sharma@sharmaent.com",
        "payment_link": "https://pay.example.com/INV-2024-001",
    },
    {
        "invoice_no": "INV-2024-002",
        "client_name": "Priya",
        "client_formal_name": "Ms. Mehta",
        "company": "Mehta Solutions Pvt Ltd",
        "amount": 120000,
        "currency": "INR",
        "days_overdue": 11,
        "stage": 2,
        "contact_email": "priya.mehta@mehtasolutions.in",
        "payment_link": "https://pay.example.com/INV-2024-002",
    },
    {
        "invoice_no": "INV-2024-003",
        "client_name": "Arjun",
        "client_formal_name": "Mr. Verma",
        "company": "Verma & Co.",
        "amount": 78500,
        "currency": "INR",
        "days_overdue": 18,
        "stage": 3,
        "contact_email": "arjun.verma@vermaandco.com",
        "payment_link": "https://pay.example.com/INV-2024-003",
    },
    {
        "invoice_no": "INV-2024-004",
        "client_name": "Sneha",
        "client_formal_name": "Ms. Rao",
        "company": "Rao Technologies",
        "amount": 200000,
        "currency": "INR",
        "days_overdue": 27,
        "stage": 4,
        "contact_email": "sneha.rao@raotechnologies.com",
        "payment_link": "https://pay.example.com/INV-2024-004",
    },
    {
        "invoice_no": "INV-2024-005",
        "client_name": "Karan",
        "client_formal_name": "Mr. Gupta",
        "company": "Gupta Imports Ltd",
        "amount": 55000,
        "currency": "INR",
        "days_overdue": 35,
        "stage": 5,
        "contact_email": "karan.gupta@guptaimports.com",
        "payment_link": "https://pay.example.com/INV-2024-005",
    },
]

# ============================================================
# MOCK EMAIL OUTPUTS
# ============================================================

MOCK_EMAILS = {
    1: {
        "subject": "Quick Reminder - Invoice #INV-2024-001 | INR 45,000 Due",
        "body": """Hi Rajesh,

Hope you're doing well!

Just a quick reminder that Invoice #INV-2024-001 for INR 45,000 was due 4 days ago.

These things can occasionally slip through, so no worries if the payment is already being processed.

Payment link:
https://pay.example.com/INV-2024-001

If payment has already been made, please ignore this email.

Warm regards,
Finance Team
accounts@ourcompany.com"""
    },

    2: {
        "subject": "Payment Pending - Invoice #INV-2024-002",
        "body": """Dear Ms. Mehta,

This is a follow-up regarding Invoice #INV-2024-002 for INR 1,20,000, which remains unpaid 11 days after the due date.

Please confirm the expected payment date at your earliest convenience.

Payment link:
https://pay.example.com/INV-2024-002

If there is any issue with the invoice, feel free to contact us.

Regards,
Finance Team"""
    },

    3: {
        "subject": "Important: Outstanding Invoice #INV-2024-003",
        "body": """Dear Mr. Verma,

Despite previous reminders, Invoice #INV-2024-003 for INR 78,500 remains unpaid and is now 18 days overdue.

Please make payment or respond within 48 hours with an update regarding the payment timeline.

Payment link:
https://pay.example.com/INV-2024-003

Regards,
Finance Department"""
    },

    4: {
        "subject": "FINAL NOTICE - Invoice #INV-2024-004",
        "body": """Dear Ms. Rao,

This is the final reminder regarding Invoice #INV-2024-004 for INR 2,00,000, which is now 27 days overdue.

Please make payment immediately to avoid escalation to our finance and recovery team.

Payment link:
https://pay.example.com/INV-2024-004

Finance Department"""
    },

    5: {
        "subject": None,
        "body": None,
        "escalation_note": "[ESCALATED] 35 days overdue. Assigned to finance/legal review."
    }
}

# ============================================================
# DEMO RUNNER
# ============================================================

def run_demo():

    print("=" * 65)
    print("FINANCE FOLLOW-UP AGENT - DEMO RUN")
    print(f"Date: {date.today()}")
    print("=" * 65)

    audit_entries = []

    for inv in MOCK_INVOICES:

        stage = inv["stage"]

        email = MOCK_EMAILS[stage]

        print("\n" + "-" * 60)

        print(f"Invoice : {inv['invoice_no']}")
        print(f"Client  : {inv['company']} ({inv['client_formal_name']})")
        print(f"Amount  : {inv['currency']} {inv['amount']:,}")
        print(f"Overdue : {inv['days_overdue']} days -> Stage {stage}")

        # ====================================================
        # STAGE 5 ESCALATION
        # ====================================================

        if stage == 5:

            print(f"\n{email['escalation_note']}")

            audit_entries.append({
                "invoice_no": inv["invoice_no"],
                "stage": 5,
                "action": "ESCALATED",
                "sent": False,
                "days_overdue": inv["days_overdue"],
            })

            with open(
                f"output/{inv['invoice_no']}_ESCALATED.txt",
                "w",
                encoding="utf-8"
            ) as f:

                f.write("ESCALATION RECORD\n")
                f.write(f"Invoice: {inv['invoice_no']}\n")
                f.write(f"Company: {inv['company']}\n")
                f.write(f"Amount: {inv['currency']} {inv['amount']:,}\n")
                f.write(f"Days Overdue: {inv['days_overdue']}\n")
                f.write("Action Required: Finance/Legal Review\n")

        # ====================================================
        # EMAIL STAGES
        # ====================================================

        else:

            print(f"\nSubject : {email['subject']}")

            print(f"\nBody:\n{email['body']}")

            masked_email = (
                f"{inv['contact_email'][:2]}***@"
                f"{inv['contact_email'].split('@')[1]}"
            )

            print(f"\n[DRY RUN] Would send to: {masked_email}")

            with open(
                f"output/{inv['invoice_no']}_stage{stage}.txt",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(f"TO: {inv['contact_email']}\n")
                f.write(f"SUBJECT: {email['subject']}\n")
                f.write(f"STAGE: {stage}\n")
                f.write(f"DAYS OVERDUE: {inv['days_overdue']}\n")
                f.write("-" * 50 + "\n")
                f.write(email["body"])

            audit_entries.append({
                "invoice_no": inv["invoice_no"],
                "stage": stage,
                "action": "Email generated (dry-run)",
                "sent": False,
                "days_overdue": inv["days_overdue"],
                "subject": email["subject"],
            })

    # ============================================================
    # SAVE AUDIT LOG
    # ============================================================

    with open(
        "logs/audit_log.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(audit_entries, f, indent=2)

    # ============================================================
    # FINAL SUMMARY
    # ============================================================

    print("\n" + "=" * 65)

    print("DEMO COMPLETE")

    print("=" * 65)

    print("Audit log   -> logs/audit_log.json")
    print("Email files -> output/")
    print("Run agent.py with API key for live AI generation.")

    print("=" * 65)

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_demo()