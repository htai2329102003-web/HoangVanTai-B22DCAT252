#!/usr/bin/env python3
import requests

MAIL_URL = "http://victim-pc:7070/mail"

EMAIL = {
    "from": "billing-alert@training.invalid",
    "subject": "[LAB] Thong bao hoa don can xac minh",
    "body": (
        "Day la email MO PHONG trong bai Labtainer callback-phishing.\n"
        "He thong thong bao co mot giao dich 5.000.000 VND can xac minh.\n"
        "Khong co URL hoac file dinh kem. De tiep tuc bai lab, hay mo tong dai mo phong\n"
        "bang lenh: python3 call_support.py\n"
        "So tong dai hien thi trong kich ban: 1900-LAB-TOAD (chi la du lieu gia lap)."
    ),
}

def main() -> None:
    print(f"[send_email] Sending simulated email to {MAIL_URL}")
    response = requests.post(MAIL_URL, json=EMAIL, timeout=5)
    response.raise_for_status()
    print("[send_email] EMAIL_SENT")
    print(response.json())

if __name__ == "__main__":
    main()
