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
                "paid_conversions": 12, "refunds": 0, "cost": 150},
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

    def write(self, data, lock=True, keep_lock=False):
        """Log the tests the honest way: plan them, lock them with check, then add results."""
        path = os.path.join(self.dir, "experiments.json")
        lock_path = os.path.join(self.dir, "experiments.lock.json")
        if not keep_lock and os.path.isfile(lock_path):
            os.unlink(lock_path)
        if lock:
            planned = copy.deepcopy(data)
            for entry in planned["experiments"]:
                entry.pop("results", None)
            with open(path, "w") as fh:
                json.dump(planned, fh)
            run(["check", "--dir", self.dir])
        with open(path, "w") as fh:
            json.dump(data, fh)

    def mutate(self, change):
        entry = copy.deepcopy(DEMAND_OK)
        change(entry)
        self.write({"experiments": [entry]})

    def test_example_log_passes_check(self):
        with open(EXAMPLE) as fh:
            self.write(json.load(fh))
        result = run(["check", "--dir", self.dir])
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
            entry["results"]["paid_conversions"] = 0
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertIn("FAIL (0 of 2 criteria met)", result.stdout)

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
            entry["criteria"] = {"min_paid": 10, "min_conversion": 2}
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

    def test_one_paid_friend_cannot_be_the_bar(self):
        """Review probe: min_paid 1 at exposure 1 compiled to Validated."""
        def change(entry):
            entry["criteria"] = {"min_paid": 1}
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("min_paid must be 5 or more", result.stdout)

    def test_demand_test_needs_min_paid(self):
        def change(entry):
            entry["criteria"] = {"max_cost_per_paid": 25}
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("a demand test needs min_paid", result.stdout)

    def test_refunds_come_off_the_paid_count(self):
        """Review probe: the example counted 12 paid while 3 asked for refunds."""
        def change(entry):
            entry["results"]["refunds"] = 3
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertIn("MIXED (1 of 2 criteria met)", result.stdout)

    def test_refunds_above_paid_are_rejected(self):
        def change(entry):
            entry["results"]["refunds"] = 13
        self.mutate(change)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("refunds (13) is above paid_conversions", result.stdout)

    def test_tiny_cohort_cannot_pass_a_rate(self):
        """Review probe: 1 repeat of 2 passed a 40% bar."""
        entry = {
            "id": "E2", "kind": "retention", "created": "2026-10-25",
            "hypothesis": "Buyers return.", "method": "loyalty cards", "audience": "first buyers",
            "criteria": {"min_repeat_rate": 0.4},
            "results": {"date": "2026-11-20", "cohort": 2, "repeat_buyers": 1},
        }
        self.write({"experiments": [entry]})
        result = run(["check", "--dir", self.dir])
        self.assertIn("FAIL (0 of 1 criteria met)", result.stdout)

    def test_wilson_lower_bound(self):
        experiments = load("pmf-test", "experiments")
        self.assertAlmostEqual(experiments.wilson_low(1, 2), 0.0945, places=3)
        self.assertAlmostEqual(experiments.wilson_low(50, 100), 0.4038, places=3)
        self.assertEqual(experiments.wilson_low(0, 10), 0.0)

    def test_check_locks_a_planned_test(self):
        entry = copy.deepcopy(DEMAND_OK)
        del entry["results"]
        self.write({"experiments": [entry]}, lock=False)
        result = run(["check", "--dir", self.dir])
        self.assertIn("locked E1", result.stdout)
        with open(os.path.join(self.dir, "experiments.lock.json")) as fh:
            self.assertIn("E1", json.load(fh))

    def test_results_without_a_lock_are_rejected(self):
        self.write({"experiments": [copy.deepcopy(DEMAND_OK)]}, lock=False)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("never locked", result.stdout)

    def test_criteria_moved_after_the_lock_are_rejected(self):
        """Review probe: criteria could be edited after the results came in."""
        entry = copy.deepcopy(DEMAND_OK)
        entry["results"]["paid_conversions"] = 8
        self.write({"experiments": [entry]})
        entry["criteria"]["min_paid"] = 8
        self.write({"experiments": [entry]}, lock=False, keep_lock=True)
        result = run(["check", "--dir", self.dir])
        self.assertEqual(result.returncode, 1)
        self.assertIn("changed after they were locked", result.stdout)

    def test_missing_file_is_an_error(self):
        result = run(["check", "--dir", os.path.join(self.dir, "nowhere")])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no test log", result.stderr)


if __name__ == "__main__":
    unittest.main()
