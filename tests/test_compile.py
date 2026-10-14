import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from _load import SKILLS_DIR, load, tool

COMPILE = tool("pmf-plan", "compile.py")
STATUS = tool("pmf", "status.py")
EXP_ECON = tool("pmf-numbers", "unit_economics.py")
EXAMPLE_NUMBERS = os.path.join(SKILLS_DIR, "pmf-numbers", "example.json")
EXAMPLE_EXPERIMENTS = os.path.join(SKILLS_DIR, "pmf-test", "experiments.example.json")
EXPERIMENTS = tool("pmf-test", "experiments.py")


def run(args, cwd):
    return subprocess.run([sys.executable, COMPILE] + args, cwd=cwd,
                          capture_output=True, text=True)


class CompileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.pmf = os.path.join(self.dir, "pmf")
        os.makedirs(os.path.join(self.pmf, "panel"))
        shutil.copy(EXAMPLE_NUMBERS, os.path.join(self.pmf, "numbers.json"))
        with open(os.path.join(self.pmf, "idea.md"), "w") as fh:
            fh.write("# Test Biz\n\nA thing for people.\n")
        self.write_panel(0.4)

    def tearDown(self):
        self.tmp.cleanup()

    def write_panel(self, buy_rate, coverage=1.0, n=30):
        answered = max(1, int(round(n * coverage)))
        path = os.path.join(self.pmf, "panel", "results.json")
        with open(path, "w") as fh:
            json.dump({"n": n, "answered": answered, "coverage": coverage,
                       "buy_rate": buy_rate}, fh)

    def add_experiments(self, change=None):
        """Plan the tests, lock them with check, then record the results."""
        with open(EXAMPLE_EXPERIMENTS) as fh:
            data = json.load(fh)
        if change:
            change(data["experiments"])
        path = os.path.join(self.pmf, "experiments.json")
        planned = json.loads(json.dumps(data))
        for entry in planned["experiments"]:
            entry.pop("results", None)
        with open(path, "w") as fh:
            json.dump(planned, fh)
        subprocess.run([sys.executable, EXPERIMENTS, "check", "--dir", self.pmf],
                       check=True, capture_output=True, text=True)
        with open(path, "w") as fh:
            json.dump(data, fh)

    def fail_the_experiment(self):
        def change(tests):
            tests[0]["results"].update({"paid_conversions": 3, "refunds": 0})
        self.add_experiments(change)

    def plan(self):
        with open(os.path.join(self.pmf, "plan.md")) as fh:
            return fh.read()


