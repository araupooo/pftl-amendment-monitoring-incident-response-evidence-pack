#!/usr/bin/env python3
"""extract_excerpts.py — copy verbatim pinned-source excerpts into
fixtures/source-excerpts/ and record blob hashes in
fixtures/source-hashes.json.

Every excerpt's line range was verified with grep -n against the local
checkout of the pinned commit (0085a1ff) in /tmp/postfiatd-pin. The
script re-verifies each range contains its anchor text before writing,
and fails loudly if an anchor is missing — so a drifted line number
cannot silently ship a wrong excerpt.
"""
import hashlib
import json
import os
import subprocess
import sys

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIN_DIR = "/tmp/postfiatd-pin"
PIN = "0085a1ff885d6a446369cf73a4430f75af22be55"
EXCERPTS = os.path.join(PACK, "fixtures", "source-excerpts")
os.makedirs(EXCERPTS, exist_ok=True)

# (outfile, source path relative to the pinned checkout,
#  [(first, last), ...] 1-based inclusive line ranges, anchor substring)
SPECS = [
    ("features-macro-PF-amendments.txt",
     "include/xrpl/protocol/detail/features.macro",
     [(44, 47)], "PF_AccountExclusion"),
    ("features-macro-unsupported.txt",
     "include/xrpl/protocol/detail/features.macro",
     [(34, 36), (38, 42), (50, 54), (66, 68)], "Supported::no"),
    ("feature-id-derivation.txt",
     "src/libxrpl/protocol/Feature.cpp",
     [(260, 270)], "sha512Half"),
    ("feature-vote-behavior-comment.txt",
     "src/libxrpl/protocol/Feature.cpp",
     [(74, 84)], "VoteBehavior::DefaultNo"),
    ("system-parameters-thresholds.txt",
     "include/xrpl/protocol/SystemParameters.h",
     [(78, 89)], "postFixAmendmentMajorityCalcThreshold"),
    ("amendment-threshold-calc.txt",
     "src/xrpld/app/misc/detail/AmendmentTable.cpp",
     [(324, 342), (359, 378)], "computeThreshold"),
    ("amendment-do-voting.txt",
     "src/xrpld/app/misc/detail/AmendmentTable.cpp",
     [(884, 940)], "tfGotMajority"),
    ("amendment-flag-ledger.txt",
     "src/xrpld/app/misc/detail/AmendmentTable.cpp",
     [(944, 956), (958, 995)], "needValidatedLedger"),
    ("amendment-one-way.txt",
     "src/xrpld/app/misc/detail/AmendmentTable.cpp",
     [(294, 302)], "one-way switch"),
    ("amendment-admin-vote-counts.txt",
     "src/xrpld/app/misc/detail/AmendmentTable.cpp",
     [(1000, 1025)], "isAdmin"),
    ("amendment-do-validation.txt",
     "src/xrpld/app/misc/detail/AmendmentTable.cpp",
     [(813, 838)], "doValidation"),
    ("feature-rpc-handler.txt",
     "src/xrpld/rpc/handlers/Feature1.cpp",
     [(40, 70), (76, 95)], "jss::majority"),
    ("config-majority-time-parse.txt",
     "src/xrpld/core/detail/Config.cpp",
     [(870, 898)], "SECTION_AMENDMENT_MAJORITY_TIME"),
    ("config-majority-time-default.txt",
     "src/xrpld/core/Config.h",
     [(246, 250)], "defaultAmendmentMajorityTime"),
    ("application-amendment-table-setup.txt",
     "src/xrpld/app/main/Application.cpp",
     [(1270, 1293)], "make_AmendmentTable"),
    ("pf-vote-tracking-gate.txt",
     "src/xrpld/app/misc/ValidatorVoteTracker.cpp",
     [(155, 165)], "featurePF_ValidatorVoteTracking"),
    ("pf-account-exclusion-gate.txt",
     "src/xrpld/app/tx/detail/Change.cpp",
     [(615, 625)], "featurePF_AccountExclusion"),
    ("feature-num-features.txt",
     "include/xrpl/protocol/Feature.h",
     [(105, 115)], "numFeatures"),
]

# Whole files shipped verbatim so the registration count is checkable.
WHOLE_FILES = [
    "include/xrpl/protocol/detail/features.macro",
]


def git_blob_sha(path):
    out = subprocess.run(["git", "hash-object", path],
                         capture_output=True, text=True, cwd=PIN_DIR)
    if out.returncode != 0:
        raise RuntimeError("git hash-object failed for %s" % path)
    return out.stdout.strip()


def main():
    head = subprocess.run(["git", "rev-parse", "HEAD"],
                          capture_output=True, text=True, cwd=PIN_DIR)
    assert head.stdout.strip() == PIN, \
        "pinned checkout HEAD is %s, want %s" % (head.stdout.strip(), PIN)
    print("pinned checkout HEAD verified: %s" % PIN)

    hashes = {"pinned_commit": PIN, "files": {}, "excerpts": {}}
    for rel in WHOLE_FILES:
        src = os.path.join(PIN_DIR, rel)
        dst = os.path.join(PACK, "fixtures", os.path.basename(rel))
        with open(src, "rb") as fh:
            data = fh.read()
        with open(dst, "wb") as fh:
            fh.write(data)
        st = os.stat(src)
        hashes["files"][rel] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha": git_blob_sha(src),
            "bytes": len(data),
            "lines": data.decode("utf-8").count("\n"),
        }
        print("whole file: %s (%d bytes)" % (rel, len(data)))

    for outfile, rel, ranges, anchor in SPECS:
        src = os.path.join(PIN_DIR, rel)
        with open(src, encoding="utf-8") as fh:
            lines = fh.readlines()
        picked = []
        for first, last in ranges:
            picked.append("--- %s lines %d-%d ---\n" % (rel, first, last))
            picked.extend(lines[first - 1:last])
        text = "".join(picked)
        if anchor not in text:
            print("FAIL anchor %r missing in %s" % (anchor, outfile))
            sys.exit(1)
        dst = os.path.join(EXCERPTS, outfile)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(text)
        hashes["excerpts"][outfile] = {
            "source": rel,
            "ranges": [[a, b] for a, b in ranges],
            "anchor": anchor,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "lines": text.count("\n"),
        }
        print("excerpt: %s <- %s %s" % (outfile, rel, ranges))

    # Absence checks: names the pinned code does NOT contain.
    absence = {}
    for name in ["OrchardPrivacy"]:
        out = subprocess.run(["grep", "-r", "--include=*.cpp",
                              "--include=*.h", "--include=*.macro",
                              "-l", name, "src", "include"],
                             capture_output=True, text=True, cwd=PIN_DIR)
        absence[name] = {"matches": out.stdout.strip().split("\n")
                         if out.stdout.strip() else []}
    hashes["absence_checks"] = absence
    print("absence: OrchardPrivacy matches: %s"
          % absence["OrchardPrivacy"]["matches"])

    with open(os.path.join(PACK, "fixtures", "source-hashes.json"),
              "w", encoding="utf-8") as fh:
        json.dump(hashes, fh, indent=1, sort_keys=True)
    print("extract_excerpts: %d excerpts, %d whole files"
          % (len(SPECS), len(WHOLE_FILES)))


if __name__ == "__main__":
    main()
