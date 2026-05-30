# Gmail Cleanup Agent

Locally running Python agent that cleans your Gmail inbox using rule-based filters + an Ollama LLM classifier. No cloud dependency — everything runs on your machine.

---

## Project Structure

```
gmail-cleanup-agent/
├── config.py          # All settings: model, queries, senders, scheduler, dry-run
├── gmail_auth.py      # Gmail OAuth2 setup — run this first to test connection
├── gmail_utils.py     # Gmail API helpers: search, archive, label
├── classifier.py      # Ollama LLM email classifier
├── main.py            # One-shot entry point — runs the agent once
├── scheduler.py       # Scheduled entry point — runs agent on a set frequency
├── scheduler.log      # Auto-created log file when scheduler runs
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Gmail API credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable the **Gmail API**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Desktop App**
6. Download the JSON file and rename it to `credentials.json`
7. Place it in this folder
8. Go to **Audience → Test users** and add your Gmail address

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull the recommended model

```bash
ollama pull llama3.1:8b
```

**Why llama3.1:8b?** Strong instruction-following capability, handles classification prompts reliably. Runs in ~5GB RAM — well within M1 16GB limits. For a lighter option use `llama3.2:3b` and update `OLLAMA_MODEL` in `config.py`.

### 4. Test Gmail connection

```bash
python gmail_auth.py
```

This opens a browser for Gmail OAuth login on first run. After that it stores `token.pickle` and all future runs are silent.

---

## Running the Agent

**One-shot (manual run):**
```bash
python main.py
```

By default `DRY_RUN = True` in `config.py` — it shows you what *would* be archived without touching anything. Once you're happy, set `DRY_RUN = False` and run again.

**Scheduled (automatic recurring run):**
```bash
python scheduler.py
```

See the [Scheduler](#scheduler) section below for setup.

---

## How It Works

**Stage 1 — Rule-based (fast, no LLM)**
Searches Gmail using the queries in `config.py` for known senders: HDFC, ICICI, SBI, NSE, BSE, Zerodha, Naukri, OTPs. These are archived immediately.

**Stage 2 — LLM classifier (Ollama)**
Picks up whatever's left unread in Primary (up to `MAX_LLM_EMAILS`). The LLM reads From, Subject, and snippet and decides `archive` or `keep`. Personal emails and anything needing attention are left alone.

**All archived emails:**
- Marked as read
- Removed from inbox
- Filed under the **Claude Read** label (never deleted)

---

## Scheduler

`scheduler.py` keeps the agent running continuously and triggers cleanup at your configured frequency. It logs every run to `scheduler.log`.

### Step 1 — Configure in `config.py`

```python
ENABLE_SCHEDULER   = True       # must be True to activate

USE_DAILY_SCHEDULE = True       # True = run once daily at a fixed time
SCHEDULE_DAILY_AT  = "08:00"    # time in HH:MM (24h format)

# If USE_DAILY_SCHEDULE = False, interval mode kicks in:
SCHEDULE_INTERVAL      = 6       # run every 6 hours
SCHEDULE_INTERVAL_UNIT = "hours" # "hours" or "minutes"
```

### Step 2 — Run it

```bash
python scheduler.py
```

Keep this terminal open (or run it in a background tmux/screen session). The agent fires immediately on startup, then repeats at the configured schedule.

### Stopping it

Press `Ctrl+C` — the scheduler exits cleanly.

### Checking logs

```bash
tail -f scheduler.log
```

### Tips

- Use `USE_DAILY_SCHEDULE = True` with `SCHEDULE_DAILY_AT = "07:00"` to wake up to a clean inbox every morning.
- For testing, set `SCHEDULE_INTERVAL = 2` and `SCHEDULE_INTERVAL_UNIT = "minutes"` to verify it fires correctly, then switch to hours.
- The scheduler catches and logs errors so a single failed run (e.g. network blip) doesn't kill the process.

---

## Configuration

Edit `config.py` to customise:

| Setting | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.1:8b` | Ollama model to use |
| `DRY_RUN` | `True` | Preview mode — no changes made |
| `MAX_LLM_EMAILS` | `50` | Max emails to classify per run |
| `LABEL_NAME` | `Claude Read` | Gmail label for archived emails |
| `SEARCH_QUERIES` | see config | Add/remove sender rules here |
| `ENABLE_SCHEDULER` | `False` | Set True to activate scheduler |
| `USE_DAILY_SCHEDULE` | `True` | True = daily at fixed time, False = interval |
| `SCHEDULE_DAILY_AT` | `"08:00"` | Time to run daily (24h format) |
| `SCHEDULE_INTERVAL` | `6` | Interval between runs (hours or minutes) |
| `SCHEDULE_INTERVAL_UNIT` | `"hours"` | Unit for interval mode |

---

## Adding More Senders

Open `config.py` and add to `SEARCH_QUERIES`:

```python
"Amazon":  "category:primary from:(amazon.in OR amazon.com) is:unread",
"IRCTC":   "category:primary from:(irctc) is:unread",
```

Always prefix with `category:primary` to avoid touching Promotions/Social tabs.
