#!/usr/bin/env python3
"""The real-world test log for the pmf pack.

Reads pmf/experiments.json: every demand or retention test the business ran
(or plans to run), with the criteria set BEFORE it ran. Validates strictly,
then computes each result: which criteria were met, the conversion, the
revenue collected, the cost per paying customer, the repeat rate.

The criteria are locked: `check` fingerprints every test that has no results
yet into pmf/experiments.lock.json. A test with results but no lock, or whose
criteria, price, kind or creation date changed after the lock, is an error.

Paid counts are net of refunds. Rate criteria are judged on the lower end of
a 95% Wilson interval, so a tiny sample cannot pass on luck. A demand test
needs min_paid of at least MIN_PAID_FLOOR.

The outcome is computed, never written: pass when every criterion is met,
fail when none is, mixed when some are. A failed test is a result, not an
error.

Usage:
  experiments.py check [--dir pmf]
  experiments.py report [--dir pmf] [--out pmf/test.md]
"""

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import date

KINDS = ("demand", "retention")
CRITERIA = {
    "demand": ("min_paid", "min_conversion", "max_cost_per_paid"),
    "retention": ("min_repeat_rate",),
}
ENTRY_FIELDS = ("id", "kind", "created", "hypothesis", "method", "audience",
                "price", "criteria", "results", "notes")
RESULT_FIELDS = {
    "demand": ("date", "exposure", "paid_conversions", "refunds", "cost", "notes"),
    "retention": ("date", "cohort", "repeat_buyers", "notes"),
}
LOCK = "experiments.lock.json"
MIN_PAID_FLOOR = 5
Z95 = 1.96


class ExperimentsError(Exception):
    pass


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        raise ExperimentsError("no test log at %s; the pmf-test skill writes it" % path)
    except ValueError as exc:
        raise ExperimentsError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(data, dict) or list(data.keys()) != ["experiments"]:
        raise ExperimentsError("%s must hold exactly one key, 'experiments', listing the tests" % path)
    if not isinstance(data["experiments"], list):
        raise ExperimentsError("'experiments' must be a list")
    return data["experiments"]


def _text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ExperimentsError("%s must be a non-empty line of text" % where)
    return value.strip()


def _number(value, where, minimum=None, above=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ExperimentsError("%s must be a number" % where)
    value = float(value)
    if above is not None and value <= above:
        raise ExperimentsError("%s must be above %g" % (where, above))
    if minimum is not None and value < minimum:
        raise ExperimentsError("%s must be %g or more" % (where, minimum))
    if maximum is not None and value > maximum:
        raise ExperimentsError("%s must be %g or less" % (where, maximum))
    return value


def _count(value, where, minimum):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) != int(value):
        raise ExperimentsError("%s must be a whole number" % where)
    value = int(value)
    if value < minimum:
        raise ExperimentsError("%s must be %d or more" % (where, minimum))
    return value


def _date(value, where):
    if not isinstance(value, str):
        raise ExperimentsError("%s must be a date like 2026-10-14" % where)
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ExperimentsError("%s must be a date like 2026-10-14 (got %r)" % (where, value))


def _criteria(raw, where, kind):
    if not isinstance(raw, dict) or not raw:
        raise ExperimentsError("%s.criteria must be an object with at least one criterion" % where)
    allowed = CRITERIA[kind]
    for key in raw:
        if key not in allowed:
            raise ExperimentsError("%s.criteria: unknown criterion '%s' (a %s test allows: %s)"
                                   % (where, key, kind, ", ".join(allowed)))
    if kind == "demand" and "min_paid" not in raw:
        raise ExperimentsError("%s.criteria: a demand test needs min_paid (at least %d)"
                               % (where, MIN_PAID_FLOOR))
    out = {}
    for key, value in raw.items():
        w = "%s.criteria.%s" % (where, key)
        if key == "min_paid":
            out[key] = _count(value, w, MIN_PAID_FLOOR)
        elif key in ("min_conversion", "min_repeat_rate"):
            out[key] = _number(value, w, above=0.0, maximum=1.0)
        else:  # max_cost_per_paid
            out[key] = _number(value, w, minimum=0.0)
    return out


