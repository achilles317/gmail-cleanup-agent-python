# config.py — all tuneable settings in one place

# ─── LLM ─────────────────────────────────────────────────────────────────────
# Using llama3.1:8b — good instruction-following, fits M1 16GB easily (~5GB RAM)
# Pull command: ollama pull llama3.1:8b
# Alternative: mistral:7b or llama3.2:3b for a lighter option
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434"  # default Ollama port

# ─── GMAIL ───────────────────────────────────────────────────────────────────
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_FILE = "credentials.json"   # downloaded from Google Cloud Console
TOKEN_FILE = "token.pickle"             # auto-generated after first OAuth login
LABEL_NAME = "Claude Read"              # label applied to archived emails

# ─── BEHAVIOUR ────────────────────────────────────────────────────────────────
DRY_RUN = True          # True = preview only, no changes made. Set False to run live.
MAX_LLM_EMAILS = 50     # max emails to send through LLM classifier per run

# ─── SCHEDULER ────────────────────────────────────────────────────────────────
# Set ENABLE_SCHEDULER = True and run scheduler.py instead of main.py.
# Supports two modes (pick one):
#
#   INTERVAL mode  — runs every N hours/minutes regardless of time of day
#   DAILY mode     — runs once a day at a fixed time (24h format, e.g. "08:00")
#
# Only one mode is active at a time. DAILY takes priority if both are set.

ENABLE_SCHEDULER = False        # flip to True to enable

# Daily mode — run once at a fixed time every day
SCHEDULE_DAILY_AT = "08:00"     # "HH:MM" in 24h format, e.g. "07:30" for 7:30am
USE_DAILY_SCHEDULE = True       # True = daily mode | False = interval mode

# Interval mode — run every N hours (or set SCHEDULE_INTERVAL_UNIT = "minutes" for testing)
SCHEDULE_INTERVAL = 6           # run every 6 hours
SCHEDULE_INTERVAL_UNIT = "hours"  # "hours" or "minutes"

# ─── RULE-BASED ARCHIVE QUERIES ──────────────────────────────────────────────
# These senders are archived immediately without going through the LLM.
# Scoped to category:primary to avoid touching Promotions/Social tabs.
# NOTE: Naukri is archived here. Other job senders are kept via KEEP_SENDERS below.
SEARCH_QUERIES = {
    "HDFC Bank":    "category:primary from:(hdfcbank OR hdfcbank.com) is:unread",
    "ICICI Bank":   "category:primary from:(icici OR icicibank) is:unread",
    "SBI":          "category:primary from:(sbi OR sbicard OR cbssbi) is:unread",
    "NSE Alerts":   "category:primary from:(nse OR nseindia OR nsemail) is:unread",
    "BSE Alerts":   "category:primary from:(bseindia) is:unread",
    "Zerodha":      "category:primary from:(zerodha) is:unread",
    "Binance":      "category:primary from:(binance OR mgdirectmail) is:unread",
    "AU Small Fin": "category:primary from:(aubank OR smallfinancebank) is:unread",
    "Townscript":   "category:primary from:(townscript) is:unread",
    "Google Maps":  "category:primary from:(google-maps-noreply) is:unread",
    "Naukri":       "category:primary from:(naukri) is:unread",
    "OTP/Transact": 'category:primary subject:(OTP OR "one time password" OR "verification code") is:unread older_than:1d',
}

# ─── ALWAYS KEEP — BYPASS LLM ────────────────────────────────────────────────
# If any of these strings appear anywhere in the sender's From field,
# the email is kept immediately without going to the LLM.
# Use substrings from the actual email address or display name.
KEEP_SENDERS = [
      # Job & career emails — keep all except Naukri (handled in rule-based archive above)
    "linkedin",
    "foundit",
    "greenhouse",
    "lever.co",
    "workday",
    "inmail",
    # Delivery updates — keep
    "delhivery",
    "shiprocket",
    "bluedart",
    "ekart",
]

# ─── ALWAYS KEEP — SUBJECT KEYWORDS (whole-word match) ───────────────────────
# Uses word-boundary matching so short words like "AI" don't match "email"/"gmail".
# Add full phrases or distinct words — no need to worry about case.
KEEP_SUBJECT_KEYWORDS = [
    "AI",                     # matches " AI " but NOT "email" or "gmail"
    "LLM",
    "GPT",
    "artificial intelligence",
    "machine learning",
    "product management",
    "product manager",
    "product sense",
    "prompt engineering",
    "vibe coding",
    "developer",
    "coding",
    "playbook",
    "career",
    "interview",
    "out for delivery",
    "order delivered",
    "order out",
]
