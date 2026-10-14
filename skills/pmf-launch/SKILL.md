---
name: pmf-launch
description: >-
  The launch, after the real test has passed. Confirms the evidence gate,
  then builds the dated countdown to opening day (permits, suppliers, build,
  brand, ads, working backwards from the date), the hour-by-hour run sheet
  for opening day, and the first 30 days of what to measure, including
  repeat purchase by cohort. Use when the user says "how do I launch",
  "launch plan", "when can I open", "launch checklist", "go live", or "soft
  open" after the demand test.
argument-hint: "[target launch date, if the user has one]"
---

# pmf-launch

Launching is a project with a date, and it starts from evidence, not hope.
The demand test lives in `pmf-test`; this skill spends real money only after
it passed.

## Step 1: confirm the gate

Read `pmf/test.md` and `pmf/experiments.json`. Recompute the outcome with
the experiments tool in the `pmf-test` skill's folder if you want the raw
read (`check --dir pmf`). The latest real test must have passed its pre-set
criteria.

- **Passed**: proceed, and quote the test's numbers in `pmf/launch.md` as
  the last evidence before spend.
- **Mixed, failed, or no test at all**: say it plainly and stop. Launching
  anyway is the user's call, but it must be written down as an explicit
  decision in `pmf/launch.md` ("launching without a passed test, because
  ..."), and the compiled verdict stays Projected or Not yet. Never
  silently treat the panel as if it were real evidence.

## Step 2: the countdown

A dated table from today to opening day: every milestone with an owner and a
date (permits confirmed, suppliers quoted, build done, brand ready, ads
scheduled), working backwards from the target date. Use the start of
`ramp_per_day` in `pmf/numbers.json` as the opening volume; if the countdown
cannot reach the plan's first month, say so and adjust the plan instead of
the optimism. The first real test's logistics that repeat at launch (the
pre-sale page, the booking flow) are already built; reuse them.

## Step 3: the run sheet

Opening day, hour by hour (or step by step online): who is where, what is
tested before the first customer (payments end to end, the queue, the
printing, the wifi), the first-hour checklist, and the person empowered to
change something on the spot. Online: deploy, test the money path twice, post
the first hook, watch for one hour.

## Step 4: the first 30 days

- The three numbers from `pmf/marketing.md` measured weekly, honestly,
  including the weeks they are ugly.
- **Repeat purchase by cohort**: a table in `pmf/launch.md` with one row per
  week's cohort (buyers that week, how many bought again in the following
  weeks, repeat rate). A first purchase is interest; a repeat is a market.
- A weekly 30-minute review: what moved, what is stuck, the one change for
  next week (price, channel, offer, or nothing).
- The first decision gate: if the repeat rate and the three numbers hold
  after 30 days, scale the working channel; if not, change one thing at a
  time; if two changes already failed, revisit `pmf-offer.md` with the new
  evidence.
- Turn the cohort table into a logged test: run `pmf-test` and add a
  `retention` entry (cohort size, repeat buyers, a `min_repeat_rate`
  criterion) so the next `pmf-plan` reads retention as real evidence, not a
  chart.

## Output

`pmf/launch.md`: the gate result, the countdown table, the run sheet, the
30-day rhythm, the cohort table. Record the fingerprint with the status tool
in the `pmf` skill's folder:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact launch.md --input experiments.json --input numbers.json --skill pmf-launch
```

Next: run the `pmf-plan` skill to compile everything with the first real
numbers in place.
