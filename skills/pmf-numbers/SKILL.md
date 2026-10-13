---
name: pmf-numbers
description: >-
  The unit economics. What one sale leaves after its own costs, the break-even
  in units a day, the real margin at the planned volume, year 1 month by
  month, the cash needed before the business pays for itself, the payback
  month, and what happens if the price drops, volume comes in low or costs
  rise. Every number traces to an input the user can check. Use when the user
  says "find the profit margins", "do the numbers", "is this profitable",
  "break-even", "unit economics", "how much do I need to start", or "run the
  CFO".
argument-hint: "[path to numbers.json]"
---

# pmf-numbers

Margins decide whether a good idea is a business. The tool in this skill's
folder does the arithmetic; you gather honest inputs and read the result back.

```bash
python3 <this skill's folder>/unit_economics.py pmf/numbers.json --out pmf/numbers.md
```

## Step 1: gather the inputs

Write `pmf/numbers.json` (a filled example sits next to this file as
`example.json`). Required fields:

| field | what goes in it |
| --- | --- |
| `unit` | what one sale is: a drink, an order, a client-month, a seat |
| `price` | price per unit before tax, from `pmf/offer.md` |
| `variable` | the cost of ONE unit: materials, packaging, shipping, card fees, per-sale commissions |
| `fixed_monthly` | what you pay every month regardless: rent, salaries, software, insurance |
| `startup` | one-off spend before opening: deposits, build-out, equipment, first stock, launch ads |
| `plan_per_day` | volume a day once it is running |
| `ramp_per_day` | 12 numbers: realistic volume a day in each month of year 1 |
| `capacity_per_day` | optional: the most you can physically sell in a day |

Prefer evidence that matches the planned business:

1. Actual invoices, lease terms or supplier quotes provided by the user.
2. Prices the user can check today (a supplier's public list, a landlord's
   listing, a competitor's menu).
3. A range the user agrees with, clearly marked as an estimate.

Never invent a cost. If the user does not know, list the number as an open
question and use the most defensible placeholder, marked. A missing field is
an error; the tool will refuse it, and so should you.

## Step 2: run and read

Run the tool, then report the five load-bearing numbers back in plain words:
contribution per unit, break-even units a day, margin at plan, year 1
operating profit, cash needed and payback month. Check them against reality:

- **Break-even against capacity**: if it does not fit, the plan cannot work
  at this price and cost. Say it before anything else.
- **Margin at plan**: thin margins (under about 20%) survive only with
  near-perfect volume; say so.
- **Cash needed**: this is the real ask. Compare it to the user's budget in
  `pmf/idea.md`; if it exceeds it, the plan needs a smaller start.
- **The what-ifs**: price 10% lower, volume 20% lower, cost 10% higher. The
  business is only real if it survives some of them. Name which one hurts most.

## Step 3: close the loop

If the numbers force a change (a higher price, a smaller start, a cheaper
supplier), send the change back: update `pmf/offer.md`'s price with the user,
and update `pmf/ops.md` costs once `pmf-ops` has run. Rerun the tool after any
input change; never edit `pmf/numbers.md` by hand.

## Output

`pmf/numbers.json` and `pmf/numbers.md` (the tool writes the report; you write
nothing into it by hand).

Next: run the `pmf-build` skill, then `pmf-marketing`.
