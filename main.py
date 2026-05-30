# main.py — entry point for the Gmail Cleanup Agent
#
# Usage:
#   python main.py
#
# Set DRY_RUN = True in config.py to preview without making changes.
# Set DRY_RUN = False to run live.

import re
from gmail_auth import get_gmail_service
from gmail_utils import get_or_create_label, search_messages, get_email_metadata, archive_messages
from classifier import build_classifier
from config import SEARCH_QUERIES, DRY_RUN, MAX_LLM_EMAILS, KEEP_SENDERS, KEEP_SUBJECT_KEYWORDS


def is_keep(sender: str, subject: str) -> bool:
    """
    Returns True if this email should be kept regardless of LLM decision.

    Sender check  — simple substring match (case-insensitive) against the full
                    From field, e.g. 'lenny@substack.com' matches 'substack'.
    Subject check — whole-word regex match so 'AI' matches ' AI ' but NOT
                    'email', 'gmail', 'available', etc.
    """
    sender_lower = sender.lower()

    for s in KEEP_SENDERS:
        if s.lower() in sender_lower:
            return True

    for kw in KEEP_SUBJECT_KEYWORDS:
        # Use word boundaries (\b) so short tokens don't match mid-word
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, subject, re.IGNORECASE):
            return True

    return False


def run():
    print("\n" + "=" * 60)
    print("  Gmail Cleanup Agent")
    print(f"  Mode: {'DRY RUN — no changes will be made' if DRY_RUN else 'LIVE'}")
    print("=" * 60 + "\n")

    # ── Step 1: Connect to Gmail ───────────────────────────────────────────
    print("[1/4] Connecting to Gmail...")
    service = get_gmail_service()
    print("  Done.\n")

    # ── Step 2: Ensure 'Claude Read' label exists ──────────────────────────
    print("[2/4] Setting up label...")
    label_id = get_or_create_label(service)
    print(f"  Label ready.\n")

    # ── Step 3: Rule-based pass (known senders) ────────────────────────────
    print("[3/4] Rule-based pass — known senders...\n")
    summary = {}
    total_archived = 0

    for category, query in SEARCH_QUERIES.items():
        messages = search_messages(service, query)
        count = len(messages)
        summary[category] = count

        if count == 0:
            print(f"  {category:<20} 0 found")
            continue

        print(f"  {category:<20} {count} emails found", end="")

        if DRY_RUN:
            print("  → [DRY RUN] skipped")
        else:
            ids = [m["id"] for m in messages]
            archive_messages(service, ids, label_id)
            total_archived += count
            print("  → archived")

    # ── Step 4: LLM pass on remaining unread Primary emails ───────────────
    print(f"\n[4/4] LLM classifier pass (up to {MAX_LLM_EMAILS} remaining emails)...\n")
    remaining = search_messages(service, "category:primary is:unread", max_results=MAX_LLM_EMAILS)

    if not remaining:
        print("  Nothing left in Primary inbox. You're clean!")
    else:
        classify = build_classifier()
        llm_archived = 0
        llm_kept = 0

        for msg_ref in remaining:
            email = get_email_metadata(service, msg_ref["id"])

            # Pre-check: bypass LLM if sender/subject matches keep rules
            if is_keep(email["from"], email["subject"]):
                print(f"  [KEEP]    {email['subject'][:55]:<55}  {email['from'][:35]}  ← keep rule")
                llm_kept += 1
                continue

            decision = classify(email["from"], email["subject"], email["snippet"])

            tag = "[ARCHIVE]" if decision == "archive" else "[KEEP]   "
            print(f"  {tag}  {email['subject'][:55]:<55}  {email['from'][:35]}")

            if decision == "archive":
                if not DRY_RUN:
                    archive_messages(service, [email["id"]], label_id)
                    total_archived += 1
                llm_archived += 1
            else:
                llm_kept += 1

        summary["LLM — Archived"] = llm_archived
        summary["LLM — Kept"] = llm_kept

    # ── Final report ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for cat, count in summary.items():
        print(f"  {cat:<25}  {count}")
    if not DRY_RUN:
        print(f"\n  Total archived:  {total_archived}")
    print(f"  Mode: {'DRY RUN — no actual changes made.' if DRY_RUN else 'LIVE — emails archived.'}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run()
