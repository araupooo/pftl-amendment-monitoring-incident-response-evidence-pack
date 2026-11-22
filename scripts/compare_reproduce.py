#!/usr/bin/env python3
"""compare_reproduce.py — compare a fresh clean_reproduce.sh run against
the shipped numbers. Called from inside the fresh copy with the shipped
values passed as arguments via environment variables, or with the
shipped run-manifest.json copied in as shipped-manifest.json.

Usage: python3 scripts/compare_reproduce.py <shipped-manifest.json>
Exits 0 only if every comparison check passes.
"""
import json
import os
import sys

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    shipped_path = sys.argv[1]
    shipped = load(shipped_path)
    fresh = load(os.path.join(PACK, "run-manifest.json"))
    watch = load(os.path.join(PACK, "outputs", "derived",
                              "activation-watch.json"))
    drill = load(os.path.join(PACK, "outputs", "derived",
                              "drill-results.json"))
    checks = []

    def check(label, ok, detail=""):
        checks.append({"check": label, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + label +
              ((" — " + detail) if detail else ""))

    sc = shipped["counts"]
    fc = fresh["counts"]
    check("findings total unchanged",
          fc["findings"]["total"] == sc["findings"]["total"],
          "%d vs shipped %d" % (fc["findings"]["total"],
                                sc["findings"]["total"]))
    check("claims total unchanged",
          fc["claims"]["total"] == sc["claims"]["total"],
          "%d vs shipped %d" % (fc["claims"]["total"], sc["claims"]["total"]))
    check("risks total unchanged",
          fc["risks"]["total"] == sc["risks"]["total"],
          "%d vs shipped %d" % (fc["risks"]["total"], sc["risks"]["total"]))
    check("gaps total unchanged",
          fc["gaps"] == sc["gaps"],
          "%d vs shipped %d" % (fc["gaps"], sc["gaps"]))
    check("amendments known unchanged",
          fc["amendments"]["known"] == sc["amendments"]["known"],
          "%d vs shipped %d" % (fc["amendments"]["known"],
                                sc["amendments"]["known"]))
    check("amendments enabled unchanged",
          fc["amendments"]["enabled"] == sc["amendments"]["enabled"],
          "%d vs shipped %d" % (fc["amendments"]["enabled"],
                                sc["amendments"]["enabled"]))
    check("drill still 29/29",
          drill["passed"] == drill["total"] == 29,
          "%d/%d" % (drill["passed"], drill["total"]))
    check("monitor checks all pass",
          all(c["pass"] for c in watch["checks"]),
          "%d/%d" % (sum(1 for c in watch["checks"] if c["pass"]),
                     len(watch["checks"])))
    check("validated ledger advanced",
          fresh["validated_ledger"] >= shipped["validated_ledger"],
          "fresh %d vs shipped %d" % (fresh["validated_ledger"],
                                      shipped["validated_ledger"]))
    check("no amendment holds a majority in the fresh run",
          watch["amendments_with_majority"] == 0)
    check("pinned commit unchanged",
          fresh["pinned_commit"] == shipped["pinned_commit"])
    check("verdict unchanged",
          fresh["verdict"] == shipped["verdict"])

    n_pass = sum(1 for c in checks if c["pass"])
    print("compare result: %d/%d checks PASS" % (n_pass, len(checks)))
    with open(os.path.join(PACK, "outputs", "derived",
                           "compare-results.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"passed": n_pass, "total": len(checks), "checks": checks},
                  fh, indent=1, sort_keys=True)
    if n_pass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
