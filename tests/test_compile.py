import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from _load import SKILLS_DIR, load, tool

COMPILE = tool("pmf-plan", "compile.py")
EXAMPLE = os.path.join(SKILLS_DIR, "pmf-numbers", "example.json")


def run(args, cwd):
    return subprocess.run([sys.executable, COMPILE] + args, cwd=cwd,
                          capture_output=True, text=True)


class CompileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        pmf = os.path.join(self.dir, "pmf")
        os.makedirs(os.path.join(pmf, "panel"))
        shutil.copy(EXAMPLE, os.path.join(pmf, "numbers.json"))
        with open(os.path.join(pmf, "idea.md"), "w") as fh:
            fh.write("# Test Biz\n\nA thing for people.\n")
        self.write_panel(0.4)

    def tearDown(self):
        self.tmp.cleanup()

    def write_panel(self, buy_rate):
        path = os.path.join(self.dir, "pmf", "panel", "results.json")
        with open(path, "w") as fh:
            json.dump({"n": 100, "answered": 100, "buy_rate": buy_rate}, fh)

    def test_profitable_verdict(self):
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = os.path.join(self.dir, "pmf", "plan.md")
        self.assertTrue(os.path.isfile(plan))
        with open(plan) as fh:
            body = fh.read()
        self.assertIn("Verdict: **Profitable**", body)
        self.assertIn("Business plan: Test Biz", body)
        self.assertIn("| present |", body)

    def test_default_directory_and_research_coverage_index(self):
        result = run([], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = os.path.join(self.dir, "pmf", "plan.md")
        with open(plan) as fh:
            self.assertIn("| `research/reach.md` | missing | `pmf-research` |", fh.read())
        os.makedirs(os.path.join(self.dir, "pmf", "research"))
        with open(os.path.join(self.dir, "pmf", "research", "reach.md"), "w") as fh:
            fh.write("# Coverage\n\nPublic price pages read. Reviews unavailable.\n")
        result = run([], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(plan) as fh:
            self.assertIn("| `research/reach.md` | present | `pmf-research` |", fh.read())

    def test_low_buy_rate_is_not_yet(self):
        self.write_panel(0.1)
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 1)
        with open(os.path.join(self.dir, "pmf", "plan.md")) as fh:
            self.assertIn("Verdict: **Not yet**", fh.read())

    def test_min_buy_rate_flag_changes_the_bar(self):
        self.write_panel(0.2)
        strict = run(["--dir", "pmf"], self.dir)
        lenient = run(["--dir", "pmf", "--min-buy-rate", "0.15"], self.dir)
        self.assertEqual(strict.returncode, 1)
        self.assertEqual(lenient.returncode, 0, lenient.stderr)

    def test_missing_panel_is_incomplete_and_check_writes_nothing(self):
        os.unlink(os.path.join(self.dir, "pmf", "panel", "results.json"))
        check = run(["--dir", "pmf", "--check"], self.dir)
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertIn("Verdict: Incomplete", check.stdout)
        self.assertIn("pmf-panel", check.stdout)
        self.assertFalse(os.path.isfile(os.path.join(self.dir, "pmf", "plan.md")))
        full = run(["--dir", "pmf"], self.dir)
        self.assertEqual(full.returncode, 1)
        with open(os.path.join(self.dir, "pmf", "plan.md")) as fh:
            self.assertIn("cannot be completed yet", fh.read())

    def test_capacity_absent_is_not_a_failure(self):
        path = os.path.join(self.dir, "pmf", "numbers.json")
        with open(path) as fh:
            data = json.load(fh)
        del data["capacity_per_day"]
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["--dir", "pmf"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.dir, "pmf", "plan.md")) as fh:
            self.assertIn("not checked: no capacity_per_day given", fh.read())

    def test_verdict_numbers_agree_with_unit_economics(self):
        economics = load("pmf-numbers", "unit_economics")
        compiler = load("pmf-plan", "compile")
        with open(EXAMPLE) as fh:
            data = json.load(fh)
        rows = economics.year1(data)
        year1 = round(sum(r["operating"] for r in rows), 2)
        checks = compiler.numbers_check(data)
        self.assertEqual(checks["year1_operating"], year1)
        self.assertEqual(checks["contribution"], round(data["price"] - data["variable"], 2))


if __name__ == "__main__":
    unittest.main()
