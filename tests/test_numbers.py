import json
import os
import subprocess
import sys
import tempfile
import unittest

from _load import SKILLS_DIR, tool

ECON = tool("pmf-numbers", "unit_economics.py")
EXAMPLE = os.path.join(SKILLS_DIR, "pmf-numbers", "example.json")


def run(path):
    return subprocess.run([sys.executable, ECON, path], capture_output=True, text=True)


def with_json(tmp_dir, mutate):
    with open(EXAMPLE) as fh:
        data = json.load(fh)
    mutate(data)
    path = os.path.join(tmp_dir, "numbers.json")
    with open(path, "w") as fh:
        json.dump(data, fh)
    return path


class UnitEconomicsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_example_numbers_are_exact(self):
        result = run(EXAMPLE)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("Each drink leaves 2.90 after its own costs.", out)
        self.assertIn("Break-even: 44 drinks per day", out)
        self.assertIn("Against capacity (180 per day): break-even fits.", out)
        self.assertIn("margin 44.3%", out)
        self.assertIn("| 1 | 45 | 6075.00 | 115.00 | -18385.00 |", out)
        self.assertIn("Year 1 revenue: 182250.00. Year 1 operating profit: 71850.00.", out)
        self.assertIn("Cash needed before it pays for itself: 18385.00.", out)
        self.assertIn("earned back in month 5", out)
        self.assertIn("Price 10% lower: each unit leaves 2.45, year 1 operating becomes 53625.00.", out)
        self.assertIn("Volume 20% lower: year 1 operating becomes 48360.00.", out)
        self.assertIn("Variable cost 10% higher: each unit leaves 2.74, year 1 operating becomes 65370.00.", out)

    def test_missing_field_is_an_error(self):
        path = with_json(self.tmp.name, lambda d: d.pop("price"))
        result = run(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing field 'price'", result.stderr)

    def test_ramp_must_have_twelve_months(self):
        path = with_json(self.tmp.name, lambda d: d.update({"ramp_per_day": d["ramp_per_day"][:11]}))
        result = run(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("12 numbers", result.stderr)

    def test_losing_unit_is_flagged(self):
        path = with_json(self.tmp.name, lambda d: d.update({"price": 1.0}))
        result = run(path)
        self.assertIn("WARNING: each sale loses money", result.stdout)

    def test_out_writes_the_report(self):
        out = os.path.join(self.tmp.name, "numbers.md")
        result = subprocess.run([sys.executable, ECON, EXAMPLE, "--out", out],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(out) as fh:
            self.assertIn("# Unit economics", fh.read())


if __name__ == "__main__":
    unittest.main()