def _results(raw, where, kind, created):
    if not isinstance(raw, dict):
        raise ExperimentsError("%s.results must be an object with 'date' and the actuals" % where)
    allowed = RESULT_FIELDS[kind]
    for key in raw:
        if key not in allowed:
            raise ExperimentsError("%s.results: unknown field '%s' (allowed: %s)"
                                   % (where, key, ", ".join(allowed)))
    results = {"date": _date(raw.get("date"), where + ".results.date")}
    if results["date"] < created:
        raise ExperimentsError("%s.results.date is before the test was created (%s)"
                               % (where, created.isoformat()))
    if kind == "demand":
        exposure = _count(raw.get("exposure"), where + ".results.exposure", 1)
        paid = _count(raw.get("paid_conversions"), where + ".results.paid_conversions", 0)
        if paid > exposure:
            raise ExperimentsError("%s.results: paid_conversions (%d) is above exposure (%d)"
                                   % (where, paid, exposure))
        refunds = _count(raw.get("refunds"), where + ".results.refunds", 0)
        if refunds > paid:
            raise ExperimentsError("%s.results: refunds (%d) is above paid_conversions (%d)"
                                   % (where, refunds, paid))
        results.update({"exposure": exposure, "paid_conversions": paid, "refunds": refunds,
                        "cost": _number(raw.get("cost"), where + ".results.cost", minimum=0.0)})
    else:
        cohort = _count(raw.get("cohort"), where + ".results.cohort", 1)
        repeat = _count(raw.get("repeat_buyers"), where + ".results.repeat_buyers", 0)
        if repeat > cohort:
            raise ExperimentsError("%s.results: repeat_buyers (%d) is above cohort (%d)"
                                   % (where, repeat, cohort))
        results.update({"cohort": cohort, "repeat_buyers": repeat})
    if "notes" in raw:
        results["notes"] = _text(raw["notes"], where + ".results.notes")
    return results


def validate_entry(item, index, seen):
    where = "experiments[%d]" % index
    if not isinstance(item, dict):
        raise ExperimentsError("%s must be one object" % where)
    for key in item:
        if key not in ENTRY_FIELDS:
            raise ExperimentsError("%s: unknown field '%s' (allowed: %s)"
                                   % (where, key, ", ".join(ENTRY_FIELDS)))
    eid = _text(item.get("id"), where + ".id")
    if eid in seen:
        raise ExperimentsError("%s: duplicate id '%s'" % (where, eid))
    kind = item.get("kind")
    if kind not in KINDS:
        raise ExperimentsError("%s.kind must be one of: %s" % (where, ", ".join(KINDS)))
    entry = {
        "id": eid,
        "kind": kind,
        "created": _date(item.get("created"), where + ".created"),
        "hypothesis": _text(item.get("hypothesis"), where + ".hypothesis"),
        "method": _text(item.get("method"), where + ".method"),
        "audience": _text(item.get("audience"), where + ".audience"),
        "criteria": _criteria(item.get("criteria"), where, kind),
    }
    if kind == "demand":
        entry["price"] = _number(item.get("price"), where + ".price", above=0.0)
    elif "price" in item:
        raise ExperimentsError("%s: 'price' belongs to demand tests only" % where)
    if "results" in item:
        entry["results"] = _results(item["results"], where, kind, entry["created"])
    if "notes" in item:
        entry["notes"] = _text(item["notes"], where + ".notes")
    return entry


def validate_all(raw):
    """Return (entries, problems): every entry is validated so all typos surface at once."""
    entries, problems = [], []
    seen = set()
    for i, item in enumerate(raw):
        try:
            entry = validate_entry(item, i, seen)
            entries.append(entry)
            seen.add(entry["id"])
        except ExperimentsError as exc:
            problems.append(str(exc))
    return entries, problems


def net_paid(results):
    return results["paid_conversions"] - results["refunds"]


def wilson_low(hits, n):
    """Lower end of the 95% Wilson interval for hits out of n."""
    p = hits / float(n)
    z2 = Z95 * Z95
    centre = p + z2 / (2 * n)
    spread = Z95 * math.sqrt(p * (1 - p) / n + z2 / (4.0 * n * n))
    return max(0.0, (centre - spread) / (1 + z2 / n))


def _judge_rate(hits, n, target, what):
    rate, low = hits / float(n), wilson_low(hits, n)
    return low >= target, rate, ("%s %s (95%% lower bound %s, from %d of %d) against a bar of %s"
                                 % (_rate(rate), what, _rate(low), hits, n, _rate(target)))


def fingerprint(entry):
    """The numbers a test is judged by, frozen before it runs."""
    frozen = {"kind": entry["kind"], "created": entry["created"].isoformat(),
              "price": entry.get("price"), "criteria": entry["criteria"]}
    return hashlib.sha256(json.dumps(frozen, sort_keys=True).encode("utf-8")).hexdigest()


