# gmail_auth.py — handles Gmail OAuth2 authentication and returns a service client
#
# Run this file directly to test your credentials:
#   python gmail_auth.py
#
# On first run it will open a browser for Google login.
# After that it stores a token.pickle so subsequent runs are silent.

import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import GMAIL_SCOPES, CREDENTIALS_FILE, TOKEN_FILE


def get_gmail_service():
    """
    Authenticates via OAuth2 and returns an authorised Gmail API service client.
    Caches the token in token.pickle after the first login.
    """
    creds = None

    # Load cached token if it exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    # Refresh or re-authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"'{CREDENTIALS_FILE}' not found. Download it from "
                    "Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client (Desktop App)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)


# ─── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    service = get_gmail_service()
    profile = service.users().getProfile(userId="me").execute()
    print(f"\nAuthenticated as: {profile['emailAddress']}")
    print(f"Total messages:  {profile['messagesTotal']}")
    print(f"Unread messages: {profile['threadsTotal']}")
    print("\nGmail connection OK.")
