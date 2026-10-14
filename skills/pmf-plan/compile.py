#!/usr/bin/env python3
"""Compiles the pmf state folder into one decision document.

Reads the projected economics (numbers.json), the demand evidence
(experiments.json when it exists, else the simulated panel) and everything
else the stages wrote. The verdict is computed, never written:

  Validated   the economics work, the latest demand test met its locked
              criteria at the plan's price, and no later retention test failed
  Projected   the economics work; no real-world test has a result yet
  Not yet     a check fails (the failing numbers are listed)
  Incomplete  numbers.json is missing or invalid

The report leads with what is known, what remains uncertain and the cheapest
next action that could change the decision. Exit code 0 for Validated and
Projected, 1 otherwise.

Usage:
  compile.py --dir pmf [--check] [--min-coverage 0.8]
"""

import argparse
import importlib.util
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

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
    ("experiments.json", "pmf-test"),
    ("test.md", "pmf-test"),
    ("build.md", "pmf-build"),
    ("marketing.md", "pmf-marketing"),
    ("brand.md", "pmf-brand"),
    ("ops.md", "pmf-ops"),
    ("launch.md", "pmf-launch"),
]

PRICE_TOLERANCE = 0.10  # a test may charge up to 10% under the plan price and still count
CONDITION_RE = re.compile(r"^\s*[-*]\s*\[([ xX])\]\s*(.+?)\s*$")
FRESHNESS = {"fresh": "fresh", "stale": "STALE", "changed": "changed",
             "missing": "MISSING"}


def die(msg):
    sys.exit("compile.py: " + msg)


def _load_tool(skill, filename, modname, required):
    path = os.path.normpath(os.path.join(HERE, os.pardir, skill, filename))
    if not os.path.isfile(path):
        if required:
            die("cannot find %s/%s; keep the pmf skill folders together (reinstall the pack)"
                % (skill, filename))
        return None
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def pressure_conditions(dirpath):
    path = os.path.join(dirpath, "pressure.md")
    if not os.path.isfile(path):
        return []
    found = []
    for line in read_text(path).splitlines():
        match = CONDITION_RE.match(line)
        if match:
            found.append((match.group(2), match.group(1).lower() == "x"))
    return found


def source_stats(analysis):
    items = analysis["variable_items"] + analysis["fixed_items"] + analysis["startup_items"]
    sourced = sum(1 for item in items if item.get("source"))
    return sourced, len(items)


def demand_summary(latest, planned, panel):
    """A one-line description of the strongest demand evidence on file."""
    if latest:
        entry, result = latest
        met = sum(1 for row in result["criteria"] if row["met"])
        return ("real test %s: %s (%d of %d criteria met, results %s)"
                % (entry["id"], result["status"].upper(), met, len(result["criteria"]),
                   entry["results"]["date"].isoformat()))
    if planned:
        return "a real test is designed (%s) with no results yet" % planned[0]["id"]
    if panel:
        rate = panel.get("buy_rate")
        rate_text = "not computed" if rate is None else "%.0f%%" % (rate * 100)
        return ("simulated only: the buyer panel's buy rate is %s (answered %s of %s)"
                % (rate_text, panel.get("answered", "?"), panel.get("n", "?")))
    return "none: no real test and no panel on file"


def readiness(verdict):
    return {
        "Validated": "ready: the economics work and a real test met its criteria; build and launch",
        "Projected": "untested: do not scale on projections; run the next real test",
        "Not yet": "blocked: fix the failing checks before spending further",
        "Incomplete": "not computable yet: the missing inputs are listed below",
    }[verdict]


