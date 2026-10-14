import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from _load import SKILLS_DIR, load, tool

TOOL = tool("pmf-test", "experiments.py")
EXAMPLE = os.path.join(SKILLS_DIR, "pmf-test", "experiments.example.json")

DEMAND_OK = {
    "id": "E1",
    "kind": "demand",
    "created": "2026-10-12",
    "hypothesis": "They will pay the price.",
    "method": "pre-sale page, 5 days",
    "audience": "park staff",
    "price": 4.5,
    "criteria": {"min_paid": 10, "max_cost_per_paid": 25},
    "results": {"date": "2026-10-19", "exposure": 480,
                "paid_conversions": 12, "cost": 150},
}


def run(args):
    return subprocess.run([sys.executable, TOOL] + args, capture_output=True, text=True)


class ExperimentsToolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.write({"experiments": [copy.deepcopy(DEMAND_OK)]})

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, data):
        with open(os.path.join(self.dir, "experiments.json"), "w") as fh:
            json.dump(data, fh)

    def mutate(self, change):
        entry = copy.deepcopy(DEMAND_OK)
        change(entry)
        self.write({"experiments": [entry]})

    def test_example_log_passes_check(self):
        os.makedirs(os.path.join(self.dir, "x"), exist_ok=True)
        shutil.copy(EXAMPLE, os.path.join(self.dir, "x", "experiments.json"))
        result = run(["check", "--dir", os.path.join(self.dir, "x")])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("E1 demand, created 2026-10-12, results 2026-10-19: PASS (2 of 2 criteria met)",
                      result.stdout)

    def test_check_reports_the_outcome(self):
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS (2 of 2 criteria met)", result.stdout)

    def test_failed_outcome_is_not_an_error(self):
        def change(entry):
            entry["results"]["paid_conversions"] = 2
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("FAIL (0 of 2 criteria met)", result.stdout)

    def test_mixed_outcome(self):
        def change(entry):
            entry["results"]["paid_conversions"] = 12
            entry["criteria"]["min_conversion"] = 0.5
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertIn("MIXED (2 of 3 criteria met)", result.stdout)

    def test_zero_paid_fails_the_cost_criterion(self):
        def change(entry):
            entry["criteria"] = {"max_cost_per_paid": 25}
            entry["results"]["paid_conversions"] = 0
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertIn("FAIL (0 of 1 criteria met)", result.stdout)

    def test_string_number_is_rejected(self):
        def change(entry):
            entry["results"]["paid_conversions"] = "12"
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("paid_conversions must be a whole number", result.stdout)

    def test_paid_above_exposure_is_rejected(self):
        def change(entry):
            entry["results"]["paid_conversions"] = 500
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("above exposure", result.stdout)

    def test_unknown_field_is_rejected(self):
        def change(entry):
            entry["results"]["paid"] = 12
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown field 'paid'", result.stdout)

    def test_results_before_creation_is_rejected(self):
        def change(entry):
            entry["results"]["date"] = "2026-10-01"
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("before the test was created", result.stdout)

    def test_unknown_criterion_is_rejected(self):
        def change(entry):
            entry["criteria"] = {"min_paying_customers": 5}
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown criterion 'min_paying_customers'", result.stdout)

    def test_rate_above_one_is_rejected(self):
        def change(entry):
            entry["criteria"] = {"min_conversion": 2}
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("1 or less", result.stdout)

    def test_duplicate_ids_are_rejected(self):
        self.write({"experiments": [copy.deepcopy(DEMAND_OK), copy.deepcopy(DEMAND_OK)]})
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate id 'E1'", result.stdout)

    def test_price_belongs_to_demand_tests_only(self):
        def change(entry):
            entry["kind"] = "retention"
            entry["criteria"] = {"min_repeat_rate": 0.4}
            entry["results"] = {"date": "2026-10-19", "cohort": 30, "repeat_buyers": 9}
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("'price' belongs to demand tests only", result.stdout)

    def test_retention_entry_is_valid(self):
        entry = {
            "id": "E2", "kind": "retention", "created": "2026-10-25",
            "hypothesis": "First-week buyers return.",
            "method": "repeat purchases in weeks 2 to 4",
            "audience": "the first 30 buyers",
            "criteria": {"min_repeat_rate": 0.4},
            "results": {"date": "2026-11-20", "cohort": 30, "repeat_buyers": 9},
        }
        self.write({"experiments": [entry]})
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("FAIL (0 of 1 criteria met)", result.stdout)

    def test_report_writes_test_md(self):
        result = run(["report", "--dir", self.dir])
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.dir, "test.md")) as fh:
            report = fh.read()
        self.assertIn("# Real-world tests", report)
        self.assertIn("**Outcome: PASS**", report)
        self.assertIn("| max_cost_per_paid | 25.00 | 12.50 | yes |", report)

    def test_planned_entry_has_no_outcome_yet(self):
        entry = copy.deepcopy(DEMAND_OK)
        del entry["results"]
        self.write({"experiments": [entry]})
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("planned, no results yet", result.stdout)

    def test_evaluate_is_pure_for_compile(self):
        experiments = load("pmf-test", "experiments")
        entries, problems = experiments.validate_all([copy.deepcopy(DEMAND_OK)])
        self.assertEqual(problems, [])
        result = experiments.evaluate(entries[0])
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["metrics"]["cost_per_paid"], 12.5)
        self.assertEqual(result["metrics"]["revenue_collected"], 54.0)

    def test_missing_file_is_an_error(self):
        result = run(["check", "--dir", os.path.join(self.dir, "nowhere")])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no test log", result.stderr)


if __name__ == "__main__":
    unittest.main()