class Verdicts(CompileTest):
    def test_projected_without_a_real_test(self):
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = self.plan()
        self.assertIn("**Verdict: Projected**", plan)
        self.assertIn("No real-world tests logged yet", plan)
        self.assertIn("Simulated panel: buy rate 40%", plan)

    def test_validated_with_a_passing_test(self):
        self.add_experiments()
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = self.plan()
        self.assertIn("**Verdict: Validated**", plan)
        self.assertIn("real test E1: PASS", plan)
        self.assertIn("| E1 | demand | 2026-10-12 | 2026-10-19 | 2 of 2 | PASS |", plan)

    def test_failed_test_beats_profitable_numbers(self):
        """The review's regression: a failed launch test must never compile to Profitable."""
        self.fail_the_experiment()
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 1)
        plan = self.plan()
        self.assertIn("**Verdict: Not yet**", plan)
        self.assertIn("Real test E1: min_paid | FAIL | 3 paid after refunds against a bar of 10", plan)
        self.assertIn("Change one thing against the missed criteria", plan)

    def test_later_retention_pass_cannot_hide_a_failed_demand_test(self):
        """Review probe: 0 of 500 buyers, then 1 repeat of 2, compiled to Validated."""
        def change(tests):
            tests[0]["results"].update({"paid_conversions": 0, "refunds": 0})
            tests[1]["criteria"] = {"min_repeat_rate": 0.1}
            tests[1]["results"] = {"date": "2026-11-20", "cohort": 30, "repeat_buyers": 20}
        self.add_experiments(change)
        result = run(["--dir", "pmf", "--check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Verdict: Not yet", result.stdout)
        self.assertIn("real test E1: FAIL", result.stdout)

    def test_failed_retention_blocks_validated(self):
        def change(tests):
            tests[1]["results"] = {"date": "2026-11-20", "cohort": 30, "repeat_buyers": 3}
        self.add_experiments(change)
        result = run(["--dir", "pmf", "--check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Verdict: Not yet", result.stdout)
        self.assertIn("Real test E2: min_repeat_rate", result.stdout)

    def test_a_test_below_the_plan_price_cannot_validate(self):
        """Review probe: a test at 0.01 validated a 4.50 plan."""
        def change(tests):
            tests[0]["price"] = 3.0
        self.add_experiments(change)
        result = run(["--dir", "pmf", "--check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("[FAIL] Real test E1: price: tested at 3.00 against a plan price of 4.50",
                      result.stdout)

    def test_criteria_moved_after_the_lock_are_incomplete(self):
        self.add_experiments()
        path = os.path.join(self.pmf, "experiments.json")
        with open(path) as fh:
            data = json.load(fh)
        data["experiments"][0]["criteria"]["min_paid"] = 5
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("**Verdict: Incomplete**", self.plan())
        self.assertIn("changed after they were locked", self.plan())

    def test_ungrounded_panel_objections_are_uncertain(self):
        path = os.path.join(self.pmf, "panel", "results.json")
        with open(path) as fh:
            data = json.load(fh)
        data["grounded_objections"] = [1, 6]
        with open(path, "w") as fh:
            json.dump(data, fh)
        run(["--dir", "pmf"], self.dir)
        self.assertIn("Panel objections without a real buyer quote behind them: 5 of 6", self.plan())

    def test_panel_alone_cannot_validate(self):
        self.write_panel(1.0)
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("**Verdict: Projected**", self.plan())

    def test_a_low_panel_rate_does_not_block_projection(self):
        self.write_panel(0.0)
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = self.plan()
        self.assertIn("**Verdict: Projected**", plan)
        self.assertIn("buy rate 0%", plan)

    def test_low_panel_coverage_is_called_noise(self):
        self.write_panel(0.4, coverage=0.1, n=100)
        run(["--dir", "pmf"], self.dir)
        self.assertIn("treat it as noise", self.plan())

    def test_incomplete_without_numbers(self):
        os.unlink(os.path.join(self.pmf, "numbers.json"))
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 1)
        plan = self.plan()
        self.assertIn("**Verdict: Incomplete**", plan)
        self.assertIn("numbers.json is missing", plan)

    def test_invalid_numbers_are_incomplete(self):
        path = os.path.join(self.pmf, "numbers.json")
        with open(path) as fh:
            data = json.load(fh)
        data["plan_per_day"] = 900
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("numbers.json is invalid", self.plan())
        self.assertIn("impossible volume", self.plan())

    def test_invalid_experiments_are_incomplete(self):
        self.add_experiments()
        path = os.path.join(self.pmf, "experiments.json")
        with open(path) as fh:
            data = json.load(fh)
        data["experiments"][0]["results"]["paid"] = 12
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("experiments.json is invalid", self.plan())

    def test_check_writes_nothing_and_reports(self):
        result = run(["--dir", "pmf", "--check"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Verdict: Projected", result.stdout)
        self.assertIn("[pass] Each unit earns money", result.stdout)
        self.assertFalse(os.path.isfile(os.path.join(self.pmf, "plan.md")))

    def test_check_exit_code_follows_the_verdict(self):
        self.fail_the_experiment()
        result = run(["--dir", "pmf", "--check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Verdict: Not yet", result.stdout)
        self.assertFalse(os.path.isfile(os.path.join(self.pmf, "plan.md")))

    def test_capacity_absent_is_not_a_failure(self):
        path = os.path.join(self.pmf, "numbers.json")
        with open(path) as fh:
            data = json.load(fh)
        del data["capacity_per_day"]
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not checked: no capacity_per_day given", self.plan())


class PlanDocument(CompileTest):
    def test_key_numbers_match_the_engine(self):
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        economics = load("pmf-numbers", "unit_economics")
        with open(EXAMPLE_NUMBERS) as fh:
            analysis = economics.analyse(json.load(fh))
        plan = self.plan()
        self.assertIn("each drink leaves 2.90", plan)
        self.assertIn("Year 1 operating profit: %.2f" % analysis["year1_operating"], plan)
        self.assertIn("Cash needed before it pays for itself: %.2f" % analysis["cash_needed"], plan)
        self.assertIn("Payback: month %d" % analysis["payback_month"], plan)

    def test_open_pressure_conditions_are_listed(self):
        with open(os.path.join(self.pmf, "pressure.md"), "w") as fh:
            fh.write("# Pressure\n\n- [x] price checked\n- [ ] demand test passed\n")
        run(["--dir", "pmf"], self.dir)
        plan = self.plan()
        self.assertIn("Conditions from the pressure test still open: 1 of 2", plan)
        self.assertIn("| demand test passed | **open** |", plan)

    def test_unsourced_costs_are_called_assumptions(self):
        run(["--dir", "pmf"], self.dir)
        plan = self.plan()
        # the example has 16 cost lines, 5 with a source
        self.assertIn("Cost lines without a source: 11 of 16", plan)

    def test_stale_recorded_inputs_are_flagged(self):
        with open(os.path.join(self.pmf, "offer.md"), "w") as fh:
            fh.write("price 4.50\n")
        subprocess.run([sys.executable, STATUS, "record", "--dir", "pmf",
                        "--artifact", "numbers.json", "--input", "offer.md",
                        "--skill", "pmf-numbers"], cwd=self.dir, check=True,
                       capture_output=True, text=True)
        with open(os.path.join(self.pmf, "offer.md"), "w") as fh:
            fh.write("price 3.90\n")
        run(["--dir", "pmf"], self.dir)
        plan = self.plan()
        self.assertIn("Recorded files whose inputs or content changed", plan)
        self.assertIn("Rerun those stages", plan)
        self.assertIn("| `numbers.json` | present | STALE | `pmf-numbers` |", plan)


if __name__ == "__main__":
    unittest.main()
