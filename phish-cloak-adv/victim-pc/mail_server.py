#!/usr/bin/env python3
import glob
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = 7070
INBOX = os.path.expanduser("~/inbox")
os.makedirs(INBOX, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/receive":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)

        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            self.send_error(400, "du lieu khong hop le")
            return

        fname = os.path.join(INBOX, f"mail_{int(time.time())}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        count = len(glob.glob(os.path.join(INBOX, "*.json")))
        print(
            f"[mail_server] Thu moi: {os.path.basename(fname)} "
            f"(tong {count} thu trong hop)",
            flush=True,
        )

        body = b'{"status":"ok"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return

if __name__ == "__main__":
    print(f"[mail_server] Lang nghe tai port {PORT} | inbox={INBOX}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
