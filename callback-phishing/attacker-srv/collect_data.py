#!/usr/bin/env python3
from pathlib import Path

loot = Path.home() / "loot.txt"

if not loot.exists():
    print("[collect_data] No lab data has been received yet.")
else:
    print("=== SYNTHETIC LAB DATA ===")
    print(loot.read_text(encoding="utf-8").rstrip())
    print("==========================")
