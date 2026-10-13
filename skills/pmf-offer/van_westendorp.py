#!/usr/bin/env python3
"""Van Westendorp price analysis for the pmf pack.

Reads the four price answers per buyer (from a panel or a CSV) and reports the
acceptable price range: marginal cheapness, marginal expensiveness, the
optimal price point, the indifference price, and where a given price sits.

Usage:
  van_westendorp.py --panel pmf/panel [--price 4.50]
  van_westendorp.py --csv prices.csv [--price 4.50]

CSV format: one row per buyer, columns too_cheap,cheap,expensive,too_expensive.
"""

import argparse
import csv
import glob
import json
import os
import statistics
import sys

KEYS = ("too_cheap", "cheap", "expensive", "too_expensive")
THIN = 8


def die(msg):
    sys.exit("van_westendorp.py: " + msg)


def load_panel(dirpath):
    paths = sorted(glob.glob(os.path.join(dirpath, "answers", "*.json")))
    if not paths:
        die("no answers in %s/answers; run the panel first or pass --csv" % dirpath)
    rows = []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except ValueError:
            die("%s is not valid JSON" % path)
        price = data.get("price", {})
        if all(isinstance(price.get(k), (int, float)) for k in KEYS):
            rows.append([float(price[k]) for k in KEYS])
    if not rows:
        die("no answers with all four price fields in %s/answers" % dirpath)
    return rows


def load_csv(path):
    rows = []
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                rows.append([float(row[k]) for k in KEYS])
            except (KeyError, TypeError, ValueError):
                die("CSV needs columns %s with numbers in every row" % ",".join(KEYS))
    if not rows:
        die("CSV has no rows: %s" % path)
    return rows


def crossing(values_down, values_up):
    """First price where the falling curve moves below the rising one.

    values_down: answers whose curve falls as price rises (too cheap, a deal).
    values_up: answers whose curve rises as price rises (expensive, too much).
    Returns the interpolated intersection, or None when the curves never cross.
    """
    n = float(len(values_down))
    grid = sorted(set(values_down) | set(values_up))
    grid = sorted(set(grid + [(a + b) / 2.0 for a, b in zip(grid, grid[1:])]))
    last_diff = None
    prev = None
    up_n = float(len(values_up))
    for p in grid:
        down = sum(1 for v in values_down if v >= p) / n
        up = sum(1 for v in values_up if v <= p) / up_n
        diff = down - up
        if last_diff is not None and last_diff >= 0 > diff:
            return round(prev + (p - prev) * (last_diff / (last_diff - diff)), 2)
        last_diff = diff
        prev = p
    return None


def main():
    parser = argparse.ArgumentParser(description="Van Westendorp price analysis (curve based).")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--panel", help="panel directory, e.g. pmf/panel")
    source.add_argument("--csv", help="CSV with the four price columns")
    parser.add_argument("--price", type=float, help="a price to place against the range")
    args = parser.parse_args()

    rows = load_panel(args.panel) if args.panel else load_csv(args.csv)
    n = len(rows)
    cols = list(zip(*rows))

    pmc = crossing(cols[0], cols[2])   # too cheap meets expensive
    pme = crossing(cols[1], cols[3])   # a deal meets too expensive
    opp = crossing(cols[0], cols[3])   # too cheap meets too expensive
    idp = crossing(cols[1], cols[2])   # a deal meets expensive

    med = {k: round(statistics.median(cols[i]), 2) for i, k in enumerate(KEYS)}

    def show(v):
        return "%.2f" % v if v is not None else "not reached (the answers do not cross)"

    print("Van Westendorp price analysis, %d buyers" % n)
    if n < THIN:
        print("WARNING: %d answers is a thin sample; treat every point as noisy." % n)
    print("")
    print("Medians: too cheap %.2f | good deal %.2f | getting expensive %.2f | too expensive %.2f"
          % (med["too_cheap"], med["cheap"], med["expensive"], med["too_expensive"]))
    print("")
    print("Marginal cheapness (PMC): %s" % show(pmc))
    print("Marginal expensiveness (PME): %s" % show(pme))
    if pmc is not None and pme is not None:
        print("Acceptable range: %.2f to %.2f" % (pmc, pme))
    else:
        print("Acceptable range: not reached")
    print("Optimal price point (OPP): %s" % show(opp))
    print("Indifference price point (IDP): %s" % show(idp))

    if args.price is not None:
        print("")
        if pmc is not None and pme is not None:
            if args.price < pmc:
                verdict = "BELOW the acceptable range: buyers may read it as too cheap to trust"
            elif args.price > pme:
                verdict = "ABOVE the acceptable range: buyers may read it as too expensive"
            else:
                verdict = "WITHIN the acceptable range"
        else:
            verdict = "range not reached; fall back to the medians above"
        print("At %.2f: %s" % (args.price, verdict))

    print("")
    print("Method: curve intersections from the four answers per buyer, the standard")
    print("Van Westendorp reading. Answers come from a simulated panel or a real")
    print("survey; both are opinions about price, not proof of willingness to pay.")


if __name__ == "__main__":
    main()
