#!/usr/bin/env python3
"""measure_cadence.py — measure the live ledger cadence over a 60 s window.

Two server_info calls 60 s apart; cadence = interval / ledgers advanced.
Writes outputs/derived/cadence.json. Read-only; two RPC calls.
"""
import json
import os
import subprocess
import time

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PACK, "outputs")
DERIVED = os.path.join(OUT, "derived")
RPC = "https://rpc.testnet.postfiat.org/"
INTERVAL = 60


def server_info():
    p = subprocess.run(
        ["curl", "-s", "-m", "30", "-X", "POST", RPC,
         "-H", "Content-Type: application/json",
         "-d", '{"method":"server_info","params":[{}]}'],
        capture_output=True, text=True)
    d = json.loads(p.stdout)
    info = d["result"]["info"]
    return info["validated_ledger"]["seq"], info["time"]


def main():
    os.makedirs(DERIVED, exist_ok=True)
    s1, t1 = server_info()
    print("t0: %d %s" % (s1, t1))
    time.sleep(INTERVAL)
    s2, t2 = server_info()
    print("t1: %d %s" % (s2, t2))
    ledgers = s2 - s1
    if ledgers <= 0:
        raise SystemExit("ledger did not advance in %d s" % INTERVAL)
    cadence = INTERVAL / ledgers
    print("ledgers: %d cadence: %.3f s/ledger" % (ledgers, cadence))
    with open(os.path.join(DERIVED, "cadence.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"seq_start": s1, "time_start": t1,
                   "seq_end": s2, "time_end": t2,
                   "interval_s": INTERVAL, "ledgers": ledgers,
                   "cadence_s": cadence}, fh, indent=1)


if __name__ == "__main__":
    main()
