#!/usr/bin/env python3
"""
victim_browser.py
-------------------
Mo phong mot nguoi dung that: cho mot khoang thoi gian (mac dinh dai hon
DELAY_THRESHOLD trong cloak_server.py) roi moi truy cap link - dung de
kiem tra logic delay activation.

Cach chay:
    python3 victim_browser.py
    python3 victim_browser.py http://localhost:8080/promo?id=demo 185
"""
import sys
import time
import requests

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/promo?id=demo"
wait_seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 185
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
}

print(f"[victim_browser] cho {wait_seconds} giay truoc khi truy cap "
      f"(mo phong hanh vi nguoi dung that)...")
time.sleep(wait_seconds)
print(f"[victim_browser] truy cap: {url}")
r = requests.get(url, headers=headers, allow_redirects=True)
print(f"[victim_browser] ket qua cuoi: {r.url}")
print(f"[victim_browser] status: {r.status_code}")
