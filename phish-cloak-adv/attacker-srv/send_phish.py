#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

VICTIM_MAIL = "http://victim-pc:7070/receive"
CLOAK_URL = "http://attacker-srv:8080/verify?ref=promo2024"

EMAIL = {
    "from": "no-reply@internal-portal.test",
    "to": "demo.user@lab.test",
    "subject": "[LAB] Tai khoan mo phong can xac nhan",
    "body": f"""Day la email MO PHONG trong Labtainer.

Vui long truy cap duong dan demo:
    {CLOAK_URL}

Chi su dung tai khoan/mat khau gia danh cho bai lab.
"""
}

def main():
    print("[send_phish] Dang gui email MO PHONG toi victim-pc...")
    data = json.dumps(EMAIL).encode("utf-8")
    req = urllib.request.Request(
        VICTIM_MAIL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                print("[OK] Email demo da gui thanh cong.")
                print("URL:", CLOAK_URL)
            else:
                print("[FAIL] victim-pc tra ve", resp.status)
    except Exception as e:
        print("[ERROR] Khong ket noi duoc victim-pc:7070:", e)

if __name__ == "__main__":
    main()
