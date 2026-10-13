---
name: pmf-panel
description: >-
  The consumer panel. Builds the target customer, then runs the pitch past a
  simulated panel of buyer agents (100 by default, 20 with --quick), each with
  its own income, habits, behaviour and doubt, and tallies who buys, who
  passes, why, what would flip a no, and at which prices the product feels too
  cheap, fair, expensive and absurd. Objections are grounded in real research
  when pmf/research exists. Use when the user says "would people buy this",
  "test it on customers", "run the consumer panel", "simulate buyers", "who is
  my customer", or "validate demand".
argument-hint: "[--n 100 | --quick] [--seed S]"
---

# pmf-panel

Instead of guessing whether people will buy, ask a hundred of them, each one a
separate agent playing a specific buyer drawn from the target customer. You
are the moderator. You never answer for a buyer.

The tool in this skill's folder does all the bookkeeping (below, PANEL means
running `panel.py` from this skill's folder):

```bash
python3 <this skill's folder>/panel.py <command> ...
```

State lives in `pmf/panel/`. The tool deals cards, checks answers, and tallies
them; it never writes an answer.

## Step 1: the target customer

Write `pmf/customer.json`. Shape (a filled example sits next to this file as
`customer.example.json`):

- `business`, `target`: the business and who the buyer is, in one line each.
- `segments`: 2 to 4 groups, each with `name`, `share` (relative weight) and
  `income` as `[low, high]` yearly numbers.
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

Use `--n 100` for a full run, `--n 20` for a quick pass (say `--quick` to the
user context), `--seed` to make a rerun identical. Before a 100-buyer run,
tell the user it is 100 buyer agents and suggest 20 first if the pitch may
still change.

## Step 4: run the buyers

Each card in `pmf/panel/cards/` is one buyer. For every card, have one buyer
agent read the card and write `pmf/panel/answers/<id>.json` in exactly the
shape the card shows. It must judge as its buyer and answer in its own words.

- If you can spawn sub-agents (Claude Code: the Agent tool; Codex and OpenCode:
  their own sub-agent tools), run one buyer per sub-agent, in waves (e.g. 25 at
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

`check` reports missing or malformed answers; fix those (rerun the buyer or
say the run is short) before tallying. `tally` writes `pmf/panel/results.json`
and `pmf/panel/results.md`: buy rate overall, by segment and by behaviour,
the four price medians, and the reasons in the buyers' own words.

## Step 6: report

Read the results and tell the user, briefly: the buy rate (and that language
models lean agreeable, so read it as an upper bound), the segments that buy,
the top objections in the buyers' words, and what would flip a no. Those
objections are the input for `pmf-offer`, and the price answers are the input
for `pmf-offer`'s price range step.

## Integrity

The panel is simulated buyers, not customers. It finds objections, segments
and wording cheaply before real money is spent; it is not a forecast, and its
quotes are research, never testimonials. Real-world tests (see `pmf-launch`)
override everything the panel said, always.

Next: run the `pmf-offer` skill with the top objections and the price answers.
