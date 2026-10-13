#!/usr/bin/env python3
"""Compiles the pmf state folder into a business plan with a computed verdict.

The verdict is computed, never written: Profitable, Not yet (with the failing
numbers) or Incomplete (with what is missing). Recomputes the load-bearing
numbers from numbers.json so the plan cannot drift from its inputs.

Usage:
  compile.py --dir pmf [--check] [--min-buy-rate 0.25]
"""

import argparse
import json
import math
import os
import sys

ARTIFACTS = [
    ("idea.md", "pmf-pressure"),
    ("pressure.md", "pmf-pressure"),
    ("research/market.md", "pmf-research"),
    ("research/voice.md", "pmf-research"),
    ("research/reach.md", "pmf-research"),
    ("customer.json", "pmf-panel"),
    ("pitch.md", "pmf-panel"),
    ("panel/results.json", "pmf-panel"),
    ("offer.md", "pmf-offer"),
    ("numbers.json", "pmf-numbers"),
    ("numbers.md", "pmf-numbers"),
    ("build.md", "pmf-build"),
    ("marketing.md", "pmf-marketing"),
    ("brand.md", "pmf-brand"),
    ("ops.md", "pmf-ops"),
    ("launch.md", "pmf-launch"),
]


def die(msg):
    sys.exit("compile.py: " + msg)


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def numbers_check(data):
    price = float(data["price"])
    variable = float(data["variable"])
    fixed = float(data["fixed_monthly"])
    contribution = price - variable
    ramp = data["ramp_per_day"]
    units = lambda per_day: per_day * 30
    year1_operating = sum(price * units(r) - variable * units(r) - fixed for r in ramp)
    break_even = math.ceil(fixed / (contribution * 30)) if contribution > 0 else None
    capacity = data.get("capacity_per_day")
    fits = None if capacity is None else (break_even is not None and break_even <= capacity)
    return {
        "contribution": round(contribution, 2),
        "break_even_day": break_even,
        "capacity": capacity,
        "fits": fits,
        "year1_operating": round(year1_operating, 2),
        "price": price,
    }


def main():
    parser = argparse.ArgumentParser(description="Compile the pmf plan and its verdict.")
    parser.add_argument("--dir", default="pmf")
    parser.add_argument("--check", action="store_true", help="print the checks, write nothing")
    parser.add_argument("--min-buy-rate", type=float, default=0.25,
                        help="the share of simulated buyers that must buy (default 0.25)")
    args = parser.parse_args()

    numbers_path = os.path.join(args.dir, "numbers.json")
    panel_path = os.path.join(args.dir, "panel", "results.json")

    missing = [p for p in (numbers_path, panel_path) if not os.path.isfile(p)]
    checks = []
    verdict = "Incomplete"

    if not missing:
        data = load_json(numbers_path)
        num = numbers_check(data)
        panel = load_json(panel_path)
        buy_rate = panel.get("buy_rate")

        checks.append(("Each unit earns money", num["contribution"] > 0,
                       "contribution per unit %.2f" % num["contribution"]))
        checks.append(("Year 1 makes an operating profit", num["year1_operating"] > 0,
                       "year 1 operating %.2f" % num["year1_operating"]))
        if num["fits"] is None:
            checks.append(("Break-even fits capacity", True,
                           "not checked: no capacity_per_day given"))
        else:
            checks.append(("Break-even fits capacity", num["fits"],
                           "break-even %s per day against capacity %s"
                           % (num["break_even_day"], num["capacity"])))
        checks.append(("Enough simulated buyers buy",
                       buy_rate is not None and buy_rate >= args.min_buy_rate,
                       "buy rate %s against a %.0f%% bar"
                       % (("%.0f%%" % (buy_rate * 100)) if buy_rate is not None else "n/a",
                          args.min_buy_rate * 100)))
        verdict = "Profitable" if all(ok for _, ok, _ in checks) else "Not yet"

    if args.check or missing:
        print("Verdict: %s" % verdict)
        if missing:
            print("Missing (the verdict cannot compute without these):")
            for p in missing:
                skill = next(s for a, s in ARTIFACTS if p.endswith(a))
                print("  %s  (run %s)" % (p, skill))
        for name, ok, detail in checks:
            print("  [%s] %s: %s" % ("pass" if ok else "FAIL", name, detail))
        if args.check:
            return

    name = "the business"
    idea_path = os.path.join(args.dir, "idea.md")
    if os.path.isfile(idea_path):
        with open(idea_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("# "):
                    name = line[2:].strip()
                    break

    lines = ["# Business plan: %s" % name, "", "Verdict: **%s**" % verdict, ""]
    if missing:
        lines.append("The plan cannot be completed yet. Missing:")
        lines.append("")
        for p in missing:
            skill = next(s for a, s in ARTIFACTS if p.endswith(a))
            lines.append("- `%s` (run `%s`)" % (p, skill))
    else:
        lines += ["## The checks", "", "| check | result | the numbers |", "| --- | --- | --- |"]
        for check_name, ok, detail in checks:
            lines.append("| %s | %s | %s |" % (check_name, "pass" if ok else "FAIL", detail))
        lines += [
            "",
            "## Key numbers",
            "",
            "- Price per unit: %.2f" % num["price"],
            "- Contribution per unit: %.2f" % num["contribution"],
            "- Break-even: %s per day" % num["break_even_day"],
            "- Year 1 operating profit: %.2f" % num["year1_operating"],
        ]

    lines += ["", "## Artifact index", "", "| file | status | owning skill |", "| --- | --- | --- |"]
    for rel, skill in ARTIFACTS:
        exists = os.path.isfile(os.path.join(args.dir, rel))
        lines.append("| `%s` | %s | `%s` |" % (rel, "present" if exists else "missing", skill))
    lines += [
        "",
        "---",
        "",
        "Generated by compile.py from the files above. Edit the inputs and rerun;",
        "never edit this file by hand. The panel is simulated and the numbers are",
        "estimates until real quotes and a real test replace them. Not financial,",
        "legal or tax advice.",
        "",
    ]

    plan_path = os.path.join(args.dir, "plan.md")
    with open(plan_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote %s (verdict: %s)" % (plan_path, verdict))
    if verdict != "Profitable":
        sys.exit(1)


if __name__ == "__main__":
    main()
