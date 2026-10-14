---
name: pmf-test
description: >-
  The cheapest real-world test of demand, run before substantial building.
  Designs the test (a pre-sale page with a deposit, a pop-up, paid pilots, a
  waitlist with a founding offer), sets the success criteria before it runs,
  logs the actuals in pmf/experiments.json and reads the computed outcome:
  pass, fail or mixed. Logs retention tests after launch too. Use when the
  user says "test demand", "should I build this", "run a real test",
  "pre-sale", "pop-up", "waitlist", "is anyone actually paying", or after the
  numbers exist and before building anything substantial.
argument-hint: "[the test the user has in mind, or leave blank]"
---

# pmf-test

The panel is simulated. This stage is not: real people, real prices, real
money. One rule orders everything here:

**The criteria are set before the test runs, written down, and never moved
afterward.** A test without pre-set criteria is a story, not evidence.

The tool in this skill's folder keeps the log honest (below, EXP means
running `experiments.py` from this skill's folder):

```bash
python3 <this skill's folder>/experiments.py check --dir pmf
python3 <this skill's folder>/experiments.py report --dir pmf
```

State: `pmf/experiments.json` (the log) and `pmf/test.md` (the report the
tool writes). A filled example sits next to this file as
`experiments.example.json`.

## Step 1: pick the cheapest test that would change the decision

| business | the test | exposure | a paid conversion |
| --- | --- | --- | --- |
| Physical, walk-in | a pop-up or market stall for 2 to 4 days at real prices | people who stopped | one sale |
| Product to pre-order | a pre-sale page with a refundable deposit | visits to the page | one deposit paid |
| Service | three paid pilots at a reduced but real price | qualified offers made | one pilot paid |
| Software or content | a waitlist that collects an email, then a paid founding offer | people who saw the offer | one founding purchase |

A test that does not risk real money for the buyer is a poll; polls do not
count here. Read `pmf/offer.md` (what is sold and at what price),
`pmf/numbers.json` (what the price and costs must cover) and
`pmf/research/voice.md` (how to word the offer) before designing it.

If the cheapest test needs an asset (a page, a flyer, a booking flow), build
only that asset, minimally, in the project's normal folders. That is not
`pmf-build`'s product; it is the test rig.

## Step 2: write the test before running it

Add one entry to `pmf/experiments.json`, with no `results` key yet. The
example next to this file shows the full shape. The fields that matter:

- `hypothesis`: one sentence, with the number and the buyer ("Office workers
  will pay 4.50 for a cart drink without a discount").
- `method` and `audience`: what exactly runs and who sees it.
- `price`: the real price the test charges.
- `criteria`: the go/no-go numbers, fixed now. The demand criteria:
  - `min_paid`: how many paid conversions count as a pass. Tie it to
    `pmf/numbers.json`: enough buyers to cover the test's cost and prove the
    price, not a rounding error.
  - `min_conversion`: optional; only if the exposure number is meaningful.
  - `max_cost_per_paid`: the ceiling for reaching and converting one paying
    buyer, from the contribution per unit.

Run `check` now, before the test: it validates the criteria and the shape, so
a typo cannot waste a week.

## Step 3: run it

Set the test live for the dates written in the entry. While it runs, capture
exactly four things: how many people were exposed, how many paid, what the
test cost (ads, page, materials, refunds), and notes in the buyers' own
words. Count only payments that were not refunded before the results date;
refunds and near-misses go in `notes`. Do not help the test along (no
discounts that were not part of the offer, no friends counted as buyers).

## Step 4: record the results

Add the `results` object to the entry: `date`, `exposure`, `paid_conversions`,
`cost`, `notes`. Then:

```bash
python3 <this skill's folder>/experiments.py check --dir pmf
python3 <this skill's folder>/experiments.py report --dir pmf
```

The outcome is computed (pass when every criterion is met, fail when none,
mixed when some), never written by hand. Existing results are never edited:
a correction is a note, a new condition is a new test with a new id.

## Step 5: read the outcome and decide

- **Pass**: log it, then run `pmf-build`. The test bought the right to spend
  the next chunk of time and money.
- **Mixed or fail**: name the missed criteria and the cheapest single change
  behind them (price, audience, offer wording, channel), make that one
  change, and log the next test as a new id. Two changes at once make the
  next result unreadable.
- **Nothing ran**: an untested plan compiles to Projected, never Validated;
  say that to the user plainly.

## Step 6: after launch, test retention

A first purchase is interest; a repeat purchase is a market. After launch
(`pmf-launch`'s first 30 days), log a `retention` entry: cohort size,
`repeat_buyers` inside the window, and a `min_repeat_rate` criterion. The
same rules apply: criteria first, actuals second, outcome computed.

## Output

`pmf/experiments.json` (the log) and `pmf/test.md` (the computed report).
Then record the fingerprints, with the status tool in the `pmf` skill's
folder, so later changes can invalidate this evidence:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact experiments.json --input offer.md --input numbers.json --skill pmf-test
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact test.md --input experiments.json --skill pmf-test
```

List the upstream files the test actually read; leave out files that did not
exist yet.

Next: on a pass, run the `pmf-build` skill; on a mixed or failed result,
change one thing and run `pmf-test` again with a new id.
