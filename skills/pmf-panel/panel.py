#!/usr/bin/env python3
"""Buyer panel bookkeeping for the pmf pack.

Deals buyer cards from a target-customer profile, checks the answers and
tallies them. It never answers for a buyer.

Usage:
  panel.py init --customer pmf/customer.json --pitch pmf/pitch.md [--n 100] [--seed 7] [--dir pmf/panel]
  panel.py check [--dir pmf/panel]
  panel.py tally [--dir pmf/panel]
"""

import argparse
import json
import os
import random
import statistics
import sys

PRICE_KEYS = ("too_cheap", "cheap", "expensive", "too_expensive")


def die(msg):
    sys.exit("panel.py: " + msg)


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        die("no such file: %s" % path)
    except ValueError as exc:
        die("%s is not valid JSON: %s" % (path, exc))


def weighted_choice(rng, items, weights):
    total = sum(weights)
    point = rng.uniform(0, total)
    upto = 0.0
    for item, weight in zip(items, weights):
        upto += weight
        if point <= upto:
            return item
    return items[-1]


def valid_customer(c):
    for field in ("business", "target", "segments", "behaviours", "objections"):
        if field not in c:
            die("customer file: missing field '%s'" % field)
    if not c["segments"] or not c["behaviours"] or not c["objections"]:
        die("customer file: segments, behaviours and objections cannot be empty")
    for seg in c["segments"]:
        for field in ("name", "share", "income"):
            if field not in seg:
                die("customer file: a segment is missing '%s'" % field)
        if not isinstance(seg["income"], list) or len(seg["income"]) != 2:
            die("customer file: segment '%s' income must be [low, high]" % seg["name"])
        if seg["income"][0] > seg["income"][1]:
            die("customer file: segment '%s' has income low above high" % seg["name"])
    for beh in c["behaviours"]:
        for field in ("name", "share", "how"):
            if field not in beh:
                die("customer file: a behaviour is missing '%s'" % field)


