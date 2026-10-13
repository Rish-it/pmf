import os
import statistics
import subprocess
import sys
import tempfile
import unittest

from _load import SKILLS_DIR, tool

VW = tool("pmf-offer", "van_westendorp.py")
EXAMPLE_CSV = os.path.join(SKILLS_DIR, "pmf-offer", "prices.example.csv")


def run(args):
    return subprocess.run([sys.executable, VW] + args, capture_output=True, text=True)


def medians_line(output):
    for line in output.splitlines():
        if line.startswith("Medians:"):
            return line
    return ""


class VanWestendorpTest(unittest.TestCase):
    def test_medians_on_example_csv(self):
        rows = []
        with open(EXAMPLE_CSV) as fh:
            for row in fh.read().strip().splitlines()[1:]:
                rows.append([float(v) for v in row.split(",")])
        expected = [round(statistics.median(col), 2) for col in zip(*rows)]
        result = run(["--csv", EXAMPLE_CSV])
        self.assertEqual(result.returncode, 0, result.stderr)
        line = medians_line(result.stdout)
        for value in expected:
            self.assertIn("%.2f" % value, line)

    def test_clean_case_points_and_verdicts(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("too_cheap,cheap,expensive,too_expensive\n")
            for _ in range(10):
                fh.write("2,3,5,8\n")
            path = fh.name
        try:
            result = run(["--csv", path, "--price", "5"])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Marginal cheapness (PMC): 3.50", result.stdout)
            self.assertIn("Marginal expensiveness (PME): 5.50", result.stdout)
            self.assertIn("Acceptable range: 3.50 to 5.50", result.stdout)
            self.assertIn("WITHIN the acceptable range", result.stdout)
            self.assertIn("BELOW", run(["--csv", path, "--price", "3"]).stdout)
            self.assertIn("ABOVE", run(["--csv", path, "--price", "9"]).stdout)
        finally:
            os.unlink(path)

    def test_no_crossing_reports_not_reached(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("too_cheap,cheap,expensive,too_expensive\n")
            for _ in range(10):
                fh.write("5,5,5,5\n")
            path = fh.name
        try:
            result = run(["--csv", path, "--price", "5"])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("not reached", result.stdout)
        finally:
            os.unlink(path)

    def test_thin_sample_warns(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("too_cheap,cheap,expensive,too_expensive\n")
            fh.write("2,3,5,8\n")
            path = fh.name
        try:
            self.assertIn("WARNING", run(["--csv", path]).stdout)
        finally:
            os.unlink(path)

    def test_bad_csv_dies(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("a,b,c\n1,2,3\n")
            path = fh.name
        try:
            self.assertNotEqual(run(["--csv", path]).returncode, 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
