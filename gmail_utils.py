# gmail_utils.py — Gmail API helper functions: search, label, archive

from typing import Optional
from googleapiclient.discovery import Resource
from config import LABEL_NAME


def get_or_create_label(service: Resource, label_name: str = LABEL_NAME) -> str:
    """
    Returns the label ID for LABEL_NAME.
    Creates the label if it doesn't exist yet.
    """
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]

    new_label = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
    ).execute()
    print(f"  [+] Created label: '{label_name}'")
    return new_label["id"]


def search_messages(service: Resource, query: str, max_results: int = 500) -> list:
    """
    Runs a Gmail search and returns a list of message objects {id, threadId}.
    Handles pagination automatically.
    """
    messages = []
    result = service.users().messages().list(
        userId="me", q=query, maxResults=min(max_results, 500)
    ).execute()
    messages.extend(result.get("messages", []))

    while "nextPageToken" in result and len(messages) < max_results:
        result = service.users().messages().list(
            userId="me", q=query, maxResults=min(max_results - len(messages), 500),
            pageToken=result["nextPageToken"]
        ).execute()
        messages.extend(result.get("messages", []))

    return messages


def get_email_metadata(service: Resource, msg_id: str) -> dict:
    """
    Fetches From, Subject, and snippet for a single message.
    Uses metadata format to avoid downloading full message body.
    """
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["From", "Subject"]
    ).execute()
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    return {
        "id": msg_id,
        "from": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "snippet": msg.get("snippet", ""),
    }


def archive_messages(service: Resource, message_ids: list[str], label_id: str) -> None:
    """
    Batch operation: marks messages as read, removes from inbox, applies label.
    Does nothing if message_ids is empty.
    """
    if not message_ids:
        return

    service.users().messages().batchModify(
        userId="me",
        body={
            "ids": message_ids,
            "removeLabelIds": ["UNREAD", "INBOX"],
            "addLabelIds": [label_id],
        }
    ).execute()
