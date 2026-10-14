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

GOOD_PRICE = {"too_cheap": 2, "cheap": 3, "expensive": 5, "too_expensive": 8}


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

    def init(self, *extra, panel="pmf/panel"):
        result = run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
                      "--dir", panel] + list(extra), self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.dir, panel, "manifest.json")) as fh:
            return json.load(fh)

    def answer(self, panel, buyer, buys, price=None, **overrides):
        data = {"buyer": buyer["id"], "buys": buys,
                "reason": "it is convenient" if buys else "too dear",
                "flip": "" if buys else "a lower price",
                "price": dict(price or GOOD_PRICE)}
        data.update(overrides)
        path = os.path.join(self.dir, panel, "answers", buyer["id"] + ".json")
        with open(path, "w") as fh:
            json.dump(data, fh)

    def answer_all(self, panel, manifest, buys_n):
        for i, buyer in enumerate(manifest["buyers"]):
            self.answer(panel, buyer, i < buys_n)

    def test_init_deals_deterministic_cards(self):
        run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
             "--n", "10", "--seed", "7", "--dir", "p1"], self.dir)
        run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
             "--n", "10", "--seed", "7", "--dir", "p2"], self.dir)
        cards1 = sorted(os.listdir(os.path.join(self.dir, "p1", "cards")))
        cards2 = sorted(os.listdir(os.path.join(self.dir, "p2", "cards")))
        self.assertEqual(cards1, cards2)
        self.assertEqual(len(cards1), 10)
        for name in cards1:
            with open(os.path.join(self.dir, "p1", "cards", name)) as f1:
                with open(os.path.join(self.dir, "p2", "cards", name)) as f2:
                    self.assertEqual(f1.read(), f2.read())

    def test_exact_quotas_match_the_customer_shares(self):
        manifest = self.init("--n", "10", "--seed", "7")
        segments = {}
        behaviours = {}
        for buyer in manifest["buyers"]:
            segments[buyer["segment"]] = segments.get(buyer["segment"], 0) + 1
            behaviours[buyer["behaviour"]] = behaviours.get(buyer["behaviour"], 0) + 1
        self.assertEqual(segments, {"a": 6, "b": 4})
        self.assertEqual(behaviours, {"quick": 5, "slow": 5})

    def test_card_embeds_pitch_behaviour_and_objection(self):
        self.init("--n", "3")
        with open(os.path.join(self.dir, "pmf", "panel", "cards", "B001.md")) as fh:
            card = fh.read()
        self.assertIn("A coffee cart. 4.50 a drink.", card)
        self.assertIn("Doubt you carry:", card)
        self.assertIn("Buying behaviour:", card)
        self.assertIn("must climb in order", card)

    def test_default_flow_check_and_tally(self):
        manifest = self.init("--n", "4")
        self.answer_all("pmf/panel", manifest, 2)
        check = run(["check"], self.dir)
        self.assertEqual(check.returncode, 0, check.stderr)
        tally = run(["tally"], self.dir)
        self.assertEqual(tally.returncode, 0, tally.stderr)
        with open(os.path.join(self.dir, "pmf", "panel", "results.json")) as fh:
            results = json.load(fh)
        self.assertEqual(results["buy_rate"], 0.5)
        self.assertEqual(results["coverage"], 1.0)
        self.assertEqual(results["price"], GOOD_PRICE)
        self.assertEqual(results["grounded_objections"], [0, 3])

    def test_sourced_objections_are_counted_and_dealt_as_text(self):
        with open(os.path.join(self.dir, "customer.json")) as fh:
            customer = json.load(fh)
        customer["objections"][0] = {"text": "too expensive",
                                     "source": "https://example.com/review/1"}
        with open(os.path.join(self.dir, "customer.json"), "w") as fh:
            json.dump(customer, fh)
        manifest = self.init("--n", "6")
        self.assertEqual(manifest["grounded_objections"], [1, 3])
        for buyer in manifest["buyers"]:
            self.assertIsInstance(buyer["objection"], str)

    def test_sourced_objection_without_a_source_is_rejected(self):
        with open(os.path.join(self.dir, "customer.json")) as fh:
            customer = json.load(fh)
        customer["objections"][0] = {"text": "too expensive", "source": ""}
        with open(os.path.join(self.dir, "customer.json"), "w") as fh:
            json.dump(customer, fh)
        result = run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
                      "--dir", "pmf/panel"], self.dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sourced objection", result.stderr)

    def test_check_requires_every_answer(self):
        self.init("--n", "4")
        self.assertEqual(run(["check"], self.dir).returncode, 1)

    def test_text_boolean_is_rejected(self):
        manifest = self.init("--n", "2")
        self.answer_all("pmf/panel", manifest, 1)
        path = os.path.join(self.dir, "pmf", "panel", "answers", "B002.json")
        with open(path) as fh:
            data = json.load(fh)
        data["buys"] = "false"
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("buys must be true or false", result.stdout)

    def test_reversed_price_answers_are_rejected(self):
        manifest = self.init("--n", "2")
        self.answer("pmf/panel", manifest["buyers"][0], True)
        self.answer("pmf/panel", manifest["buyers"][1], False,
                    price={"too_cheap": 8, "cheap": 5, "expensive": 3, "too_expensive": 2})
        result = run(["check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("climb in order", result.stdout)

    def test_wrong_buyer_id_is_rejected(self):
        manifest = self.init("--n", "2")
        self.answer_all("pmf/panel", manifest, 1)
        path = os.path.join(self.dir, "pmf", "panel", "answers", "B002.json")
        with open(path) as fh:
            data = json.load(fh)
        data["buyer"] = "B001"
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("buyer is 'B001' but the file is B002", result.stdout)

    def test_unknown_keys_are_rejected(self):
        manifest = self.init("--n", "2")
        self.answer_all("pmf/panel", manifest, 1)
        path = os.path.join(self.dir, "pmf", "panel", "answers", "B002.json")
        with open(path) as fh:
            data = json.load(fh)
        data["confidence"] = 0.9
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown keys confidence", result.stdout)

    def test_missing_flip_on_a_no_is_rejected(self):
        manifest = self.init("--n", "2")
        self.answer("pmf/panel", manifest["buyers"][0], False, flip="")
        self.answer("pmf/panel", manifest["buyers"][1], True)
        result = run(["check"], self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("flip must say what would change a no", result.stdout)

    def test_invalid_answers_do_not_enter_the_tally(self):
        manifest = self.init("--n", "4")
        self.answer_all("pmf/panel", manifest, 3)
        path = os.path.join(self.dir, "pmf", "panel", "answers", "B004.json")
        with open(path) as fh:
            data = json.load(fh)
        data["buys"] = "no"
        with open(path, "w") as fh:
            json.dump(data, fh)
        result = run(["tally"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.dir, "pmf", "panel", "results.json")) as fh:
            results = json.load(fh)
        self.assertEqual(results["answered"], 3)
        self.assertEqual(results["coverage"], 0.75)
        self.assertEqual(results["buy_rate"], 1.0)

    def test_reuse_keeps_the_roster_and_archives_the_run(self):
        manifest = self.init("--n", "4", "--seed", "11")
        self.answer_all("pmf/panel", manifest, 2)
        self.assertEqual(run(["tally"], self.dir).returncode, 0)
        with open(os.path.join(self.dir, "pitch.md"), "a") as fh:
            fh.write("Now 4.00 with the loyalty card.\n")
        result = run(["init", "--reuse", "pmf/panel", "--pitch", "pitch.md"], self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.dir, "pmf", "panel", "manifest.json")) as fh:
            new = json.load(fh)
        roster_old = [(b["id"], b["segment"], b["income"], b["objection"]) for b in manifest["buyers"]]
        roster_new = [(b["id"], b["segment"], b["income"], b["objection"]) for b in new["buyers"]]
        self.assertEqual(roster_old, roster_new)
        runs = os.listdir(os.path.join(self.dir, "pmf", "panel", "runs"))
        self.assertEqual(len(runs), 1)
        with open(os.path.join(self.dir, "pmf", "panel", "runs", runs[0], "results.json")) as fh:
            self.assertEqual(json.load(fh)["buy_rate"], 0.5)

    def test_runs_table_appears_after_a_second_tally(self):
        manifest = self.init("--n", "4", "--seed", "11")
        self.answer_all("pmf/panel", manifest, 1)
        self.assertEqual(run(["tally"], self.dir).returncode, 0)
        with open(os.path.join(self.dir, "pitch.md"), "a") as fh:
            fh.write("Now 4.00 with the loyalty card.\n")
        self.assertEqual(run(["init", "--reuse", "pmf/panel",
                              "--pitch", "pitch.md"], self.dir).returncode, 0)
        with open(os.path.join(self.dir, "pmf", "panel", "manifest.json")) as fh:
            manifest = json.load(fh)
        self.answer_all("pmf/panel", manifest, 3)
        self.assertEqual(run(["tally"], self.dir).returncode, 0)
        with open(os.path.join(self.dir, "pmf", "panel", "results.md")) as fh:
            results = fh.read()
        self.assertIn("Runs so far", results)
        self.assertIn("a different pitch", results)
        self.assertIn("this run", results)

    def test_tally_refuses_empty_panel(self):
        self.init("--n", "2")
        self.assertNotEqual(run(["tally"], self.dir).returncode, 0)

    def test_customer_share_must_be_positive(self):
        with open(os.path.join(self.dir, "customer.json")) as fh:
            customer = json.load(fh)
        customer["segments"][0]["share"] = 0
        with open(os.path.join(self.dir, "customer.json"), "w") as fh:
            json.dump(customer, fh)
        result = run(["init", "--customer", "customer.json", "--pitch", "pitch.md",
                      "--dir", "pmf/panel"], self.dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("above zero", result.stderr)


if __name__ == "__main__":
    unittest.main()
