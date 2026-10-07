#!/usr/bin/env python3
"""
sandbox_bot.py
---------------
Mo phong mot trinh quet tu dong (sandbox / URL scanner) truy cap link
NGAY LAP TUC sau khi link duoc tao - dung de kiem tra logic cloaking.

Cach chay:
    python3 sandbox_bot.py
    python3 sandbox_bot.py http://localhost:8080/promo?id=demo
"""
import sys
import requests

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/promo?id=demo"
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; SandboxScanner/1.0; "
                  "+https://example-security-vendor.test)"
}

print(f"[sandbox_bot] truy cap ngay lap tuc: {url}")
r = requests.get(url, headers=headers, allow_redirects=True)
print(f"[sandbox_bot] ket qua cuoi: {r.url}")
print(f"[sandbox_bot] status: {r.status_code}")
