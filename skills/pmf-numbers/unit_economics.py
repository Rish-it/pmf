#!/usr/bin/env python3
"""Unit economics for the pmf pack.

Reads one JSON describing a business unit and reports what one sale earns, the
break-even, the margin at plan, year 1 month by month, the cash needed, the
payback month and what-ifs. Every number traces to an input; a missing field
is an error, never a guess.

Usage:
  unit_economics.py pmf/numbers.json [--out pmf/numbers.md]
"""

import argparse
import json
import math
import sys

REQUIRED = ("unit", "price", "variable", "fixed_monthly", "startup",
            "plan_per_day", "ramp_per_day")


def die(msg):
    sys.exit("unit_economics.py: " + msg)


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        die("no such file: %s" % path)
    except ValueError as exc:
        die("%s is not valid JSON: %s" % (path, exc))
    for field in REQUIRED:
        if field not in data:
            die("%s: missing field '%s'" % (path, field))
    for field in ("price", "variable", "fixed_monthly", "startup", "plan_per_day"):
        if not isinstance(data[field], (int, float)):
            die("%s: '%s' must be a number" % (path, field))
    ramp = data["ramp_per_day"]
    if not isinstance(ramp, list) or len(ramp) != 12 or not all(isinstance(v, (int, float)) for v in ramp):
        die("%s: 'ramp_per_day' must be 12 numbers, one per month of year 1" % path)
    if "capacity_per_day" in data and not isinstance(data["capacity_per_day"], (int, float)):
        die("%s: 'capacity_per_day' must be a number" % path)
    return data


def money(v):
    return "%.2f" % v


def year1(data, price=None, volume_scale=1.0, variable=None):
    price = data["price"] if price is None else price
    variable = data["variable"] if variable is None else variable
    rows = []
    cumulative = -float(data["startup"])
    for month, per_day in enumerate(data["ramp_per_day"], start=1):
        units = per_day * volume_scale * 30
        revenue = price * units
        variable_cost = variable * units
        operating = revenue - variable_cost - data["fixed_monthly"]
        cumulative += operating
        rows.append({"month": month, "units": units, "revenue": revenue,
                     "operating": operating, "cumulative": cumulative})
    return rows


def report(data, path):
    price = float(data["price"])
    variable = float(data["variable"])
    fixed = float(data["fixed_monthly"])
    startup = float(data["startup"])
    plan = float(data["plan_per_day"])
    capacity = data.get("capacity_per_day")

    contribution = price - variable
    if contribution <= 0:
        lines_warning = ["WARNING: each sale loses money (price %.2f, variable cost %.2f). " % (price, variable) +
                         "Fix the price or the cost before anything else counts."]
    else:
        lines_warning = []
    break_even_day = math.ceil(fixed / (contribution * 30)) if contribution > 0 else None

    monthly_revenue = price * plan * 30
    monthly_operating = monthly_revenue - variable * plan * 30 - fixed
    margin = (monthly_operating / monthly_revenue * 100.0) if monthly_revenue else 0.0

    rows = year1(data)
    year1_revenue = sum(r["revenue"] for r in rows)
    year1_operating = sum(r["operating"] for r in rows)
    lowest = min(r["cumulative"] for r in rows)
    cash_needed = max(0.0, -lowest)
    payback = next((r["month"] for r in rows if r["cumulative"] >= 0), None)

    out = []
    out.append("# Unit economics")
    out.append("")
    out.append("Inputs read from %s: unit '%s', price %s, variable cost %s, fixed %s per month,"
               % (path, data["unit"], money(price), money(variable), money(fixed)))
    out.append("startup %s, plan %s per day." % (money(startup), money(plan)))
    out.append("")
    for line in lines_warning:
        out.append(line)
        out.append("")
    out.append("## Per unit")
    out.append("")
    out.append("- Each %s leaves %s after its own costs." % (data["unit"], money(contribution)))
    if break_even_day is not None:
        out.append("- Break-even: %d %s per day cover the fixed costs." % (break_even_day, data["unit"] + "s"))
        if capacity is not None:
            fits = "fits" if break_even_day <= capacity else "does NOT fit"
            out.append("- Against capacity (%s per day): break-even %s." % (capacity, fits))
    out.append("")
    out.append("## At the planned volume (%s per day)" % money(plan))
    out.append("")
    out.append("- Monthly revenue %s, monthly operating profit %s, margin %.1f%%."
               % (money(monthly_revenue), money(monthly_operating), margin))
    out.append("")
    out.append("## Year 1, month by month")
    out.append("")
    out.append("| month | units/day | revenue | operating | cash after startup |")
    out.append("| --- | --- | --- | --- | --- |")
    for r, per_day in zip(rows, data["ramp_per_day"]):
        out.append("| %d | %g | %s | %s | %s |"
                   % (r["month"], per_day, money(r["revenue"]), money(r["operating"]), money(r["cumulative"])))
    out.append("")
    out.append("- Year 1 revenue: %s. Year 1 operating profit: %s." % (money(year1_revenue), money(year1_operating)))
    out.append("- Cash needed before it pays for itself: %s." % money(cash_needed))
    if payback is not None:
        out.append("- Startup spend is earned back in month %d." % payback)
    else:
        out.append("- Startup spend is not earned back inside year 1.")
    out.append("")
    out.append("## What-ifs")
    out.append("")

    low_price = year1(data, price=price * 0.9)
    low_price_op = sum(r["operating"] for r in low_price)
    out.append("- Price 10%% lower: each unit leaves %s, year 1 operating becomes %s."
               % (money(price * 0.9 - variable), money(low_price_op)))
    low_volume = year1(data, volume_scale=0.8)
    low_volume_op = sum(r["operating"] for r in low_volume)
    out.append("- Volume 20%% lower: year 1 operating becomes %s." % money(low_volume_op))
    high_cost = year1(data, variable=variable * 1.1)
    high_cost_op = sum(r["operating"] for r in high_cost)
    out.append("- Variable cost 10%% higher: each unit leaves %s, year 1 operating becomes %s."
               % (money(price - variable * 1.1), money(high_cost_op)))
    out.append("")
    out.append("Every number above is computed from the inputs listed at the top. Estimates")
    out.append("stay estimates until real quotes arrive; check costs, payroll and tax with")
    out.append("an accountant.")
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Unit economics for the pmf pack.")
    parser.add_argument("numbers", help="path to numbers.json")
    parser.add_argument("--out", help="write the report to this file as well")
    args = parser.parse_args()
    data = load(args.numbers)
    text = report(data, args.numbers)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
