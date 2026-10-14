#!/usr/bin/env python3
"""State ledger for the pmf pack.

Every stage records a fingerprint (sha256) of the file it wrote, together
with the files it read. The check then marks an artifact stale when any of
its recorded inputs changed after it was recorded, and stale again for
everything that depends on a stale artifact. Nothing is judged by
timestamps; only content hashes.

Statuses:
  fresh    the recorded inputs are unchanged
  stale    a recorded input changed, or a dependency is stale or missing
  changed  the artifact itself was rewritten after the last record
  missing  the artifact was recorded but the file is gone

Exit code: 1 when anything is stale, changed or missing, else 0.

Usage:
  status.py record --dir pmf --artifact numbers.md --input numbers.json [--skill pmf-numbers]
  status.py check --dir pmf [--json]
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

LEDGER = "status.json"
ORDER = {"stale": 0, "changed": 1, "missing": 2, "fresh": 3}


class StatusError(Exception):
    pass


def _clean_rel(value):
    rel = value.replace("\\", "/").strip("/")
    if not rel or rel.startswith("..") or os.path.isabs(value):
        raise StatusError("the path must stay inside the pmf folder: %r" % value)
    return rel


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def ledger_path(dirpath):
    return os.path.join(dirpath, LEDGER)


def read_ledger(dirpath):
    path = ledger_path(dirpath)
    if not os.path.isfile(path):
        return {"version": 1, "artifacts": {}}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except ValueError as exc:
        raise StatusError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(data, dict) or not isinstance(data.get("artifacts"), dict):
        raise StatusError("%s is not a status ledger; delete it and record again" % path)
    return data


def write_ledger(dirpath, ledger):
    path = ledger_path(dirpath)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def record(dirpath, artifact, inputs, skill):
    if not os.path.isdir(dirpath):
        raise StatusError("no such folder: %s" % dirpath)
    artifact = _clean_rel(artifact)
    full = os.path.join(dirpath, artifact)
    if not os.path.isfile(full):
        raise StatusError("no such artifact: %s" % full)
    input_hashes = {}
    for value in inputs:
        rel = _clean_rel(value)
        full_input = os.path.join(dirpath, rel)
        if not os.path.isfile(full_input):
            raise StatusError("no such input: %s" % full_input)
        input_hashes[rel] = file_hash(full_input)
    ledger = read_ledger(dirpath)
    ledger["version"] = 1
    ledger["artifacts"][artifact] = {
        "sha256": file_hash(full),
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skill": skill or "",
        "inputs": input_hashes,
    }
    write_ledger(dirpath, ledger)
    return artifact


def check(dirpath):
    """Return {"artifacts": [...], "counts": {...}} with the freshness computed."""
    ledger = read_ledger(dirpath)
    artifacts = ledger.get("artifacts", {})
    report = []
    for rel in sorted(artifacts):
        rec = artifacts[rel]
        full = os.path.join(dirpath, rel)
        reasons = []
        if not os.path.isfile(full):
            status = "missing"
            reasons.append("the file is gone")
        else:
            status = "fresh"
            if file_hash(full) != rec.get("sha256"):
                status = "changed"
                reasons.append("rewritten since it was recorded")
            for inp, recorded in sorted(rec.get("inputs", {}).items()):
                full_input = os.path.join(dirpath, inp)
                if not os.path.isfile(full_input):
                    reasons.append("input %s is gone" % inp)
                elif file_hash(full_input) != recorded:
                    reasons.append("input %s changed after this was recorded" % inp)
            if any(r.startswith("input ") for r in reasons):
                status = "stale"
        report.append({"artifact": rel, "status": status, "note": "; ".join(reasons),
                       "recorded_at": rec.get("recorded_at", ""),
                       "skill": rec.get("skill", "")})
    by_name = {r["artifact"]: r for r in report}
    queue = [r["artifact"] for r in report if r["status"] in ("stale", "missing")]
    seen = set(queue)
    while queue:
        current = queue.pop()
        for r in report:
            rel = r["artifact"]
            if rel in seen:
                continue
            if current in artifacts[rel].get("inputs", {}):
                if r["status"] not in ("stale", "missing"):
                    r["status"] = "stale"
                note = "depends on %s, which is %s" % (current, by_name[current]["status"])
                r["note"] = (r["note"] + "; " + note) if r["note"] else note
                seen.add(rel)
                queue.append(rel)
    counts = {"fresh": 0, "stale": 0, "changed": 0, "missing": 0}
    for r in report:
        counts[r["status"]] += 1
    return {"artifacts": report, "counts": counts}


def print_report(dirpath, report):
    counts = report["counts"]
    listed = sorted(report["artifacts"],
                    key=lambda r: (ORDER[r["status"]], r["artifact"]))
    if not listed:
        print("%s has no recorded artifacts yet; records appear as stages run." % dirpath)
        return
    print("%s tracks %d artifact%s:" % (dirpath, len(listed), "" if len(listed) == 1 else "s"))
    for r in listed:
        note = r["note"] or ("recorded %s" % r["recorded_at"] if r["recorded_at"] else "")
        print("  %-7s %-24s %s" % (r["status"], r["artifact"], note))
    print("%d fresh, %d stale, %d changed, %d missing."
          % (counts["fresh"], counts["stale"], counts["changed"], counts["missing"]))


def main():
    parser = argparse.ArgumentParser(description="State ledger for the pmf pack.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_record = sub.add_parser("record", help="fingerprint one artifact and its inputs")
    p_record.add_argument("--dir", default="pmf")
    p_record.add_argument("--artifact", required=True)
    p_record.add_argument("--input", action="append", default=[], dest="inputs")
    p_record.add_argument("--skill", default="", help="the skill that wrote the artifact")
    p_check = sub.add_parser("check", help="compute what is fresh, stale, changed or missing")
    p_check.add_argument("--dir", default="pmf")
    p_check.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "record":
            rel = record(args.dir, args.artifact, args.inputs, args.skill)
            print("recorded %s" % rel)
            return
        report = check(args.dir)
    except StatusError as exc:
        sys.exit("status.py: %s" % exc)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_report(args.dir, report)
    counts = report["counts"]
    bad = counts["stale"] + counts["changed"] + counts["missing"]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
