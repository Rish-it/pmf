#!/usr/bin/env python3
"""Buyer panel bookkeeping for the pmf pack.

Deals buyer cards from a target-customer profile with exact quotas, so the
panel's segment and behaviour mix matches the profile by construction and
cannot drift between runs. Checks the answers strictly and tallies them.
It never answers for a buyer.

Usage:
  panel.py init --customer pmf/customer.json --pitch pmf/pitch.md [--n 30] [--seed 7] [--dir pmf/panel]
  panel.py init --reuse pmf/panel --pitch pmf/pitch.md [--dir pmf/panel]
  panel.py check [--dir pmf/panel]
  panel.py tally [--dir pmf/panel]
"""

import argparse
import hashlib
import json
import os
import random
import shutil
import statistics
import sys
from datetime import datetime, timezone

PRICE_KEYS = ("too_cheap", "cheap", "expensive", "too_expensive")
ANSWER_KEYS = ("buyer", "buys", "reason", "flip", "price")


class PanelError(Exception):
    pass


def _stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise PanelError("no such file: %s" % path)
    except ValueError as exc:
        raise PanelError("%s is not valid JSON: %s" % (path, exc))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _share(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise PanelError("customer file: %s must be a number above zero" % where)
    return float(value)


def _quota(items, n):
    """Split n across items by their shares exactly (largest remainder)."""
    total = sum(_share(it["share"], "a share") for it in items)
    raw = [n * _share(it["share"], "a share") / total for it in items]
    counts = [int(r) for r in raw]
    order = sorted(range(len(items)), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in order[: n - sum(counts)]:
        counts[i] += 1
    return counts


def valid_customer(c):
    for field in ("business", "target", "segments", "behaviours", "objections"):
        if field not in c or c[field] in ("", [], None):
            raise PanelError("customer file: missing field '%s'" % field)
    for seg in c["segments"]:
        for field in ("name", "share", "income"):
            if field not in seg:
                raise PanelError("customer file: a segment is missing '%s'" % field)
        if not isinstance(seg["income"], list) or len(seg["income"]) != 2:
            raise PanelError("customer file: segment '%s' income must be [low, high]" % seg["name"])
        if isinstance(seg["income"][0], bool) or isinstance(seg["income"][1], bool) \
                or not all(isinstance(v, (int, float)) for v in seg["income"]):
            raise PanelError("customer file: segment '%s' income must be two numbers" % seg["name"])
        if seg["income"][0] > seg["income"][1]:
            raise PanelError("customer file: segment '%s' has income low above high" % seg["name"])
    for beh in c["behaviours"]:
        for field in ("name", "share", "how"):
            if field not in beh:
                raise PanelError("customer file: a behaviour is missing '%s'" % field)


def deal(customer, n, rng):
    """Deal n buyers: exact quotas for segments and behaviours, then shuffled."""
    segments = customer["segments"]
    behaviours = customer["behaviours"]
    segs = []
    for seg, count in zip(segments, _quota(segments, n)):
        segs += [seg] * count
    behs = []
    for beh, count in zip(behaviours, _quota(behaviours, n)):
        behs += [beh] * count
    rng.shuffle(segs)
    rng.shuffle(behs)
    objections = customer["objections"]
    habits = customer.get("habits") or []
    buyers = []
    for i in range(n):
        seg, beh = segs[i], behs[i]
        buyers.append({
            "id": "B%03d" % (i + 1),
            "segment": seg["name"],
            "behaviour": beh["name"],
            "behaviour_how": beh.get("how", ""),
            "income": rng.randint(int(seg["income"][0]), int(seg["income"][1])),
            "objection": rng.choice(objections),
            "habit": rng.choice(habits) if habits else "",
        })
    return buyers


def archive(panel_dir, names):
    """Move the named files or folders into runs/<stamp>/.

    Returns the folder name used, or None when there was nothing to move.
    """
    stamp = _stamp()
    runs = os.path.join(panel_dir, "runs", stamp)
    moved = False
    for name in names:
        src = os.path.join(panel_dir, name)
        if os.path.isdir(src):
            if os.listdir(src):
                os.makedirs(runs, exist_ok=True)
                shutil.move(src, os.path.join(runs, name))
                moved = True
            else:
                os.rmdir(src)
        elif os.path.isfile(src):
            os.makedirs(runs, exist_ok=True)
            shutil.move(src, os.path.join(runs, name))
            moved = True
    return stamp if moved else None


def archive_run(panel_dir):
    """Archive a whole run before dealing a new one."""
    return archive(panel_dir, ("answers", "manifest.json", "results.json", "results.md"))


def archive_results(panel_dir):
    """Archive the previous tally before overwriting it."""
    return archive(panel_dir, ("results.json", "results.md"))


def card_text(buyer, pitch):
    lines = [
        "# Buyer %s" % buyer["id"],
        "",
        "- Segment: %s | Income: %s" % (buyer["segment"], buyer["income"]),
        "- Buying behaviour: %s. %s" % (buyer["behaviour"], buyer.get("behaviour_how", "")),
        "- Doubt you carry: %s" % buyer["objection"],
    ]
    if buyer.get("habit"):
        lines.append("- Everyday context: %s" % buyer["habit"])
    lines += [
        "",
        "You are this buyer. You cannot see the other buyers or the maker.",
        "Answer as this person, in your own words, from what you know of your",
        "own life. Do not be polite for the sake of the maker.",
        "",
        "## What you see",
        "",
        pitch,
        "",
        "## Answer file",
        "",
        "Write `answers/%s.json` with exactly this shape:" % buyer["id"],
        "",
        "```json",
        json.dumps({
            "buyer": buyer["id"],
            "buys": False,
            "reason": "why, in your words, as this buyer",
            "flip": "what would change your no into a yes (empty if you buy)",
            "price": {k: 0 for k in PRICE_KEYS},
        }, indent=2),
        "```",
        "",
        "`buys` is a JSON boolean: true or false, not text. `reason` is required.",
        "`flip` is empty when you buy and required when you do not. `price` is",
        "four numbers that must climb in order: too cheap to trust, a good deal,",
        "getting expensive, too expensive to consider.",
        "",
    ]
    return "\n".join(lines)


def cmd_init(args):
    if not os.path.isfile(args.pitch):
        raise PanelError("no such file: %s" % args.pitch)
    pitch = read_text(args.pitch).strip()
    if not pitch:
        raise PanelError("pitch file is empty: %s" % args.pitch)

    if args.reuse and args.customer:
        raise PanelError("give either --customer or --reuse, not both")
    if args.reuse:
        old = load_json(os.path.join(args.reuse, "manifest.json"))
        buyers = old.get("buyers") or []
        if not buyers or "objection" not in buyers[0]:
            raise PanelError("the panel at %s has no buyer details to reuse; run a fresh init" % args.reuse)
        business = old.get("business", "")
        target = old.get("target", "")
        customer_hash = old.get("customer_sha256", "")
        seed = old.get("seed")
    else:
        if not args.customer:
            raise PanelError("give --customer, or --reuse with a previous panel folder")
        customer = load_json(args.customer)
        valid_customer(customer)
        if args.n < 1:
            raise PanelError("--n must be at least 1")
        buyers = deal(customer, args.n, random.Random(args.seed))
        business = customer["business"]
        target = customer["target"]
        customer_hash = sha256_file(args.customer)
        seed = args.seed

    os.makedirs(args.dir, exist_ok=True)
    archived = archive_run(args.dir)
    cards_dir = os.path.join(args.dir, "cards")
    answers_dir = os.path.join(args.dir, "answers")
    os.makedirs(cards_dir, exist_ok=True)
    os.makedirs(answers_dir, exist_ok=True)
    for name in os.listdir(cards_dir):
        full = os.path.join(cards_dir, name)
        if os.path.isfile(full):
            os.unlink(full)

    for buyer in buyers:
        with open(os.path.join(cards_dir, buyer["id"] + ".md"), "w", encoding="utf-8") as fh:
            fh.write(card_text(buyer, pitch))

    manifest = {
        "n": len(buyers),
        "seed": seed,
        "business": business,
        "target": target,
        "created": _now(),
        "pitch_sha256": sha256_file(args.pitch),
        "customer_sha256": customer_hash,
        "buyers": buyers,
    }
    with open(os.path.join(args.dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    print("dealt %d buyer cards to %s" % (len(buyers), cards_dir))
    print("each buyer writes one JSON file to %s" % answers_dir)
    if archived:
        print("the previous run was kept in %s" % os.path.join(args.dir, "runs", archived))
    if args.reuse:
        print("buyer roster reused from %s; the composition is identical" % args.reuse)


def parse_answer(path, buyer_id):
    """Return (answer, None) or (None, problem). Strict: a typo is a problem."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return None, "no answer file"
    except ValueError:
        return None, "invalid JSON"
    if not isinstance(data, dict):
        return None, "the answer must be one JSON object"
    unknown = sorted(set(data) - set(ANSWER_KEYS))
    if unknown:
        return None, "unknown keys %s; a card shows the exact shape" % ", ".join(unknown)
    missing = [k for k in ANSWER_KEYS if k not in data]
    if missing:
        return None, "missing keys: %s" % ", ".join(missing)
    if data["buyer"] != buyer_id:
        return None, "buyer is %r but the file is %s" % (data["buyer"], buyer_id)
    if not isinstance(data["buys"], bool):
        return None, "buys must be true or false (a JSON boolean), not %r" % (data["buys"],)
    if not isinstance(data["reason"], str) or not data["reason"].strip():
        return None, "reason must be a non-empty line of text"
    if not isinstance(data["flip"], str):
        return None, "flip must be text (empty when the buyer buys)"
    if not data["buys"] and not data["flip"].strip():
        return None, "flip must say what would change a no into a yes"
    price = data["price"]
    if not isinstance(price, dict):
        return None, "price must be an object with the four numbers"
    unknown = sorted(set(price) - set(PRICE_KEYS))
    if unknown:
        return None, "price has unknown keys: %s" % ", ".join(unknown)
    missing = [k for k in PRICE_KEYS if k not in price]
    if missing:
        return None, "price is missing: %s" % ", ".join(missing)
    values = {}
    for key in PRICE_KEYS:
        value = price[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None, "price.%s must be a number" % key
        if value < 0:
            return None, "price.%s cannot be negative" % key
        values[key] = float(value)
    ordered = [values[k] for k in PRICE_KEYS]
    if ordered != sorted(ordered):
        return None, ("the four price answers must climb in order: too cheap <= good deal"
                      " <= getting expensive <= too expensive (got %s)"
                      % ", ".join("%g" % v for v in ordered))
    data["price"] = values
    return data, None


def read_panel(dirpath):
    manifest_path = os.path.join(dirpath, "manifest.json")
    if not os.path.isfile(manifest_path):
        raise PanelError("no panel at %s; run init first" % dirpath)
    manifest = load_json(manifest_path)
    answers, problems = [], []
    for buyer in manifest["buyers"]:
        path = os.path.join(dirpath, "answers", buyer["id"] + ".json")
        data, problem = parse_answer(path, buyer["id"])
        if problem:
            problems.append("%s: %s" % (buyer["id"], problem))
            continue
        answers.append({**buyer, **data})
    return manifest, answers, problems


def cmd_check(args):
    manifest, answers, problems = read_panel(args.dir)
    print("%d of %d buyers answered" % (len(answers), manifest["n"]))
    for problem in problems:
        print("  " + problem)
    if problems:
        sys.exit(1)


def rate(rows):
    if not rows:
        return None
    bought = sum(1 for r in rows if r.get("buys"))
    return round(float(bought) / len(rows), 4)


def group_rate(answers, key):
    groups = {}
    for a in answers:
        groups.setdefault(a[key], []).append(a)
    return {name: {"n": len(rows), "buy_rate": rate(rows)} for name, rows in sorted(groups.items())}


def medians(answers):
    out = {}
    for key in PRICE_KEYS:
        values = [a["price"][key] for a in answers]
        out[key] = round(statistics.median(values), 2) if values else None
    return out


def previous_runs(dirpath):
    runs_dir = os.path.join(dirpath, "runs")
    found = []
    if os.path.isdir(runs_dir):
        for name in sorted(os.listdir(runs_dir)):
            path = os.path.join(runs_dir, name, "results.json")
            if os.path.isfile(path):
                try:
                    found.append(load_json(path))
                except PanelError:
                    continue
    return sorted(found, key=lambda r: r.get("created", ""))


def cmd_tally(args):
    manifest, answers, problems = read_panel(args.dir)
    if not answers:
        raise PanelError("no valid answers in %s; nothing to tally" % args.dir)
    buy_rate = rate(answers)
    by_segment = group_rate(answers, "segment")
    by_behaviour = group_rate(answers, "behaviour")
    price = medians(answers)
    no_reasons = [{"buyer": a["id"], "segment": a["segment"], "reason": a["reason"].strip()}
                  for a in answers if not a["buys"] and a["reason"].strip()]
    flips = [{"buyer": a["id"], "segment": a["segment"], "flip": a["flip"].strip()}
             for a in answers if not a["buys"] and a["flip"].strip()]

    if os.path.isfile(os.path.join(args.dir, "results.json")):
        archive_results(args.dir)

    results = {
        "n": manifest["n"],
        "answered": len(answers),
        "unanswered": len(problems),
        "coverage": round(len(answers) / float(manifest["n"]), 4),
        "buy_rate": buy_rate,
        "by_segment": by_segment,
        "by_behaviour": by_behaviour,
        "price": price,
        "business": manifest.get("business", ""),
        "target": manifest.get("target", ""),
        "created": _now(),
        "pitch_sha256": manifest.get("pitch_sha256", ""),
        "customer_sha256": manifest.get("customer_sha256", ""),
    }
    with open(os.path.join(args.dir, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
        fh.write("\n")

    lines = [
        "# Buyer panel results",
        "",
        "- Buy rate: %s (%d of %d answered, coverage %.0f%%)" % (
            ("%.0f%%" % (buy_rate * 100)) if buy_rate is not None else "n/a",
            len(answers), manifest["n"], results["coverage"] * 100),
        "- Unanswered or invalid: %d" % len(problems),
        "",
        "A simulated buy rate is an upper bound for finding objections and wording,",
        "not a conversion forecast. The real verdict comes from a real-world test",
        "(see pmf-test).",
        "",
        "Segment and behaviour counts match the customer profile by construction",
        "(exact quotas), so two runs against the same profile stay comparable.",
        "",
        "## Buy rate by segment",
        "",
        "| segment | answered | buy rate |",
        "| --- | --- | --- |",
    ]
    for name, g in by_segment.items():
        lines.append("| %s | %d | %.0f%% |" % (name, g["n"], (g["buy_rate"] or 0) * 100))
    lines += ["", "## Buy rate by behaviour", "", "| behaviour | answered | buy rate |", "| --- | --- | --- |"]
    for name, g in by_behaviour.items():
        lines.append("| %s | %d | %.0f%% |" % (name, g["n"], (g["buy_rate"] or 0) * 100))
    lines += [
        "",
        "## Price answers (medians)",
        "",
        "| too cheap | good deal | getting expensive | too expensive |",
        "| --- | --- | --- | --- |",
        "| %s | %s | %s | %s |" % (price["too_cheap"], price["cheap"], price["expensive"], price["too_expensive"]),
        "",
        "## Why buyers passed, in their words",
        "",
    ]
    for r in no_reasons:
        lines.append("- %s (%s): \"%s\"" % (r["buyer"], r["segment"], r["reason"]))
    lines += ["", "## What would flip a no", ""]
    for r in flips:
        lines.append("- %s (%s): \"%s\"" % (r["buyer"], r["segment"], r["flip"]))
    runs = previous_runs(args.dir)
    if runs:
        lines += [
            "",
            "## Runs so far",
            "",
            "| recorded | answered | buy rate | notes |",
            "| --- | --- | --- | --- |",
        ]
        for run in runs:
            note = "" if run.get("pitch_sha256") == results["pitch_sha256"] else "a different pitch"
            run_rate = run.get("buy_rate")
            rate_text = "n/a" if run_rate is None else "%.0f%%" % (run_rate * 100)
            lines.append("| %s | %d | %s | %s |"
                         % (run.get("created", "?"), run.get("answered", 0), rate_text, note))
        lines.append("| %s | %d | %.0f%% | this run |"
                     % (results["created"], results["answered"], (buy_rate or 0) * 100))
    lines.append("")
    with open(os.path.join(args.dir, "results.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote %s and %s" % (os.path.join(args.dir, "results.json"), os.path.join(args.dir, "results.md")))
    if problems:
        print("%d buyers did not answer or had an invalid answer; rates are over the %d valid ones"
              % (len(problems), len(answers)))


def main():
    parser = argparse.ArgumentParser(description="Buyer panel bookkeeping for the pmf pack.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="deal buyer cards from a customer profile and a pitch")
    p_init.add_argument("--customer", help="path to customer.json")
    p_init.add_argument("--reuse", help="a previous panel folder whose buyers should answer the new pitch")
    p_init.add_argument("--pitch", required=True)
    p_init.add_argument("--n", type=int, default=30, help="how many buyers (default 30)")
    p_init.add_argument("--seed", type=int, default=7)
    p_init.add_argument("--dir", default="pmf/panel")
    p_init.set_defaults(func=cmd_init)

    p_check = sub.add_parser("check", help="check the answers are present and shaped right")
    p_check.add_argument("--dir", default="pmf/panel")
    p_check.set_defaults(func=cmd_check)

    p_tally = sub.add_parser("tally", help="tally the answers into results.json and results.md")
    p_tally.add_argument("--dir", default="pmf/panel")
    p_tally.set_defaults(func=cmd_tally)

    args = parser.parse_args()
    try:
        args.func(args)
    except PanelError as exc:
        sys.exit("panel.py: %s" % exc)


if __name__ == "__main__":
    main()
