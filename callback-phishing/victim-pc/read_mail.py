#!/usr/bin/env python3
from pathlib import Path
import json

mail_file = Path.home() / "inbox" / "latest_mail.json"

if not mail_file.exists():
    raise SystemExit("[read_mail] Chua co email. Hay de attacker-srv chay send_email.py truoc.")

mail = json.loads(mail_file.read_text(encoding="utf-8"))

print("=" * 64)
print("INBOX - EMAIL MO PHONG")
print("=" * 64)
print("From   :", mail.get("from", ""))
print("Subject:", mail.get("subject", ""))
print("-" * 64)
print(mail.get("body", ""))
print("=" * 64)
