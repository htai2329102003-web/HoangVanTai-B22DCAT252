#!/usr/bin/env python3
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOST = "0.0.0.0"
PORT = 8080
DELAY_THRESHOLD = 30
STATE_FILE = "/tmp/cloak_state.json"
LOG_FILE = os.path.expanduser("~/cloak_server.log")

BOT_KEYWORDS = [
    "sandboxscanner", "python-requests", "python-urllib",
    "curl", "wget", "googlebot", "bingbot", "scanner",
    "crawler", "spider", "headless", "monitor", "check"
]

def ts():
    return time.strftime("%H:%M:%S")

def log(msg):
    line = f"[{ts()}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)

def is_bot(ua):
    ua = ua.lower()
    return any(k in ua for k in BOT_KEYWORDS)

def read_html(name):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, name), encoding="utf-8") as f:
        return f.read()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/verify":
            self.send_error(404)
            return

        params = parse_qs(parsed.query)
        ref = params.get("ref", ["unknown"])[0]
        ua = self.headers.get("User-Agent", "")
        src_ip = self.client_address[0]
        now = time.time()

        state = load_state()
        if ref not in state:
            state[ref] = {"first_seen": now, "hits": 0}
        state[ref]["hits"] += 1
        save_state(state)

        elapsed = now - state[ref]["first_seen"]
        hit_no = state[ref]["hits"]

        if is_bot(ua):
            reason, dest = "BOT_UA", "DECOY"
        elif elapsed < DELAY_THRESHOLD:
            reason, dest = f"EARLY({elapsed:.1f}s<{DELAY_THRESHOLD}s)", "DECOY"
        else:
            reason, dest = f"PASSED({elapsed:.1f}s)", "LOGIN"

        log(
            f"hit={hit_no} ref={ref} ip={src_ip} "
            f"ua='{ua[:55]}' {reason} -> {dest}"
        )

        html = read_html("decoy_page.html" if dest == "DECOY" else "login_page.html")
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return

if __name__ == "__main__":
    log(f"cloak_server khoi dong | port={PORT} | DELAY={DELAY_THRESHOLD}s")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
