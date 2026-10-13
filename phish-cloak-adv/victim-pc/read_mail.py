#!/usr/bin/env python3
"""
read_mail.py  |  victim-pc
----------------------------
Doc va hien thi email trong ~/inbox/ voi giao dien dep trong terminal.
Phat hien va lam noi bat URL co trong noi dung email.

Cach chay:
    python3 read_mail.py
"""
import os, json, glob, re

INBOX = os.path.expanduser("~/inbox")

B  = "\033[1m";  C  = "\033[96m"; Y  = "\033[93m"
R  = "\033[91m"; G  = "\033[92m"; RS = "\033[0m"
DIM= "\033[2m"

def find_urls(text):
    return re.findall(r"https?://[^\s]+", text)

def render(path):
    with open(path, encoding="utf-8") as f:
        m = json.load(f)

    urls  = find_urls(m.get("body", ""))
    width = 62

    print(f"\n{'=' * width}")
    print(f"{B}  INOX THU DIEN TU{RS}")
    print(f"{'=' * width}")
    print(f"  {B}Tu     :{RS} {C}{m.get('from','')}{RS}")
    print(f"  {B}Den    :{RS} {m.get('to','')}")
    print(f"  {B}Tieu de:{RS} {Y}{m.get('subject','')}{RS}")
    print(f"  {DIM}{'- ' * 31}{RS}")
    # In noi dung - them khoang trang dau moi dong
    for line in m.get("body", "").splitlines():
        print(f"  {line}")
    if urls:
        print(f"\n  {R}{B}[!] PHAT HIEN URL TRONG EMAIL:{RS}")
        for u in urls:
            print(f"      {C}{u}{RS}")
    print(f"{'=' * width}")
    print(f"\n  {G}Buoc tiep theo:{RS} python3 browse.py\n")

def main():
    files = sorted(glob.glob(os.path.join(INBOX, "*.json")))
    if not files:
        print(f"{Y}[read_mail]{RS} Hop thu trong.")
        print("  -> Dam bao mail_server.py dang chay va attacker-srv")
        print("     da chay python3 send_phish.py.")
        return
    print(f"[read_mail] Co {len(files)} thu trong hop.")
    for p in files:
        render(p)

if __name__ == "__main__":
    main()
