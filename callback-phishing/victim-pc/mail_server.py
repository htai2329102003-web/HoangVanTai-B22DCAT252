#!/usr/bin/env python3
from flask import Flask, request, jsonify
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)
HOME = Path.home()
INBOX = HOME / "inbox"
LOG = HOME / "victim_mail.log"
INBOX.mkdir(exist_ok=True)

def log(message: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{ts} {message}\n")
    print(message, flush=True)

@app.route("/mail", methods=["POST"])
def receive_mail():
    data = request.get_json(silent=True) or {}
    (INBOX / "latest_mail.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log("EMAIL_RECEIVED")
    return jsonify({"status": "ok", "stored": str(INBOX / "latest_mail.json")})

if __name__ == "__main__":
    print("[mail_server] Listening on 0.0.0.0:7070", flush=True)
    app.run(host="0.0.0.0", port=7070, debug=False)
