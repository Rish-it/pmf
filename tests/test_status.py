import json
import os
import subprocess
import sys
import tempfile
import unittest

from _load import tool

STATUS = tool("pmf", "status.py")


def run(args, cwd):
    return subprocess.run([sys.executable, STATUS] + args, cwd=cwd,
                          capture_output=True, text=True)


def check_json(cwd):
    result = run(["check", "--json"], cwd)
    return result, json.loads(result.stdout)


class StatusTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        os.makedirs(os.path.join(self.dir, "pmf"))
        self.write("pmf/offer.md", "price 4.50\n")
        self.write("pmf/numbers.json", '{"price": 4.5}\n')
        self.write("pmf/numbers.md", "report\n")
        self.write("pmf/plan.md", "plan\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        with open(os.path.join(self.dir, rel), "w") as fh:
            fh.write(text)

    def record(self, artifact, inputs=(), skill=""):
        args = ["record", "--dir", "pmf", "--artifact", artifact]
        for one in inputs:
            args += ["--input", one]
        if skill:
            args += ["--skill", skill]
        return run(args, self.dir)

    def statuses(self, result):
        return {row["artifact"]: row["status"] for row in result["artifacts"]}

    def test_record_and_check_fresh(self):
        for args in (("numbers.json", ("offer.md",)), ("numbers.md", ("numbers.json",)),
                     ("plan.md", ("numbers.json",))):
            self.assertEqual(self.record(*args).returncode, 0)
        result, report = check_json(self.dir)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(set(self.statuses(report).values()), {"fresh"})
        self.assertEqual(report["counts"]["fresh"], 3)

    def test_changed_input_marks_dependents_stale(self):
        self.record("numbers.json", ("offer.md",))
        self.record("numbers.md", ("numbers.json",))
        self.record("plan.md", ("numbers.json",))
        self.write("pmf/offer.md", "price 3.90\n")
        result, report = check_json(self.dir)
        self.assertEqual(result.returncode, 1)
        statuses = self.statuses(report)
        self.assertEqual(statuses["numbers.json"], "stale")
        self.assertEqual(statuses["numbers.md"], "stale")
        self.assertEqual(statuses["plan.md"], "stale")
        notes = {row["artifact"]: row["note"] for row in report["artifacts"]}
        self.assertIn("offer.md changed", notes["numbers.json"])
        self.assertIn("depends on numbers.json", notes["plan.md"])

    def test_rewritten_artifact_is_changed_and_dependents_stale(self):
        self.record("numbers.json", ("offer.md",))
        self.record("plan.md", ("numbers.json",))
        self.write("pmf/numbers.json", '{"price": 5.0}\n')
        result, report = check_json(self.dir)
        self.assertEqual(result.returncode, 1)
        statuses = self.statuses(report)
        self.assertEqual(statuses["numbers.json"], "changed")
        self.assertEqual(statuses["plan.md"], "stale")

    def test_missing_artifact(self):
        self.record("numbers.md", ("numbers.json",))
        os.unlink(os.path.join(self.dir, "pmf", "numbers.md"))
        result, report = check_json(self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.statuses(report)["numbers.md"], "missing")

    def test_record_requires_the_inputs_to_exist(self):
        result = self.record("numbers.json", ("nowhere.md",))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no such input", result.stderr)

    def test_record_rejects_paths_outside_the_folder(self):
        result = self.record("../escape.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inside the pmf folder", result.stderr)

    def test_empty_ledger_is_clean(self):
        result, report = check_json(self.dir)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["artifacts"], [])

    def test_recording_again_clears_staleness(self):
        self.record("numbers.json", ("offer.md",))
        self.write("pmf/offer.md", "price 3.90\n")
        self.assertEqual(run(["check"], self.dir).returncode, 1)
        self.record("numbers.json", ("offer.md",))
        self.assertEqual(run(["check"], self.dir).returncode, 0)


if __name__ == "__main__":
    unittest.main()
