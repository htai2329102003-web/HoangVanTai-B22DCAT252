#!/usr/bin/env python3
"""
cloak_server.py
----------------
Mo phong mot "redirector" phuc vu bai lab URL Cloaking & Delayed Activation.
File nay KHONG chua ma doc hai thuc su - chi mo phong luong dieu huong
(redirect) theo ky thuat cloaking/delay activation, phuc vu dao tao
an toan thong tin trong moi truong Labtainer (container co lap).

Cach chay:
    python3 cloak_server.py
Server se lang nghe tai: http://localhost:8080/promo?id=<ten_nguoi_dung>
"""
import time
import json
import os
from flask import Flask, request, redirect

from delay_logic import decide_destination

app = Flask(__name__)

STATE_FILE = "/tmp/visitor_state.json"
DELAY_THRESHOLD = 180  # giay - sinh vien co the doc/tham khao gia tri nay trong delay_logic.py

# File log ben vung - dung cho checkwork/cham diem tu dong (xem docs/README
# phan "Checkwork"). Ghi vao thu muc HOME cua sinh vien, Labtainer se tu
# thu thap file nay vi no duoc nhac toi trong instr_config/results.config
LOG_FILE = os.path.join(os.path.expanduser("~"), "cloak_server.log")


def log_line(text: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {text}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


@app.route("/promo")
def promo():
    visitor_id = request.args.get("id", "anonymous")
    ua = request.headers.get("User-Agent", "")
    now = time.time()

    state = load_state()
    if visitor_id not in state:
        state[visitor_id] = {"first_seen": now, "visits": 0}
    state[visitor_id]["visits"] += 1
    save_state(state)

    first_seen = state[visitor_id]["first_seen"]
    elapsed = now - first_seen

    destination = decide_destination(elapsed, ua, DELAY_THRESHOLD)

    if destination == "decoy":
        log_line(f"visitor={visitor_id} ua='{ua}' elapsed={elapsed:.1f}s -> DECOY")
        return redirect("/decoy")
    else:
        log_line(f"visitor={visitor_id} ua='{ua}' elapsed={elapsed:.1f}s -> PAYLOAD")
        return redirect("/payload")


@app.route("/decoy")
def decoy():
    with open("decoy_page.html") as f:
        return f.read()


@app.route("/payload")
def payload():
    with open("payload_page.html") as f:
        return f.read()


if __name__ == "__main__":
    log_line(f"[cloak_server] khoi dong, DELAY_THRESHOLD={DELAY_THRESHOLD}s")
    app.run(host="0.0.0.0", port=8080)
