---
name: pmf-launch
description: >-
  The launch. Starts with the cheapest real-world test that proves or kills
  the panel's verdict with real buyers (a pre-sale, a waitlist with a deposit,
  a pop-up, a pilot), success criteria set before the test runs, then a dated
  countdown to opening day, the run sheet, and the first 30 days of what to
  measure and what to change. Use when the user says "how do I launch",
  "launch plan", "when can I open", "launch checklist", "go live", or "soft
  open".
argument-hint: "[target launch date, if the user has one]"
---

# pmf-launch

Launching is a project with a date. This turns the whole pack into one, and
it starts by finding out whether real people pay, cheaply, before the big
costs start.

## Step 1: the real test

Pick the cheapest test that fits the business and would genuinely change
decisions; the panel's verdict is an upper bound, this is the verdict:

| business | the test |
| --- | --- |
| Physical, walk-in | a pop-up or market stall for 2 to 4 days with real prices |
| Product to pre-order | a pre-sale page with a refundable deposit |
| Service | three paid pilots at a reduced but real price |
| Software or content | a waitlist that collects an email, then a paid founding offer |

Set the success criteria BEFORE running it (the numbers that mean go, the
numbers that mean change, the numbers that mean stop), tied to the checks in
`pmf/numbers.json` (does the test cover break-even's daily units? does it
confirm the price?). Record actual results against the panel's predictions in
`pmf/launch.md`; when they disagree, real beats simulated, always.

## Step 2: the countdown

A dated table from today to opening day: every milestone with an owner and a
date (permits confirmed, suppliers quoted, build done, brand ready, ads
scheduled), working backwards from the target date. Use the start of
`ramp_per_day` in `pmf/numbers.json` as the opening volume; if the countdown
cannot reach the plan's first month, say so and adjust the plan instead of
the optimism.

## Step 3: the run sheet

Opening day, hour by hour (or step by step online): who is where, what is
tested before the first customer (payments end to end, the queue, the
printing, the wifi), the first-hour checklist, and the person empowered to
change something on the spot. Online: deploy, test the money path twice, post
the first hook, watch for one hour.

## Step 4: the first 30 days

- The three numbers from `pmf/marketing.md` measured weekly, honestly,
  including the weeks they are ugly.
- A weekly 30-minute review: what moved, what is stuck, the one change for
  next week (price, channel, offer, or nothing).
- The first decision gate: if the buy rate from the real test holds after 30
  days, scale the working channel; if not, change one thing at a time; if two
  changes already failed, revisit `pmf-offer.md` with the new evidence.

## Output

`pmf/launch.md`: the chosen test with its criteria and results, the countdown
table, the run sheet, the 30-day rhythm.

Next: run the `pmf-plan` skill to compile everything.