def main():
    parser = argparse.ArgumentParser(description="Compile the pmf plan and its verdict.")
    parser.add_argument("--dir", default="pmf")
    parser.add_argument("--check", action="store_true", help="print the verdict and checks, write nothing")
    parser.add_argument("--min-coverage", type=float, default=0.8,
                        help="panel coverage below this is called noise (default 0.8)")
    args = parser.parse_args()

    dirpath = args.dir
    numbers_path = os.path.join(dirpath, "numbers.json")
    panel_path = os.path.join(dirpath, "panel", "results.json")
    experiments_path = os.path.join(dirpath, "experiments.json")

    econ = _load_tool("pmf-numbers", "unit_economics.py", "pmf_unit_economics", required=True)
    exp = _load_tool("pmf-test", "experiments.py", "pmf_experiments",
                     required=os.path.isfile(experiments_path))
    status_mod = _load_tool("pmf", "status.py", "pmf_status", required=False)

    problems = []
    analysis = None
    if not os.path.isfile(numbers_path):
        problems.append("numbers.json is missing (run pmf-numbers)")
    else:
        try:
            analysis = econ.analyse(econ.load(numbers_path))
        except econ.NumbersError as exc:
            problems.append("numbers.json is invalid: %s" % exc)

    entries, latest, planned, exp_problem = [], None, [], None
    if os.path.isfile(experiments_path) and exp:
        try:
            entries, exp_problems, _ = exp.validate_dir(dirpath)
            if exp_problems:
                exp_problem = "; ".join(exp_problems)
        except exp.ExperimentsError as exc:
            exp_problem = str(exc)
        if exp_problem:
            problems.append("experiments.json is invalid: %s" % exp_problem)
            entries = []
        else:
            done = [(e, exp.evaluate(e)) for e in entries if "results" in e]
            done.sort(key=lambda pair: pair[0]["results"]["date"])
            # the latest result of each kind decides; a failure of either kind blocks
            last = {pair[0]["kind"]: pair for pair in done}
            decisive = [last[k] for k in exp.KINDS if k in last]
            failing = [pair for pair in decisive if pair[1]["status"] != "pass"]
            latest = failing[0] if failing else last.get("demand")
            planned = [e for e in entries if "results" not in e]

    panel = None
    panel_problem = None
    if os.path.isfile(panel_path):
        try:
            panel = read_json(panel_path)
        except ValueError as exc:
            panel_problem = str(exc)

    checks = []
    if analysis:
        unit = analysis["unit"]
        checks.append(("Each unit earns money", analysis["contribution"] > 0,
                       "contribution %.2f per %s" % (analysis["contribution"], unit)))
        checks.append(("Year 1 makes an operating profit", analysis["year1_operating"] > 0,
                       "year 1 operating %.2f" % analysis["year1_operating"]))
        if analysis["capacity_per_day"] is None:
            checks.append(("Break-even fits capacity", True,
                           "not checked: no capacity_per_day given"))
        else:
            fits = (analysis["break_even_day"] is not None
                    and analysis["break_even_day"] <= analysis["capacity_per_day"])
            checks.append(("Break-even fits capacity", fits,
                           "break-even %s per day against capacity %g"
                           % ("never" if analysis["break_even_day"] is None
                              else "%d" % math.ceil(analysis["break_even_day"]),
                              analysis["capacity_per_day"])))
    if latest:
        entry, result = latest
        for row in result["criteria"]:
            checks.append(("Real test %s: %s" % (entry["id"], row["criterion"]), row["met"],
                           row["detail"]))
        if analysis and entry["kind"] == "demand":
            floor = analysis["price"] * (1 - PRICE_TOLERANCE)
            checks.append(("Real test %s: price" % entry["id"], entry["price"] >= floor,
                           "tested at %.2f against a plan price of %.2f (at least %.2f counts)"
                           % (entry["price"], analysis["price"], floor)))

    if problems:
        verdict = "Incomplete"
    elif not all(ok for _, ok, _ in checks[:3]):
        verdict = "Not yet"
    elif latest is None:
        verdict = "Projected"
    elif latest[0]["kind"] == "demand" and all(ok for _, ok, _ in checks[3:]):
        verdict = "Validated"
    else:
        verdict = "Not yet"

    name = "the business"
    idea_path = os.path.join(dirpath, "idea.md")
    if os.path.isfile(idea_path):
        for line in read_text(idea_path).splitlines():
            if line.startswith("# "):
                name = line[2:].strip()
                break

    if args.check:
        print("Verdict: %s" % verdict)
        for problem in problems:
            print("  blocked: %s" % problem)
        for check_name, ok, detail in checks:
            print("  [%s] %s: %s" % ("pass" if ok else "FAIL", check_name, detail))
        print("  demand: %s" % demand_summary(latest, planned, panel))
        if verdict not in ("Validated", "Projected"):
            sys.exit(1)
        return

    lines = ["# Business plan: %s" % name, "", "**Verdict: %s**" % verdict, ""]

    if analysis:
        econ_line = ("**profitable** on the projections (each %s leaves %.2f; break-even %s per day; year 1 operating %.2f)"
                     % (analysis["unit"], analysis["contribution"],
                        "never" if analysis["break_even_day"] is None
                        else "%d" % math.ceil(analysis["break_even_day"]),
                        analysis["year1_operating"])) \
            if all(ok for _, ok, _ in checks[:3]) else "**not working on these numbers**"
        lines.append("- Projected economics: %s." % econ_line)
        lines.append("- Demand evidence: %s." % demand_summary(latest, planned, panel))
    else:
        lines.append("- Projected economics: not computed: %s." % "; ".join(problems))
    lines.append("- Readiness: %s." % readiness(verdict))
    lines.append("")

    conditions = pressure_conditions(dirpath)
    freshness = None
    if status_mod is not None:
        try:
            report = status_mod.check(dirpath)
            freshness = {row["artifact"]: row for row in report["artifacts"]}
        except status_mod.StatusError:
            freshness = None

    uncertain = []
    if problems:
        uncertain.append("The verdict cannot compute: %s." % "; ".join(problems))
    if latest is None and not planned:
        uncertain.append("No real-world test has run; the panel is simulated and a simulated "
                         "buy rate is not a forecast. The next test is the cheapest way to change this.")
    if latest is None and planned:
        uncertain.append("The real test %s is designed but not run." % planned[0]["id"])
    missed = ", ".join(name.split(": ", 1)[1] for name, ok, _ in checks[3:] if not ok)
    if latest is not None and missed:
        uncertain.append("The latest real test (%s) did not meet: %s." % (latest[0]["id"], missed))
    sourced_obj = (panel or {}).get("grounded_objections")
    if sourced_obj and sourced_obj[0] < sourced_obj[1]:
        uncertain.append("Panel objections without a real buyer quote behind them: %d of %d. "
                         "Personas built on guesses barely beat strangers; link quotes from "
                         "research/voice.md in customer.json." % (sourced_obj[1] - sourced_obj[0],
                                                                  sourced_obj[1]))
    if analysis:
        sourced, total = source_stats(analysis)
        if sourced < total:
            uncertain.append("Cost lines without a source: %d of %d; those are assumptions until "
                             "a quote or invoice replaces them." % (total - sourced, total))
    if conditions:
        open_count = sum(1 for _, done_flag in conditions if not done_flag)
        if open_count:
            uncertain.append("Conditions from the pressure test still open: %d of %d."
                             % (open_count, len(conditions)))
    if freshness:
        bad = sorted(rel for rel, row in freshness.items()
                     if row["status"] in ("stale", "changed", "missing"))
        if bad:
            uncertain.append("Recorded files whose inputs or content changed since they were "
                             "recorded: %s. Rerun those stages and compile again." % ", ".join(bad))
    if not uncertain:
        uncertain.append("Nothing recorded contradicts this plan. The numbers are still "
                         "estimates until real quotes and real buyers replace them.")
    lines.append("## What remains uncertain")
    lines.append("")
    for item in uncertain:
        lines.append("- %s" % item)
    lines.append("")

    lines += ["## The next cheapest action", ""]
    if verdict == "Incomplete":
        action = ("Complete the missing inputs (%s), then compile again."
                  % "; ".join(problems))
    elif verdict == "Not yet" and not all(ok for _, ok, _ in checks[:3]):
        action = ("Repair the failing economics first: rerun pmf-numbers with honest costs, "
                  "and pmf-offer if the price or the offer is the problem. A demand test on "
                  "numbers that cannot work proves nothing.")
    elif verdict == "Not yet" and latest is not None:
        action = ("Change one thing against the missed criteria (%s), then run a new test in "
                  "pmf-test and log it as a new id. One change at a time." % missed)
    elif verdict == "Projected" and planned:
        action = ("Run %s and record its results in pmf/experiments.json, then rerun pmf-test "
                  "and compile again." % planned[0]["id"])
    elif verdict == "Projected":
        action = ("Design and run the cheapest real test in pmf-test (a pre-sale, a pop-up, "
                  "paid pilots or a deposit waitlist); record the results and compile again.")
    else:
        action = ("Proceed: run pmf-build for the smallest next slice, then pmf-launch when "
                  "the product is ready, watching the 30-day numbers against the same criteria.")
    lines.append(action)
    lines.append("")

    lines += ["## The checks", "", "| check | result | the numbers |", "| --- | --- | --- |"]
    if checks:
        for check_name, ok, detail in checks:
            lines.append("| %s | %s | %s |" % (check_name, "pass" if ok else "FAIL", detail))
    else:
        lines.append("| (none) | | the verdict cannot compute yet |")
    lines.append("")

    lines += ["## Demand evidence", ""]
    if entries:
        lines += ["| test | kind | created | results | criteria met | outcome |",
                  "| --- | --- | --- | --- | --- | --- |"]
        for entry in entries:
            result = exp.evaluate(entry)
            if result["status"] == "planned":
                lines.append("| %s | %s | %s | not run yet | | |"
                             % (entry["id"], entry["kind"], entry["created"].isoformat()))
            else:
                met = sum(1 for row in result["criteria"] if row["met"])
                lines.append("| %s | %s | %s | %s | %d of %d | %s |"
                             % (entry["id"], entry["kind"], entry["created"].isoformat(),
                                entry["results"]["date"].isoformat(), met,
                                len(result["criteria"]), result["status"].upper()))
        lines.append("")
    else:
        lines.append("No real-world tests logged yet (pmf-test writes them).")
        lines.append("")
    if panel:
        rate = panel.get("buy_rate")
        coverage = panel.get("coverage")
        text = ("Simulated panel: buy rate %s from %s of %s answered"
                % ("not computed" if rate is None else "%.0f%%" % (rate * 100),
                   panel.get("answered", "?"), panel.get("n", "?")))
        if coverage is not None:
            text += " (coverage %.0f%%)" % (coverage * 100)
        text += ". A simulated rate finds objections and wording; it is not a conversion forecast."
        if coverage is not None and coverage < args.min_coverage:
            text += " Coverage is below the %.0f%% bar: treat it as noise." % (args.min_coverage * 100)
        lines.append(text)
        lines.append("")
    elif panel_problem:
        lines.append("The panel results could not be read: %s" % panel_problem)
        lines.append("")

    if analysis:
        lines += [
            "## Key numbers", "",
            "- Price per %s: %.2f" % (analysis["unit"], analysis["price"]),
            "- Contribution per %s: %.2f" % (analysis["unit"], analysis["contribution"]),
            "- Break-even: %s per day" % ("never" if analysis["break_even_day"] is None
                                          else "%d" % math.ceil(analysis["break_even_day"])),
            "- Margin at plan: %.1f%%" % analysis["margin_at_plan"],
            "- Year 1 operating profit: %.2f" % analysis["year1_operating"],
            "- Cash needed before it pays for itself: %.2f" % analysis["cash_needed"],
            "- Payback: %s" % ("month %d" % analysis["payback_month"]
                               if analysis["payback_month"] else "not in year 1"),
            "",
        ]

    if conditions:
        lines += ["## Conditions from the pressure test", "",
                  "| condition | status |", "| --- | --- |"]
        for text, done_flag in conditions:
            lines.append("| %s | %s |" % (text, "done" if done_flag else "**open**"))
        lines.append("")

    lines += ["## Artifact index", ""]
    header = "| file | status | owning skill |"
    divider = "| --- | --- | --- |"
    if freshness is not None:
        header = "| file | status | freshness | owning skill |"
        divider = "| --- | --- | --- | --- |"
    lines += [header, divider]
    for rel, skill in ARTIFACTS:
        exists = os.path.isfile(os.path.join(dirpath, rel))
        if freshness is not None:
            row = freshness.get(rel)
            mark = "-" if row is None else FRESHNESS[row["status"]]
            lines.append("| `%s` | %s | %s | `%s` |"
                         % (rel, "present" if exists else "missing", mark, skill))
        else:
            lines.append("| `%s` | %s | `%s` |" % (rel, "present" if exists else "missing", skill))
    lines += [
        "",
        "---",
        "",
        "Generated by compile.py from the files above. Edit the inputs and rerun; never",
        "edit this file by hand. The panel is simulated, the economics are projections",
        "from your inputs, and a pass is permission to proceed one step, not proof of",
        "product-market fit. Not financial, legal or tax advice.",
        "",
    ]

    plan_path = os.path.join(dirpath, "plan.md")
    with open(plan_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote %s (verdict: %s)" % (plan_path, verdict))
    if verdict not in ("Validated", "Projected"):
        sys.exit(1)


if __name__ == "__main__":
    main()
