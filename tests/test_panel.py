import json
import os
import subprocess
import sys
import tempfile
import unittest

from _load import tool

PANEL = tool("pmf-panel", "panel.py")

CUSTOMER = {
    "business": "Test Co",
    "target": "test buyers",
    "segments": [
        {"name": "a", "share": 60, "income": [30000, 60000]},
        {"name": "b", "share": 40, "income": [60000, 120000]},
    ],
    "behaviours": [
        {"name": "quick", "share": 50, "how": "buys fast"},
        {"name": "slow", "share": 50, "how": "reads every review"},
    ],
    "objections": ["too expensive", "does not trust carts", "no time"],
    "habits": ["walks past daily", "buys after lunch"],
}


def run(args, cwd):
    return subprocess.run([sys.executable, PANEL] + args, cwd=cwd,
                          capture_output=True, text=True)


class PanelTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        with open(os.path.join(self.dir, "customer.json"), "w") as fh:
            json.dump(CUSTOMER, fh)
        with open(os.path.join(self.dir, "pitch.md"), "w") as fh:
            fh.write("A coffee cart. 4.50 a drink.\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write_answers(self, panel_dir, manifest, buys, price=None):
        price = price or {"too_cheap": 2, "cheap": 3, "expensive": 5, "too_expensive": 8}
        os.makedirs(os.path.join(panel_dir, "answers"), exist_ok=True)
        for i, buyer in enumerate(manifest["buyers"]):
            buys_here = i < buys
            data = {"buyer": buyer["id"], "buys": buys_here,
                    "reason": "a reason" if not buys_here else "",
                    "flip": "a lower price" if not buys_here else "",
                    "price": dict(price)}
            with open(os.path.join(panel_dir, "answers", buyer["id"] + ".json"), "w") as fh:
                json.dump(data, fh)

    def test_init_deals_deterministic_cards(self):
        r1 = run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
                  "--n", "10", "--seed", "7", "--dir", "p1"], self.dir)
        r2 = run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
                  "--n", "10", "--seed", "7", "--dir", "p2"], self.dir)
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        cards1 = sorted(os.listdir(os.path.join(self.dir, "p1", "cards")))
        cards2 = sorted(os.listdir(os.path.join(self.dir, "p2", "cards")))
        self.assertEqual(cards1, cards2)
        self.assertEqual(len(cards1), 10)
        for name in cards1:
            with open(os.path.join(self.dir, "p1", "cards", name)) as f1:
                with open(os.path.join(self.dir, "p2", "cards", name)) as f2:
                    self.assertEqual(f1.read(), f2.read())

    def test_default_directory_supports_init_check_and_tally(self):
        init = run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
                    "--n", "4"], self.dir)
        self.assertEqual(init.returncode, 0, init.stderr)
        panel_dir = os.path.join(self.dir, "pmf", "panel")
        with open(os.path.join(panel_dir, "manifest.json")) as fh:
            manifest = json.load(fh)
        self.write_answers(panel_dir, manifest, buys=2)
        check = run(["check"], self.dir)
        self.assertEqual(check.returncode, 0, check.stderr)
        tally = run(["tally"], self.dir)
        self.assertEqual(tally.returncode, 0, tally.stderr)
        with open(os.path.join(panel_dir, "results.json")) as fh:
            self.assertEqual(json.load(fh)["buy_rate"], 0.5)

    def test_cards_embed_pitch_and_objection(self):
        run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
             "--n", "3", "--dir", "p"], self.dir)
        with open(os.path.join(self.dir, "p", "cards", "B001.md")) as fh:
            card = fh.read()
        self.assertIn("A coffee cart. 4.50 a drink.", card)
        self.assertIn("Doubt you carry:", card)

    def test_check_requires_every_answer(self):
        run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
             "--n", "4", "--dir", "p"], self.dir)
        self.assertEqual(run(["check", "--dir", "p"], self.dir).returncode, 1)
        with open(os.path.join(self.dir, "p", "manifest.json")) as fh:
            manifest = json.load(fh)
        self.write_answers(os.path.join(self.dir, "p"), manifest, buys=2)
        self.assertEqual(run(["check", "--dir", "p"], self.dir).returncode, 0)

    def test_malformed_answer_fails_check(self):
        run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
             "--n", "2", "--dir", "p"], self.dir)
        with open(os.path.join(self.dir, "p", "manifest.json")) as fh:
            manifest = json.load(fh)
        self.write_answers(os.path.join(self.dir, "p"), manifest, buys=1)
        path = os.path.join(self.dir, "p", "answers", "B001.json")
        with open(path) as fh:
            data = json.load(fh)
        del data["price"]
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["check", "--dir", "p"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("B001", result.stdout)

    def test_tally_computes_rates_and_medians(self):
        run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
             "--n", "10", "--seed", "7", "--dir", "p"], self.dir)
        with open(os.path.join(self.dir, "p", "manifest.json")) as fh:
            manifest = json.load(fh)
        self.write_answers(os.path.join(self.dir, "p"), manifest, buys=6)
        result = run(["tally", "--dir", "p"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.dir, "p", "results.json")) as fh:
            results = json.load(fh)
        self.assertEqual(results["answered"], 10)
        self.assertEqual(results["buy_rate"], 0.6)
        self.assertEqual(results["price"], {"too_cheap": 2, "cheap": 3,
                                            "expensive": 5, "too_expensive": 8})
        self.assertEqual(results["n"], 10)
        with open(os.path.join(self.dir, "p", "results.md")) as fh:
            self.assertIn("Why buyers passed", fh.read())

    def test_tally_refuses_empty_panel(self):
        run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
             "--n", "2", "--dir", "p"], self.dir)
        self.assertNotEqual(run(["tally", "--dir", "p"], self.dir).returncode, 0)


if __name__ == "__main__":
    unittest.main()