def read_lock(dirpath):
    path = os.path.join(dirpath, LOCK)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except ValueError as exc:
        raise ExperimentsError("%s is not valid JSON: %s" % (path, exc))
    if not isinstance(data, dict) or not all(
            isinstance(v, dict) and isinstance(v.get("sha256"), str) for v in data.values()):
        raise ExperimentsError("%s is not a lock file; it maps each test id to its fingerprint" % path)
    return data


def lock_problems(entries, lock):
    """A result needs a lock taken before it, and a lock never moves."""
    problems = []
    for entry in entries:
        rec = lock.get(entry["id"])
        if rec is None:
            if "results" in entry:
                problems.append("%s has results but its criteria were never locked; run check "
                                "before a test runs, and log this one again as a new id" % entry["id"])
        elif rec["sha256"] != fingerprint(entry):
            problems.append("%s: the criteria, price, kind or creation date changed after they were "
                            "locked on %s; restore them or log a new test with a new id"
                            % (entry["id"], rec.get("locked_on", "?")))
    return problems


def validate_dir(dirpath):
    """Load, validate and lock-check pmf/experiments.json. Return (entries, problems, lock)."""
    raw = load(os.path.join(dirpath, "experiments.json"))
    entries, problems = validate_all(raw)
    lock = read_lock(dirpath)
    if not problems:
        problems = lock_problems(entries, lock)
    return entries, problems, lock


def _judge(name, target, entry, results):
    """Return (met, actual, detail) for one criterion. The actual is None when not computable."""
    if name == "min_paid":
        paid = net_paid(results)
        return paid >= target, paid, "%d paid after refunds against a bar of %d" % (paid, target)
    if name == "min_conversion":
        return _judge_rate(net_paid(results), results["exposure"], target, "conversion")
    if name == "max_cost_per_paid":
        paid = net_paid(results)
        if not paid:
            return False, None, "no paid conversions after refunds to divide the cost by"
        per = results["cost"] / paid
        return per <= target, per, "cost %.2f per paid against a ceiling of %.2f" % (per, target)
    if name == "min_repeat_rate":
        return _judge_rate(results["repeat_buyers"], results["cohort"], target, "repeat")
    raise ExperimentsError("unknown criterion: %s" % name)


def _rate(v):
    return "%.1f%%" % (v * 100.0)


def _criterion_text(name, value):
    if name == "min_paid":
        return "%d" % value
    if name in ("min_conversion", "min_repeat_rate"):
        return _rate(value)
    return "%.2f" % value


def evaluate(entry):
    """Compute one entry's outcome and metrics. The outcome is never stored."""
    results = entry.get("results")
    if results is None:
        return {"status": "planned", "criteria": [], "metrics": {}}
    rows = []
    for name in sorted(entry["criteria"]):
        met, actual, detail = _judge(name, entry["criteria"][name], entry, results)
        rows.append({"criterion": name, "target": entry["criteria"][name],
                     "actual": actual, "met": met, "detail": detail})
    met_count = sum(1 for r in rows if r["met"])
    if met_count == len(rows):
        status = "pass"
    elif met_count == 0:
        status = "fail"
    else:
        status = "mixed"
    metrics = {}
    if entry["kind"] == "demand":
        paid, exposure = net_paid(results), results["exposure"]
        metrics["conversion_rate"] = paid / exposure
        metrics["cost_per_paid"] = (results["cost"] / paid) if paid else None
        metrics["revenue_collected"] = paid * entry["price"]
        metrics["net"] = metrics["revenue_collected"] - results["cost"]
    else:
        metrics["repeat_rate"] = results["repeat_buyers"] / results["cohort"]
    return {"status": status, "criteria": rows, "metrics": metrics}


def evaluate_all(entries):
    return [(entry, evaluate(entry)) for entry in entries]


def _summary_line(entry, result):
    when = entry["results"]["date"].isoformat() if "results" in entry else ""
    if result["status"] == "planned":
        return "%s %s, created %s: planned, no results yet" % (
            entry["id"], entry["kind"], entry["created"].isoformat())
    met = sum(1 for r in result["criteria"] if r["met"])
    return "%s %s, created %s, results %s: %s (%d of %d criteria met)" % (
        entry["id"], entry["kind"], entry["created"].isoformat(), when,
        result["status"].upper(), met, len(result["criteria"]))


