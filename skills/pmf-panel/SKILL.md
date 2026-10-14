---
name: pmf-panel
description: >-
  The consumer panel. Builds the target customer, then runs the pitch past a
  simulated panel of buyer agents (30 by default, scale up for a final read),
  each with its own income, habits, behaviour and doubt, and tallies who
  buys, who passes, why, what would flip a no, and at which prices the
  product feels too cheap, fair, expensive and absurd. The segment and
  behaviour mix matches the customer profile exactly; before-and-after
  comparisons reuse the same buyers. Objections are grounded in real research
  when pmf/research exists. Use when the user says "would people buy this",
  "test it on customers", "run the consumer panel", "simulate buyers", "who is
  my customer", or "validate demand".
argument-hint: "[--n 30 | --n 100] [--seed S] [--reuse pmf/panel]"
---

# pmf-panel

Instead of guessing whether people will buy, ask a panel of buyer agents,
each one a separate agent playing a specific buyer drawn from the target
customer. You are the moderator. You never answer for a buyer.

The tool in this skill's folder does all the bookkeeping (below, PANEL means
running `panel.py` from this skill's folder):

```bash
python3 <this skill's folder>/panel.py <command> ...
```

State lives in `pmf/panel/`. The tool deals cards, checks answers, and tallies
them; it never writes an answer.

The buy rate is an upper bound, not a forecast: language models lean
agreeable, and a simulated purchase rate has no known mapping to real
conversion. The panel's job is to find the objections and the wording before
real money is spent; `pmf-test` is where real evidence comes from.

## Step 1: the target customer

Write `pmf/customer.json`. Shape (a filled example sits next to this file as
`customer.example.json`):

- `business`, `target`: the business and who the buyer is, in one line each.
- `segments`: 2 to 4 groups, each with `name`, `share` (a weight above zero)
  and `income` as `[low, high]` yearly numbers.
- `behaviours`: 4 to 8 buying behaviours, each with `name`, `share` and a
  `how` line (daily regular, deal hunter, reads every review, loyal to a
  competitor...).
- `objections`: the 4 to 8 doubts this buyer really carries.
- `habits` (optional): everyday context lines that make a buyer concrete.

Ground it in real material: the user's own customer knowledge, and if
`pmf/research/` exists, the complaints and the voice bank there. If real
customer data exists (interviews, reviews, survey answers), prefer it and say
which parts are guesses. Show the user the profile in a few lines and let them
correct it before dealing: a wrong customer makes the whole panel wrong.

## Step 2: the pitch

Write `pmf/pitch.md`: what a buyer would actually see. Product, price, where
and how to get it, any opening offer. Three to six plain lines, no
superlatives, nothing the business cannot deliver. Every buyer sees exactly
this, and it is embedded in every card.

## Step 3: deal the cards

```bash
python3 <this skill's folder>/panel.py init --customer pmf/customer.json --pitch pmf/pitch.md
```

- The default is 30 buyers: small enough to run while the offer is still
  moving. Scale to 100 only for the final read, when the pitch is stable.
- `--seed` makes a rerun identical; the segment and behaviour counts always
  match the profile exactly (largest-remainder quotas), so the composition
  cannot drift between runs.
- For a before-and-after comparison (a changed price, offer or guarantee),
  re-deal with the same buyers instead of a new audience:

  ```bash
  python3 <this skill's folder>/panel.py init --reuse pmf/panel --pitch pmf/pitch.md
  ```

  The previous run's cards, answers, manifest and results are kept in
  `pmf/panel/runs/`, so the two rounds can be compared directly.

Before dealing, say how many buyer agents the run is.

## Step 4: run the buyers

Each card in `pmf/panel/cards/` is one buyer. For every card, have one buyer
agent read the card and write `pmf/panel/answers/<id>.json` in exactly the
shape the card shows. It must judge as its buyer and answer in its own words.

- If you can spawn sub-agents (Claude Code: the Agent tool; Codex and OpenCode:
  their own sub-agent tools), run one buyer per sub-agent, in waves (e.g. 15 at
  a time) so a failure does not lose the run.
- If you cannot, process the cards in batches of 10 to 20 in your own context,
  writing one answer file per buyer, and say in the results that it was a
  batched run.
- Never answer for a buyer, never fix a buyer's answer, never skip a doubt
  that makes the result uglier.

## Step 5: check and tally

```bash
python3 <this skill's folder>/panel.py check
python3 <this skill's folder>/panel.py tally
```

`check` is strict on purpose: it rejects a text `"false"` for `buys`, price
answers that do not climb in order (too cheap <= good deal <= getting
expensive <= too expensive), a wrong buyer id, unknown keys and missing
fields. On a problem, rerun that buyer (delete the file and run the card
again) or say plainly that the run is short; never edit an answer by hand.

`tally` writes `pmf/panel/results.json` and `pmf/panel/results.md`: buy rate
over the valid answers, coverage, by segment and by behaviour, the four price
medians, the reasons in the buyers' own words, and a runs table when there is
history.

## Step 6: report

Read the results and tell the user, briefly: the buy rate as an upper bound,
its coverage, the segments that buy, and the top objections in the buyers'
words. Then do the moderator's job: cluster the reasons into three to five
named objections, rank them, and name the single objection the next test
should probe or the offer should answer first. That ranked list feeds
`pmf-offer`, and the price answers feed its price range step.

## Integrity

The panel is simulated buyers, not customers. It finds objections, segments
and wording cheaply before real money is spent; it is not a forecast, and its
quotes are research, never testimonials. Real-world tests (see `pmf-test`)
override everything the panel said, always.

## Output

`pmf/customer.json`, `pmf/pitch.md`, `pmf/panel/`. Record the fingerprints
with the status tool in the `pmf` skill's folder:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact panel/results.json --input pitch.md --input customer.json --skill pmf-panel
```

Next: run the `pmf-offer` skill with the top objections and the price answers.
