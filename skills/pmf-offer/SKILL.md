---
name: pmf-offer
description: >-
  Builds the offer and prices it: turns every objection the panel found into
  something the offer answers, stacks honest bonuses and a guarantee the
  numbers can afford, gives it a name, scores it on outcome, likelihood, time
  and effort, then reads the panel's four price answers into an acceptable
  range and sets the price against competitors, margin and that range. Use
  when the user says "make my offer better", "why won't people buy", "what
  should I include", "guarantee", "bonuses", "what should I charge", "pricing",
  or after the panel shows people passing.
argument-hint: "[what the business sells]"
---

# pmf-offer

Most businesses sell a product. Good ones sell an offer: the product plus
everything that makes buying it an easy yes. This skill builds the offer, then
prices it with the panel's own price answers instead of a guess.

## Step 1: read what is known

- `pmf/panel/results.md` and `results.json`: why buyers pass, in their words,
  and the four price medians. Every top objection must be answered by
  something in the offer.
- `pmf/research/voice.md` and `competitors.csv`: the buyer's real vocabulary
  and the competitor price range, for the price step.
- `pmf/numbers.json`: what each extra costs, so the stack stays profitable.
- `pmf/pressure.md`: the conditions checklist.

If the panel has not run, say so and offer a quick one first; if the numbers
do not exist yet, build the offer, then run `pmf-numbers` right after with the
new price.

## Step 2: the problem list

List every problem the buyer hits on the way to the result, from their trigger
to their tenth purchase: what stops them starting, what slows them down, what
they fear after paying. Source: the panel's reasons and flips, the research
complaints, the user's own answers. Keep the buyer's words.

## Step 3: the stack

For each problem, the cheapest thing that removes it:

- **Core**: what is sold, described as the outcome, not the features.
- **Bonuses**: only what is valuable to the buyer and cheap to deliver.
  Anything expensive to deliver is a margin leak; check `numbers.json`.
- **Guarantee**: the strongest promise the numbers can afford. A refund is
  not free: you keep the price but can lose the delivery cost you cannot
  recover, payment fees, and any replacement you ship. Estimate the refund
  rate and the unrecoverable cost per refund before promising, and put both
  in `pmf/numbers.json` when they are material; a guarantee that kills the
  business when 20% claim it is not a guarantee, it is a gamble.
- **Urgency**: real and dated (a launch price with an end date, limited
  capacity that truly is limited). Never a fake countdown; it destroys trust
  faster than no urgency at all.
- **Name**: an offer name a buyer can repeat from memory.

## Step 4: score it

Rate, 1 to 10 each, and write the sentence behind every number:

| dimension | question |
| --- | --- |
| Outcome | does the buyer clearly get what they wanted? |
| Likelihood | do they believe it will work for them? |
| Time | how soon do they see the result? |
| Effort | how little do they have to do? |

A weak score on any dimension points back to a specific part of the stack.

## Step 5: the price

Run the price analysis from this skill's folder (below, VW means running
`van_westendorp.py` from here):

```bash
python3 <this skill's folder>/van_westendorp.py --panel pmf/panel --price <current price>
```

A real survey CSV works the same way with `--csv`. Read out: the acceptable
range (marginal cheapness to marginal expensiveness), the optimal and
indifference points. Then set the price with all three inputs:

1. **The range**: inside it. Below it reads as too cheap to trust; above it
   reads as too expensive.
2. **The competitors** (`pmf/research/market.md`): the price has to make sense
   next to the comparable item, and the gap has to justify any premium.
3. **The margin floor** (`pmf/numbers.json`): the contribution must cover
   break-even at a volume the business can reach. If the panel loves 3.50 and
   the floor is 3.80, say exactly that and pick 3.80 with the smallest
   possible sweetener, or shrink the cost, or walk away from the price point.

If the three disagree, present the conflict and the chosen resolution to the
user; never quietly average them.

## Step 6: re-test when it changed

If the offer or price changed materially, update `pmf/pitch.md` and re-deal
the panel against the SAME buyers, so the audience does not move with the
offer. Use the panel tool in the `pmf-panel` skill's folder:

```bash
python3 <the pmf-panel skill's folder>/panel.py init --reuse pmf/panel --pitch pmf/pitch.md
```

Then run the buyers, `check`, `tally`, and report before and after from the
runs table in `pmf/panel/results.md`. A fresh seed or a new roster is only
for a genuinely new audience. This is optional for cosmetic changes and
required for a changed price or guarantee. Say plainly that a re-dealt panel
is still simulated; the real read comes from `pmf-test`.

## Output

`pmf/offer.md`: the problem list, the stack, the scores with their sentences,
the price decision with all three inputs, the re-test result if any. Record
the fingerprints with the status tool in the `pmf` skill's folder:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact offer.md --input panel/results.json --skill pmf-offer
```

Add `--input research/market.md` when that file exists. Do not list
`numbers.json` here: the price dependency runs the other way (numbers.json
records offer.md), and two files listing each other would make every rerun
look stale forever.

Next: run the `pmf-numbers` skill with the final price, then `pmf-test` to
buy real evidence before `pmf-build`.
