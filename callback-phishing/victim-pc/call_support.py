#!/usr/bin/env python3
import json
import os
import socket

HOST = "support-bot"
PORT = 9000

SESSION_FILE = os.path.expanduser("~/session_data.json")

with socket.create_connection((HOST, PORT), timeout=5) as sock:
    reader = sock.makefile("r", encoding="utf-8", newline="\n")

    def read_line():
        line = reader.readline()
        return line.rstrip("\r\n") if line else ""

    print(read_line())
    print(read_line())
    print(read_line())

    name = input("> Ten gia lap: ").strip()
    if not name:
        name = "Victim Lab"

    sock.sendall((name + "\n").encode("utf-8"))

    print(read_line())

    invoice = input("> Ma hoa don gia lap: ").strip()
    if not invoice:
        invoice = "INV-LAB-001"

    sock.sendall((invoice + "\n").encode("utf-8"))

    session_data = {
        "name": name,
        "invoice": invoice,
        "classification": "FAKE-DATA-FOR-LAB"
    }

    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    while True:
        line = read_line()
        if not line:
            break
        print(line)

print("[call_support] Session data saved to ~/session_data.json")
