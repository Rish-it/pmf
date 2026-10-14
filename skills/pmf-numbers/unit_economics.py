#!/usr/bin/env python3
"""Unit economics for the pmf pack.

One JSON in, one report out: what each sale leaves, the break-even in units a
day, the margin at plan, year 1 month by month, the cash needed (including
the startup spend before month 1), the payback month, red flags and what-if
scenarios. Costs can be itemised, each line with an optional source.

Every number traces to an input. A missing field is an error, never a guess,
and an impossible volume (a plan or ramp above capacity) is an error too.

Usage:
  unit_economics.py pmf/numbers.json [--out pmf/numbers.md]
  unit_economics.py pmf/numbers.json --json
  unit_economics.py pmf/numbers.json --price 4.00 --volume 0.8
"""

import argparse
import json
import math
import sys

TOP_FIELDS = (
    "business", "unit", "price",
    "variable", "variable_items",
    "fixed_monthly", "fixed_items",
    "startup", "startup_items",
    "days_per_month", "plan_per_day", "ramp_per_day",
    "capacity_per_day", "scenarios",
)
SCENARIO_FIELDS = ("price", "volume_scale", "variable_scale", "fixed_scale")


class NumbersError(Exception):
    pass


def money(v):
    return "%.2f" % v


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        raise NumbersError("no such file: %s" % path)
    except ValueError as exc:
        raise NumbersError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(data, dict):
        raise NumbersError("%s: the top level must be one JSON object" % path)
    return data


