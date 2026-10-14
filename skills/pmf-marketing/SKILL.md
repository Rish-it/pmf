---
name: pmf-marketing
description: >-
  The product-market fit plan itself. Turns the panel and the research into
  positioning, the channels the target buyer actually uses, a dated 30-day
  launch campaign, ten hooks written in the buyers' own words, a budget split,
  the most you can pay to win a customer, and the three numbers to watch.
  Every message answers an objection real or simulated buyers raised. Use when
  the user says "how do I market this", "marketing plan", "launch campaign",
  "how do I get customers", "where do I advertise", "write my ads", or
  "positioning".
argument-hint: "[monthly budget]"
---

# pmf-marketing

A business no one hears about does not exist. This plans how the first
customers hear about it, from evidence the pack already gathered, never from
a generic playbook.

## Step 1: read the evidence

- `pmf/panel/results.md`: the segments with the highest buy rate are the
  first audience; the top objections are what every message must answer.
- `pmf/research/`: where buyers hang out (Step 5) is the channel list, the
  voice bank is the copywriter, competitor positioning is what to sound
  nothing like.
- `pmf/offer.md` and `pmf/numbers.json`: what is sold, at what price, what a
  customer is worth, which caps what a customer may cost.

If any of these is missing, name it and offer the quick version of that step
first. Do not invent an audience.

## Step 2: positioning

State the buyer, outcome and reason to choose this offer in one sentence:

```
<Business> helps <first buyer> achieve <desired outcome> through
<evidence-backed difference from their current solution>.
```

Every blank comes from a file above. Test the line: a stranger should be able
to say it back after hearing it once.

## Step 3: channels, from evidence

List only channels that appeared in `pmf/research/` where buyers actually
are, each with what the evidence was. Pick 2 or 3 primary channels plus 1
experiment, and for each: the format (a post, a flyer, a local partnership), a
monthly budget, and why it fits the buying behaviour (the trigger from
`voice.md`). A channel with no evidence line gets dropped, however familiar it
feels.

## Step 4: the 30-day campaign

A dated table: day, channel, action, asset needed, owner, budget. At least
one touch per week per primary channel, and an asset checklist (page, photos,
offer copy, the hooks below) with owners. The campaign points at one action
per asset (join the waitlist, pre-order, come on opening day); two calls to
action is one too many.

## Step 5: ten hooks

Ten first lines in the buyers' own vocabulary, from `pmf/research/voice.md`:
each answers one objection or presses one desire, in under twelve words. Mark
which objection each hook answers; a hook that answers none is a slogan.

## Step 6: the money

- **Budget split**: channel by channel, from the user's monthly number (ask
  if unknown; never invent it).
- **Most a customer may cost**: the contribution from `pmf/numbers.md` for
  what one customer buys in a defensible window (one purchase, or the first
  month of a subscription). If contribution is 2.90 and a click costs 1.50
  with a 2% signup rate, the maths is already telling you something; write it
  out plainly.
- **The three numbers to watch**: cost per signup (or per visit), the percent
  that become buyers, and the repeat rate. One line each on what a bad week
  looks like and what you would change.

## Output

`pmf/marketing.md`: positioning, evidence-backed channels, the dated 30-day
plan, ten hooks with their objections, the budget and the CAC cap, the three
numbers. Record the fingerprints with the status tool in the `pmf` skill's
folder:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact marketing.md --input panel/results.json --input offer.md --skill pmf-marketing
```

Add `--input research/market.md` and `--input research/voice.md` when those
files exist; the channels and the hooks come from them.

Next: run the `pmf-brand` skill with the positioning line.
