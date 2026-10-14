import json
import os
import subprocess
import sys
import tempfile
import unittest

from _load import SKILLS_DIR, load, tool

ECON = tool("pmf-numbers", "unit_economics.py")
EXAMPLE = os.path.join(SKILLS_DIR, "pmf-numbers", "example.json")


def run(args):
    return subprocess.run([sys.executable, ECON] + args, capture_output=True, text=True)


def with_json(tmp_dir, mutate, name="numbers.json"):
    with open(EXAMPLE) as fh:
        data = json.load(fh)
    mutate(data)
    path = os.path.join(tmp_dir, name)
    with open(path, "w") as fh:
        json.dump(data, fh)
    return path


class UnitEconomicsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_example_numbers_are_exact(self):
        result = run([EXAMPLE])
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("Each drink leaves 2.90 after its own costs.", out)
        self.assertIn("Break-even: 44 drinks per day", out)
        self.assertIn("Against capacity (180 per day): break-even fits.", out)
        self.assertIn("margin 44.3%", out)
        self.assertIn("| 1 | 45 | 6075.00 | 115.00 | -18385.00 |", out)
        self.assertIn("Year 1 revenue: 182250.00. Year 1 operating profit: 71850.00.", out)
        self.assertIn("After the 18500.00 startup spend: 53350.00.", out)
        self.assertIn("Cash needed before it pays for itself: 18500.00"
                      " (deepest point: the startup spend before month 1).", out)
        self.assertIn("Startup spend is earned back in month 5.", out)

    def test_example_itemises_costs_with_sources(self):
        out = run([EXAMPLE]).stdout
        self.assertIn("| coffee beans | 0.70 | roaster list price, 2026-09-30 |", out)
        self.assertIn("cart lease and pitch fee 900.00 (council pitch schedule, 2026-09-28)", out)
        self.assertIn("| Winter footfall (volume -35%) | 2.90 | 44 | 30742.50 |", out)
        self.assertIn("| Chain opens across the road (price -10%, volume -20%) | 2.45 | 52 | 33780.00 |", out)

    def test_cash_needed_includes_startup_before_month_one(self):
        """The review's regression: a profitable month 1 must not hide the startup spend."""
        economics = load("pmf-numbers", "unit_economics")
        data = {"unit": "cup", "price": 4.0, "variable": 1.0, "fixed_monthly": 10.0,
                "startup": 100.0, "plan_per_day": 20,
                "ramp_per_day": [20] * 12}
        analysis = economics.analyse(data)
        self.assertEqual(analysis["cash_needed"], 100.0)
        self.assertIsNone(analysis["cash_deepest_month"])

    def test_deepest_month_is_named_when_losses_dig_below_startup(self):
        economics = load("pmf-numbers", "unit_economics")
        data = {"unit": "cup", "price": 2.0, "variable": 1.0, "fixed_monthly": 300.0,
                "startup": 100.0, "plan_per_day": 20,
                "ramp_per_day": [5] * 12}
        analysis = economics.analyse(data)
        self.assertEqual(analysis["cash_deepest_month"], 12)
        self.assertGreater(analysis["cash_needed"], 100.0)

    def test_analysis_matches_the_example_numbers(self):
        economics = load("pmf-numbers", "unit_economics")
        with open(EXAMPLE) as fh:
            data = json.load(fh)
        analysis = economics.analyse(data)
        self.assertEqual(analysis["contribution"], 2.9)
        self.assertEqual(analysis["year1_operating"], 71850.0)
        self.assertEqual(analysis["months"][-1]["cumulative"], 53350.0)
        self.assertEqual(analysis["payback_month"], 5)

    def test_days_per_month_changes_the_break_even(self):
        path = with_json(self.tmp.name, lambda d: d.update({"days_per_month": 22}))
        out = run([path]).stdout
        self.assertIn("Break-even: 60 drinks per day", out)
        self.assertIn("22 selling days a month", out)

    def test_missing_field_is_an_error(self):
        path = with_json(self.tmp.name, lambda d: d.pop("price"))
        result = run([path])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("price", result.stderr)

    def test_ramp_must_have_twelve_months(self):
        path = with_json(self.tmp.name, lambda d: d.update({"ramp_per_day": d["ramp_per_day"][:11]}))
        result = run([path])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("12 numbers", result.stderr)

    def test_unknown_field_is_an_error(self):
        path = with_json(self.tmp.name, lambda d: d.update({"fixd_monthly": 10}))
        result = run([path])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown field 'fixd_monthly'", result.stderr)

    def test_both_cost_forms_at_once_is_an_error(self):
        path = with_json(self.tmp.name, lambda d: d.update({"variable": 1.0}))
        result = run([path])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("either 'variable' or 'variable_items'", result.stderr)

    def test_negative_cost_is_rejected(self):
        path = with_json(self.tmp.name, lambda d: d.update({"price": -1.0}))
        result = run([path])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("price", result.stderr)

    def test_plan_above_capacity_is_impossible(self):
        path = with_json(self.tmp.name, lambda d: d.update({"plan_per_day": 500}))
        result = run([path])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("impossible volume", result.stderr)

    def test_ramp_above_capacity_is_impossible(self):
        ramp = [45, 70, 95, 110, 120, 130, 140, 140, 135, 130, 120, 300]
        path = with_json(self.tmp.name, lambda d: d.update({"ramp_per_day": ramp}))
        result = run([path])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("month 12 (300)", result.stderr)

    def test_scenario_typo_is_rejected(self):
        path = with_json(self.tmp.name, lambda d: d.update(
            {"scenarios": [{"name": "x", "volum_scale": 0.5}]}))
        result = run([path])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown field 'volum_scale'", result.stderr)

    def test_legacy_flat_costs_still_work(self):
        economics = load("pmf-numbers", "unit_economics")
        data = {"unit": "drink", "price": 4.5, "variable": 1.6, "fixed_monthly": 3800,
                "startup": 18500, "plan_per_day": 140,
                "ramp_per_day": [45, 70, 95, 110, 120, 130, 140, 140, 135, 130, 120, 115],
                "capacity_per_day": 180}
        analysis = economics.analyse(data)
        self.assertEqual(analysis["year1_operating"], 71850.0)
        self.assertEqual(analysis["cash_needed"], 18500.0)

    def test_price_and_volume_overrides(self):
        result = run([EXAMPLE, "--volume", "0.8", "--price", "3.90"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("What-if overrides applied: price 3.90, volume x0.8.", result.stdout)
        self.assertIn("Year 1 operating profit: 28920.00.", result.stdout)

    def test_json_mode_prints_the_analysis(self):
        result = run([EXAMPLE, "--json"])
        self.assertEqual(result.returncode, 0, result.stderr)
        analysis = json.loads(result.stdout)
        self.assertEqual(analysis["contribution"], 2.9)
        self.assertEqual(analysis["cash_needed"], 18500.0)

    def test_out_writes_the_report(self):
        out = os.path.join(self.tmp.name, "numbers.md")
        result = run([EXAMPLE, "--out", out])
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(out) as fh:
            self.assertIn("# Unit economics", fh.read())


if __name__ == "__main__":
    unittest.main()