def _number(value, where, minimum=None, above=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NumbersError("%s must be a number" % where)
    value = float(value)
    if above is not None and value <= above:
        raise NumbersError("%s must be above %g" % (where, above))
    if minimum is not None and value < minimum:
        raise NumbersError("%s must be %g or more" % (where, minimum))
    return value


def _whole(value, where, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NumbersError("%s must be a whole number" % where)
    if float(value) != int(value):
        raise NumbersError("%s must be a whole number" % where)
    value = int(value)
    if value < low or value > high:
        raise NumbersError("%s must be from %d to %d" % (where, low, high))
    return value


def _text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise NumbersError("%s must be a non-empty line of text" % where)
    return value.strip()


def _cost_items(data, flat, items_field, per):
    """Read one cost group from either a flat number or an itemised list."""
    if flat in data and items_field in data:
        raise NumbersError("give either '%s' or '%s', not both" % (flat, items_field))
    if items_field in data:
        raw = data[items_field]
        if not isinstance(raw, list) or not raw:
            raise NumbersError("'%s' must be a list with at least one item" % items_field)
        out = []
        for i, item in enumerate(raw):
            where = "%s[%d]" % (items_field, i)
            if not isinstance(item, dict):
                raise NumbersError("%s must be an object with 'name' and '%s'" % (where, per))
            allowed = {"name", per, "source"}
            for key in item:
                if key not in allowed:
                    raise NumbersError("%s: unknown field '%s' (allowed: name, %s, source)"
                                       % (where, key, per))
            name = _text(item.get("name"), where + ".name")
            amount = _number(item.get(per), "%s.%s" % (where, per), minimum=0.0)
            entry = {"name": name, per: amount}
            if "source" in item:
                entry["source"] = _text(item["source"], where + ".source")
            out.append(entry)
        return out
    if flat in data:
        amount = _number(data[flat], "'%s'" % flat, minimum=0.0)
        return [{"name": "all %s" % flat.replace("_", " "), per: amount}]
    raise NumbersError("missing field '%s' (or '%s' as an itemised list)" % (flat, items_field))


def _scenarios(raw):
    if not isinstance(raw, list):
        raise NumbersError("'scenarios' must be a list")
    out = []
    for i, item in enumerate(raw):
        where = "scenarios[%d]" % i
        if not isinstance(item, dict):
            raise NumbersError("%s must be an object with a 'name' and at least one override" % where)
        for key in item:
            if key not in SCENARIO_FIELDS and key != "name":
                raise NumbersError("%s: unknown field '%s' (allowed: name, %s)"
                                   % (where, key, ", ".join(SCENARIO_FIELDS)))
        name = _text(item.get("name"), where + ".name")
        scenario = {"name": name}
        if "price" in item:
            scenario["price"] = _number(item["price"], where + ".price", above=0.0)
        for key in ("volume_scale", "variable_scale", "fixed_scale"):
            if key in item:
                scenario[key] = _number(item[key], "%s.%s" % (where, key), minimum=0.0)
        if len(scenario) == 1:
            raise NumbersError("%s: give at least one of price, volume_scale, variable_scale, fixed_scale" % where)
        out.append(scenario)
    return out


def normalise(data):
    """Validate the input and expand costs into itemised lists."""
    for key in data:
        if key not in TOP_FIELDS:
            raise NumbersError("unknown field '%s' (allowed: %s)" % (key, ", ".join(TOP_FIELDS)))
    unit = _text(data.get("unit"), "'unit'")
    business = _text(data["business"], "'business'") if "business" in data else ""
    price = _number(data.get("price"), "'price'", above=0.0)
    variable_items = _cost_items(data, "variable", "variable_items", "per_unit")
    fixed_items = _cost_items(data, "fixed_monthly", "fixed_items", "per_month")
    startup_items = _cost_items(data, "startup", "startup_items", "amount")
    if "days_per_month" in data:
        days = _whole(data["days_per_month"], "'days_per_month'", 1, 31)
    else:
        days = 30
    plan = _number(data.get("plan_per_day"), "'plan_per_day'", minimum=0.0)
    ramp = data.get("ramp_per_day")
    if not isinstance(ramp, list) or len(ramp) != 12:
        raise NumbersError("'ramp_per_day' must be 12 numbers, one per month of year 1")
    ramp = [_number(v, "'ramp_per_day' month %d" % (i + 1), minimum=0.0) for i, v in enumerate(ramp)]
    capacity = None
    if "capacity_per_day" in data:
        capacity = _number(data["capacity_per_day"], "'capacity_per_day'", above=0.0)
        if plan > capacity:
            raise NumbersError(
                "'plan_per_day' (%g) is above 'capacity_per_day' (%g): impossible volume"
                % (plan, capacity))
        for i, value in enumerate(ramp):
            if value > capacity:
                raise NumbersError(
                    "'ramp_per_day' month %d (%g) is above 'capacity_per_day' (%g): impossible volume"
                    % (i + 1, value, capacity))
    scenarios = _scenarios(data["scenarios"]) if "scenarios" in data else []
    return {
        "business": business, "unit": unit, "price": price,
        "variable_items": variable_items, "fixed_items": fixed_items,
        "startup_items": startup_items, "days_per_month": days,
        "plan_per_day": plan, "ramp_per_day": ramp,
        "capacity_per_day": capacity, "scenarios": scenarios,
    }


def analyse(data, price=None, volume=1.0, variable_scale=1.0, fixed_scale=1.0):
    """Validate one numbers description and compute every number in the report.

    Pure function: same input, same output. Raises NumbersError on bad input.
    """
    spec = normalise(data)
    p = spec["price"] if price is None else _number(price, "the price override", above=0.0)
    volume = _number(volume, "the volume override", minimum=0.0)
    variable_scale = _number(variable_scale, "the variable cost scale", minimum=0.0)
    fixed_scale = _number(fixed_scale, "the fixed cost scale", minimum=0.0)

    variable = sum(it["per_unit"] for it in spec["variable_items"]) * variable_scale
    fixed = sum(it["per_month"] for it in spec["fixed_items"]) * fixed_scale
    startup = sum(it["amount"] for it in spec["startup_items"])
    days = spec["days_per_month"]
    plan = spec["plan_per_day"] * volume
    capacity = spec["capacity_per_day"]

    contribution = p - variable
    contribution_pct = (contribution / p * 100.0) if p else 0.0
    break_even = None if contribution <= 0 else fixed / (contribution * days)

    months = []
    cumulative = -startup
    for month, per_day in enumerate(spec["ramp_per_day"], start=1):
        per_day = per_day * volume
        units = per_day * days
        revenue = p * units
        variable_cost = variable * units
        operating = revenue - variable_cost - fixed
        cumulative += operating
        months.append({"month": month, "per_day": per_day, "units": units,
                       "revenue": revenue, "variable_cost": variable_cost,
                       "fixed": fixed, "operating": operating,
                       "cumulative": cumulative})

    year1_revenue = sum(m["revenue"] for m in months)
    year1_operating = sum(m["operating"] for m in months)
    deepest = min([-startup] + [m["cumulative"] for m in months])
    cash_needed = -deepest if deepest < 0 else 0.0
    deepest_month = None
    for m in months:
        if m["cumulative"] == deepest:
            deepest_month = m["month"]
    if deepest == -startup:
        deepest_month = None  # the startup spend before month 1 is the low point
    payback = next((m["month"] for m in months if m["cumulative"] >= 0), None)

    plan_units = plan * days
    monthly_revenue = p * plan_units
    monthly_operating = monthly_revenue - variable * plan_units - fixed
    margin_at_plan = (monthly_operating / monthly_revenue * 100.0) if monthly_revenue else 0.0

    flags = []
    u = spec["unit"]
    if contribution <= 0:
        flags.append("each %s loses money before fixed costs (price %s, variable cost %s)"
                     % (u, money(p), money(variable)))
    if capacity is not None and (break_even is None or break_even > capacity):
        flags.append("break-even %s needs more than the capacity of %g %ss a day"
                     % ("never happens" if break_even is None else "%d" % math.ceil(break_even),
                        capacity, u))
    if year1_operating <= 0:
        flags.append("year 1 loses money on operations (%s)" % money(year1_operating))
    if payback is None:
        flags.append("the startup spend is not earned back inside year 1")

    return {
        "business": spec["business"], "unit": u, "price": p,
        "variable_per_unit": variable, "contribution": contribution,
        "contribution_pct": contribution_pct,
        "fixed_monthly": fixed, "startup": startup,
        "days_per_month": days, "plan_per_day": plan,
        "monthly_revenue": monthly_revenue, "monthly_operating": monthly_operating,
        "margin_at_plan": margin_at_plan,
        "break_even_day": break_even, "capacity_per_day": capacity,
        "months": months,
        "year1_revenue": year1_revenue, "year1_operating": year1_operating,
        "year1_after_startup": year1_operating - startup,
        "cash_needed": cash_needed, "cash_deepest_month": deepest_month,
        "payback_month": payback, "flags": flags,
        "variable_items": spec["variable_items"], "fixed_items": spec["fixed_items"],
        "startup_items": spec["startup_items"], "scenarios": spec["scenarios"],
    }


def sensitivity(data):
    """The base plan, the three standard what-ifs and the scenarios from the file."""
    base = analyse(data)
    rows = [("Base plan", base)]
    rows.append(("Price 10% lower", analyse(data, price=base["price"] * 0.9)))
    rows.append(("Volume 20% lower", analyse(data, volume=0.8)))
    rows.append(("Variable cost 10% higher", analyse(data, variable_scale=1.1)))
    for scenario in base["scenarios"]:
        options = {("volume" if k == "volume_scale" else k): v
                   for k, v in scenario.items() if k != "name"}
        rows.append((scenario["name"], analyse(data, **options)))
    return rows


def _items_line(items, per):
    parts = []
    for it in items:
        part = "%s %s" % (it["name"], money(it[per]))
        if it.get("source"):
            part += " (%s)" % it["source"]
        parts.append(part)
    return "; ".join(parts)


def report(path, data, overrides="", price=None, volume=1.0):
    a = analyse(data, price=price, volume=volume)
    u = a["unit"]
    out = []
    out.append("# Unit economics")
    out.append("")
    out.append("Inputs read from %s: unit '%s', price %s, variable cost %s, fixed %s per month,"
               % (path, data["unit"], money(a["price"]), money(a["variable_per_unit"]),
                  money(a["fixed_monthly"])))
    out.append("startup %s, plan %g per day, %d selling days a month."
               % (money(a["startup"]), a["plan_per_day"], a["days_per_month"]))
    if a["business"]:
        out.append("Business: %s." % a["business"])
    if overrides:
        out.append("What-if overrides applied: %s." % overrides)
    out.append("")
    out.append("## Per unit")
    out.append("")
    out.append("| line | per %s | source |" % u)
    out.append("| --- | --- | --- |")
    for it in a["variable_items"]:
        out.append("| %s | %s | %s |" % (it["name"], money(it["per_unit"]), it.get("source", "")))
    out.append("| **what one %s leaves** | **%s** (%.0f%% of the price) | |"
               % (u, money(a["contribution"]), a["contribution_pct"]))
    out.append("")
    out.append("Fixed costs, %s a month: %s." % (money(a["fixed_monthly"]),
                                                 _items_line(a["fixed_items"], "per_month")))
    out.append("Startup spend, %s: %s." % (money(a["startup"]),
                                           _items_line(a["startup_items"], "amount")))
    out.append("")
    out.append("- Each %s leaves %s after its own costs." % (u, money(a["contribution"])))
    if a["break_even_day"] is None:
        out.append("- Break-even: never; each %s loses money before fixed costs." % u)
    else:
        out.append("- Break-even: %d %ss per day cover the fixed costs."
                   % (math.ceil(a["break_even_day"]), u))
        if a["capacity_per_day"] is not None:
            fits = "fits" if a["break_even_day"] <= a["capacity_per_day"] else "does NOT fit"
            out.append("- Against capacity (%g per day): break-even %s."
                       % (a["capacity_per_day"], fits))
    out.append("")
    out.append("## At the planned volume (%g per day, %d selling days a month)"
               % (a["plan_per_day"], a["days_per_month"]))
    out.append("")
    out.append("- Monthly revenue %s, monthly operating profit %s, margin %.1f%%."
               % (money(a["monthly_revenue"]), money(a["monthly_operating"]), a["margin_at_plan"]))
    out.append("")
    out.append("## Year 1, month by month")
    out.append("")
    out.append("| month | units/day | revenue | operating | cash position |")
    out.append("| --- | --- | --- | --- | --- |")
    for m in a["months"]:
        out.append("| %d | %g | %s | %s | %s |"
                   % (m["month"], m["per_day"], money(m["revenue"]),
                      money(m["operating"]), money(m["cumulative"])))
    out.append("")
    out.append("- Year 1 revenue: %s. Year 1 operating profit: %s."
               % (money(a["year1_revenue"]), money(a["year1_operating"])))
    out.append("- After the %s startup spend: %s."
               % (money(a["startup"]), money(a["year1_after_startup"])))
    deepest = "the startup spend before month 1" if a["cash_deepest_month"] is None \
        else "month %d" % a["cash_deepest_month"]
    out.append("- Cash needed before it pays for itself: %s (deepest point: %s)."
               % (money(a["cash_needed"]), deepest))
    if a["payback_month"] is not None:
        out.append("- Startup spend is earned back in month %d." % a["payback_month"])
    else:
        out.append("- Startup spend is not earned back inside year 1.")
    out.append("")
    out.append("## What if")
    out.append("")
    out.append("| scenario | what one %s leaves | break-even a day | year 1 operating |" % u)
    out.append("| --- | --- | --- | --- |")
    for name, s in sensitivity(data):
        be = "never" if s["break_even_day"] is None else "%d" % math.ceil(s["break_even_day"])
        out.append("| %s | %s | %s | %s |"
                   % (name, money(s["contribution"]), be, money(s["year1_operating"])))
    out.append("")
    if a["flags"]:
        out.append("## Red flags")
        out.append("")
        for flag in a["flags"]:
            out.append("- %s%s." % (flag[0].upper(), flag[1:]))
        out.append("")
    out.append("Every number above is computed from the inputs listed at the top. Estimates")
    out.append("stay estimates until real quotes arrive; check costs, payroll and tax with")
    out.append("an accountant.")
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Unit economics for the pmf pack.")
    parser.add_argument("numbers", help="path to numbers.json")
    parser.add_argument("--out", help="write the report to this file as well")
    parser.add_argument("--json", action="store_true", help="print the computed numbers as JSON")
    parser.add_argument("--price", type=float, help="what-if price, without editing the file")
    parser.add_argument("--volume", type=float, default=1.0, help="what-if volume multiplier, 0.8 = 20%% fewer")
    args = parser.parse_args()
    try:
        data = load(args.numbers)
        overrides = []
        if args.price is not None:
            overrides.append("price %s" % money(args.price))
        if args.volume != 1.0:
            overrides.append("volume x%g" % args.volume)
        analysis = analyse(data, price=args.price, volume=args.volume)
    except NumbersError as exc:
        sys.exit("unit_economics.py: %s" % exc)
    if args.json:
        print(json.dumps(analysis, indent=2))
        return
    text = report(args.numbers, data, overrides=", ".join(overrides),
                  price=args.price, volume=args.volume)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