def report_text(entries):
    evaluated = evaluate_all(entries)
    done = [(e, r) for e, r in evaluated if r["status"] != "planned"]
    planned = [(e, r) for e, r in evaluated if r["status"] == "planned"]
    out = ["# Real-world tests", ""]
    out.append("%d test%s logged: %d with results, %d planned. Outcomes are computed from"
               " the actuals against the criteria set before each test ran."
               % (len(entries), "" if len(entries) == 1 else "s", len(done), len(planned)))
    out.append("")
    for entry, result in evaluated:
        head = "%s: %s test" % (entry["id"], entry["kind"])
        out.append("## %s" % head)
        out.append("")
        out.append("- Created: %s" % entry["created"].isoformat())
        out.append("- Hypothesis: %s" % entry["hypothesis"])
        out.append("- Method: %s" % entry["method"])
        out.append("- Audience: %s" % entry["audience"])
        if entry["kind"] == "demand":
            out.append("- Price tested: %.2f" % entry["price"])
        if entry.get("notes"):
            out.append("- Notes: %s" % entry["notes"])
        out.append("")
        if result["status"] == "planned":
            out.append("- Criteria: %s" % ", ".join(
                "%s %s" % (k, _criterion_text(k, v)) for k, v in sorted(entry["criteria"].items())))
            out.append("")
            out.append("- Outcome: not run yet.")
            out.append("")
            continue
        out.append("- Results date: %s" % entry["results"]["date"].isoformat())
        out.append("")
        out.append("| criterion | target | actual | met |")
        out.append("| --- | --- | --- | --- |")
        for row in result["criteria"]:
            out.append("| %s | %s | %s | %s |"
                       % (row["criterion"], _criterion_text(row["criterion"], row["target"]),
                          "n/a" if row["actual"] is None else _criterion_text(row["criterion"], row["actual"]),
                          "yes" if row["met"] else "no"))
        out.append("")
        if entry["kind"] == "demand":
            out.append("- Exposure: %d reached, %d paid, %d refunded, %s conversion."
                       % (entry["results"]["exposure"], entry["results"]["paid_conversions"],
                          entry["results"]["refunds"], _rate(result["metrics"]["conversion_rate"])))
            cpp = result["metrics"]["cost_per_paid"]
            out.append("- Test cost: %.2f; revenue collected: %.2f; net: %.2f%s."
                       % (entry["results"]["cost"], result["metrics"]["revenue_collected"],
                          result["metrics"]["net"],
                          ("; cost per paying customer %.2f" % cpp) if cpp is not None else ""))
        else:
            out.append("- Cohort: %d buyers; %d bought again (%s)."
                       % (entry["results"]["cohort"], entry["results"]["repeat_buyers"],
                          _rate(result["metrics"]["repeat_rate"])))
        met = sum(1 for r in result["criteria"] if r["met"])
        out.append("- **Outcome: %s** (%d of %d criteria met)."
                   % (result["status"].upper(), met, len(result["criteria"])))
        if "notes" in entry["results"]:
            out.append("- Notes: %s" % entry["results"]["notes"])
        out.append("")
    out.append("Read a pass as permission to build the next slice, not as proof of product-")
    out.append("market fit. Read a fail or a mixed result as the next thing to change, one")
    out.append("change at a time. Never edit a recorded result; log a new test instead.")
    return "\n".join(out) + "\n"


def _report_problems(problems):
    print("the test log has %d problem%s:" % (len(problems), "" if len(problems) == 1 else "s"))
    for problem in problems:
        print("  " + problem)


def main():
    parser = argparse.ArgumentParser(description="The real-world test log for the pmf pack.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("check", "validate the log and show each computed outcome"),
                            ("report", "write pmf/test.md from the log")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--dir", default="pmf")
        if name == "report":
            p.add_argument("--out", help="default: <dir>/test.md")
    args = parser.parse_args()

    try:
        entries, problems, lock = validate_dir(args.dir)
    except ExperimentsError as exc:
        sys.exit("experiments.py: %s" % exc)
    if problems:
        _report_problems(problems)
        sys.exit(1)
    if args.command == "check":
        fresh = [e for e in entries if e["id"] not in lock and "results" not in e]
        for entry in fresh:
            lock[entry["id"]] = {"sha256": fingerprint(entry), "locked_on": date.today().isoformat()}
            print("locked %s: its criteria cannot change from here" % entry["id"])
        if fresh:
            with open(os.path.join(args.dir, LOCK), "w", encoding="utf-8") as fh:
                json.dump(lock, fh, indent=2, sort_keys=True)
                fh.write("\n")
        evaluated = evaluate_all(entries)
        for entry, result in evaluated:
            print(_summary_line(entry, result))
        done = sum(1 for _, r in evaluated if r["status"] != "planned")
        print("%d test%s: %d with results, %d planned."
              % (len(entries), "" if len(entries) == 1 else "s", done, len(entries) - done))
        return
    text = report_text(entries)
    out_path = args.out or os.path.join(args.dir, "test.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("wrote %s" % out_path)


if __name__ == "__main__":
    main()
