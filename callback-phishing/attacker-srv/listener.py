#!/usr/bin/env python3
import json
import socket
from pathlib import Path
from datetime import datetime

HOST = "0.0.0.0"
PORT = 4444
LOG = Path.home() / "attacker_callback.log"
LOOT = Path.home() / "loot.txt"

def log(message: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{ts} {message}\n")
    print(message, flush=True)

def main() -> None:
    print(f"[listener] Lab-only callback listener on {HOST}:{PORT}", flush=True)
    print("[listener] This demo accepts structured lab data only; it does not execute commands.", flush=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)

        conn, addr = server.accept()
        with conn:
            log(f"CALLBACK_CONNECTED source={addr[0]}:{addr[1]}")
            raw = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                raw += chunk
                if len(raw) > 64 * 1024:
                    break

            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                payload = {}

            if payload.get("lab") != "callback-phishing":
                log("INVALID_LAB_PAYLOAD")
                return

            synthetic = str(payload.get("synthetic_secret", ""))
            if synthetic:
                LOOT.write_text(synthetic + "\n", encoding="utf-8")
                log("SECRET_DATA_RECEIVED")
                print(f"[listener] Synthetic lab data saved to {LOOT}", flush=True)
            else:
                log("NO_SYNTHETIC_DATA")

if __name__ == "__main__":
    main()
