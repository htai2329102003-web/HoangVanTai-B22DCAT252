#!/usr/bin/env python3
import socket
from pathlib import Path
from datetime import datetime

HOST = "0.0.0.0"
PORT = 9000
LOG = Path.home() / "support.log"

def log(message: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{ts} {message}\n")
    print(message, flush=True)

def send_line(conn, text: str) -> None:
    conn.sendall((text + "\n").encode("utf-8"))

def recv_line(conn) -> str:
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(1024)
        if not chunk:
            break
        data += chunk
        if len(data) > 4096:
            break
    return data.decode("utf-8", errors="replace").strip()

def handle(conn, addr) -> None:
    log(f"VICTIM_CONNECTED source={addr[0]}:{addr[1]}")
    send_line(conn, "=== TONG DAI MO PHONG CALLBACK-PHISHING ===")
    send_line(conn, "Day la dich vu gia lap chi dung trong Labtainer.")
    send_line(conn, "Nhap ten gia lap cua ban:")
    name = recv_line(conn)
    send_line(conn, f"Xin chao {name or 'hoc vien'}. Nhap ma hoa don gia lap:")
    invoice = recv_line(conn)

    send_line(conn, "Da ghi nhan thong tin mo phong.")
    send_line(conn, "Buoc tiep theo cua bai lab: ket thuc cuoc goi, sau do chay:")
    send_line(conn, "python3 callback_client.py")
    send_line(conn, "Client nay CHI gui du lieu mau den attacker-srv trong mang noi bo cua lab.")
    log(f"SUPPORT_GUIDANCE_SENT invoice={invoice or 'unknown'}")

def main() -> None:
    print(f"[support-bot] Listening on {HOST}:{PORT}", flush=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        while True:
            conn, addr = server.accept()
            with conn:
                handle(conn, addr)

if __name__ == "__main__":
    main()