def cmd_init(args):
    customer = load_json(args.customer)
    valid_customer(customer)
    if not os.path.isfile(args.pitch):
        die("no such file: %s" % args.pitch)
    pitch = read_text(args.pitch).strip()
    if not pitch:
        die("pitch file is empty: %s" % args.pitch)
    if args.n < 1:
        die("--n must be at least 1")

    rng = random.Random(args.seed)
    cards_dir = os.path.join(args.dir, "cards")
    answers_dir = os.path.join(args.dir, "answers")
    os.makedirs(cards_dir, exist_ok=True)
    os.makedirs(answers_dir, exist_ok=True)

    segments = customer["segments"]
    behaviours = customer["behaviours"]
    objections = customer["objections"]
    habits = customer.get("habits", [])

    buyers = []
    for i in range(1, args.n + 1):
        seg = weighted_choice(rng, segments, [s["share"] for s in segments])
        beh = weighted_choice(rng, behaviours, [b["share"] for b in behaviours])
        income = rng.randint(seg["income"][0], seg["income"][1])
        objection = rng.choice(objections)
        habit = rng.choice(habits) if habits else ""
        bid = "B%03d" % i
        buyers.append({"id": bid, "segment": seg["name"], "behaviour": beh["name"]})

        lines = [
            "# Buyer %s" % bid,
            "",
            "- Segment: %s | Income: %s" % (seg["name"], income),
            "- Buying behaviour: %s. %s" % (beh["name"], beh["how"]),
            "- Doubt you carry: %s" % objection,
        ]
        if habit:
            lines.append("- Everyday context: %s" % habit)
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
            "Write `answers/%s.json` next to the cards with exactly this shape:" % bid,
            "",
            "```json",
            json.dumps({
                "buyer": bid,
                "buys": False,
                "reason": "why, in your words, as this buyer",
                "flip": "what would change your no into a yes (empty if you buy)",
                "price": {k: 0 for k in PRICE_KEYS},
            }, indent=2),
            "```",
            "",
            "`price` is four numbers: at what price it feels too cheap to trust,",
            "a good deal, getting expensive, too expensive to consider.",
            "",
        ]
        with open(os.path.join(cards_dir, bid + ".md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))

    manifest = {
        "n": args.n,
        "seed": args.seed,
        "business": customer["business"],
        "target": customer["target"],
        "buyers": buyers,
    }
    with open(os.path.join(args.dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    print("dealt %d buyer cards to %s" % (args.n, cards_dir))
    print("each buyer writes one JSON file to %s" % answers_dir)


def read_answers(args):
    manifest = load_json(os.path.join(args.dir, "manifest.json"))
    answers = []
    problems = []
    for b in manifest["buyers"]:
        path = os.path.join(args.dir, "answers", b["id"] + ".json")
        if not os.path.isfile(path):
            problems.append("%s: no answer file" % b["id"])
            continue
        try:
            data = load_json(path)
        except SystemExit:
            problems.append("%s: invalid JSON" % b["id"])
            continue
        missing = [k for k in ("buys", "reason", "price") if k not in data]
        if missing:
            problems.append("%s: missing keys: %s" % (b["id"], ", ".join(missing)))
            continue
        if not isinstance(data["price"], dict):
            problems.append("%s: price must be an object" % b["id"])
            continue
        bad = [k for k in PRICE_KEYS if not isinstance(data["price"].get(k), (int, float))]
        if bad:
            problems.append("%s: price missing numbers: %s" % (b["id"], ", ".join(bad)))
            continue
        answers.append({**b, **data})
    return manifest, answers, problems


def cmd_check(args):
    if not os.path.isfile(os.path.join(args.dir, "manifest.json")):
        die("no panel at %s; run init first" % args.dir)
    manifest, answers, problems = read_answers(args)
    print("%d of %d buyers answered" % (len(answers), manifest["n"]))
    for p in problems:
        print("  " + p)
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
    for k in PRICE_KEYS:
        values = [a["price"][k] for a in answers]
        out[k] = round(statistics.median(values), 2) if values else None
    return out


def cmd_tally(args):
    manifest, answers, problems = read_answers(args)
    if not answers:
        die("no valid answers in %s; nothing to tally" % args.dir)
    buy_rate = rate(answers)
    by_segment = group_rate(answers, "segment")
    by_behaviour = group_rate(answers, "behaviour")
    price = medians(answers)
    no_reasons = [{"buyer": a["id"], "segment": a["segment"], "reason": a["reason"]}
                  for a in answers if not a.get("buys") and a.get("reason")]
    flips = [{"buyer": a["id"], "segment": a["segment"], "flip": a["flip"]}
             for a in answers if not a.get("buys") and a.get("flip")]

    results = {
        "n": manifest["n"],
        "answered": len(answers),
        "unanswered": len(problems),
        "buy_rate": buy_rate,
        "by_segment": by_segment,
        "by_behaviour": by_behaviour,
        "price": price,
        "business": manifest.get("business", ""),
        "target": manifest.get("target", ""),
    }
    with open(os.path.join(args.dir, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
        fh.write("\n")

    lines = [
        "# Buyer panel results",
        "",
        "- Buy rate: %s (%d of %d answered)" % (
            ("%.0f%%" % (buy_rate * 100)) if buy_rate is not None else "n/a",
            len(answers), manifest["n"]),
        "- Unanswered: %d" % len(problems),
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
        lines.append("- %s (%s): \"%s\"" % (r["buyer"], r["segment"], r["reason"].strip()))
    lines += ["", "## What would flip a no", ""]
    for r in flips:
        lines.append("- %s (%s): \"%s\"" % (r["buyer"], r["segment"], r["flip"].strip()))
    lines.append("")
    with open(os.path.join(args.dir, "results.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote %s and %s" % (os.path.join(args.dir, "results.json"), os.path.join(args.dir, "results.md")))
    if problems:
        print("%d buyers did not answer; rates are over the %d who did" % (len(problems), len(answers)))


def main():
    parser = argparse.ArgumentParser(description="Buyer panel bookkeeping for the pmf pack.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="deal buyer cards from a customer profile and a pitch")
    p_init.add_argument("--customer", required=True)
    p_init.add_argument("--pitch", required=True)
    p_init.add_argument("--n", type=int, default=100)
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
    args.func(args)


if __name__ == "__main__":
    main()
