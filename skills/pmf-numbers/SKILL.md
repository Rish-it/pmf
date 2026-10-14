---
name: pmf-numbers
description: >-
  The unit economics. What one sale leaves after its own costs, the break-even
  in units a day, the real margin at the planned volume, year 1 month by
  month, the cash needed before the business pays for itself (including the
  startup spend), the payback month, red flags, and what-if scenarios
  (price, volume, costs) including custom ones from the file. Costs are
  itemised with an optional source per line; the tool rejects impossible
  volumes and invalid numbers. Use when the user says "find the profit
  margins", "do the numbers", "is this profitable", "break-even", "unit
  economics", "how much do I need to start", or "run the CFO".
argument-hint: "[path to numbers.json]"
---

# pmf-numbers

Margins decide whether a good idea is a business. The tool in this skill's
folder is the one calculation engine: it computes every number, and
`pmf-plan`'s compiler reuses the same engine, so the plan cannot drift from
the inputs.

```bash
python3 <this skill's folder>/unit_economics.py pmf/numbers.json --out pmf/numbers.md
```

## Step 1: gather the inputs

Write `pmf/numbers.json` (a filled example sits next to this file as
`example.json`). The fields:

| field | what goes in it |
| --- | --- |
| `unit` | what one sale is: a drink, an order, a client-month, a seat |
| `price` | price per unit before tax, from `pmf/offer.md` |
| `variable_items` | the cost of ONE unit, itemised: a list of `{name, per_unit, source}` |
| `fixed_items` | costs every month whatever you sell: `{name, per_month, source}` |
| `startup_items` | one-off spend before opening: `{name, amount, source}` |
| `days_per_month` | optional: selling days in a month (default 30) |
| `plan_per_day` | volume a day once it is running |
| `ramp_per_day` | 12 numbers: realistic volume a day in each month of year 1 |
| `capacity_per_day` | optional: the most you can physically sell in a day |
| `scenarios` | optional: named what-ifs, `{name, price?, volume_scale?, variable_scale?, fixed_scale?}` |

`source` is optional on every cost line but valuable: the tool counts lines
without one and calls them assumptions in the compiled plan. The old flat
fields (`variable`, `fixed_monthly`, `startup` as single numbers) still work
when the itemised list is absent; giving both forms at once is an error.

Prefer evidence that matches the planned business:

1. Actual invoices, lease terms or supplier quotes provided by the user.
2. Prices the user can check today (a supplier's public list, a landlord's
   listing, a competitor's menu).
3. A range the user agrees with, clearly marked as an estimate.

Never invent a cost. If the user does not know, list the number as an open
question and use the most defensible placeholder, marked. A missing field is
an error; the tool will refuse it, and so should you. It also refuses
impossible numbers: a plan or a ramp above capacity, negative costs, a price
of zero, or a selling month outside 1 to 31 days.

## Step 2: run and read

Run the tool, then report the load-bearing numbers in plain words:

- contribution per unit,
- break-even units a day,
- margin at plan,
- year 1 operating profit,
- **cash needed**, which now includes the startup spend before month 1. If
  the deepest point is a later month, the tool says which one; that month is
  the real funding ask. Compare it to the user's budget in `pmf/idea.md`.
- payback month.

Check them against reality, in this order:

- **Break-even against capacity**: if it does not fit, the plan cannot work
  at this price and cost. Say it before anything else.
- **Margin at plan**: thin margins (under about 20%) survive only with
  near-perfect volume; say so.
- **The red flags**: the tool lists them; read them out, do not summarize.
- **The what-ifs**: the three standard probes plus any scenario in the file
  (winter volume, a competitor's price cut). Name which one hurts most, and
  whether the business survives it.

For a quick probe without editing the file:

```bash
python3 <this skill's folder>/unit_economics.py pmf/numbers.json --price 3.90 --volume 0.8
```

## Step 3: close the loop

If the numbers force a change (a higher price, a smaller start, a cheaper
supplier), send the change back: update `pmf/offer.md`'s price with the user,
and update `pmf/ops.md` costs once `pmf-ops` has run. Rerun the tool after any
input change; never edit `pmf/numbers.md` by hand.

## Output

`pmf/numbers.json` and `pmf/numbers.md` (the tool writes the report; you write
nothing into it by hand). Record the fingerprints with the status tool in the
`pmf` skill's folder, so a later price or offer change marks the dependent
stages stale:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact numbers.json --input offer.md --skill pmf-numbers
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact numbers.md --input numbers.json --skill pmf-numbers
```

Next: run the `pmf-test` skill to buy the first real evidence, then
`pmf-build`.
