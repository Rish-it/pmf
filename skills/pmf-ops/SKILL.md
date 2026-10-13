---
name: pmf-ops
description: >-
  Operations on day one: the daily cycle step by step, the suppliers to line
  up and the exact questions to ask them, the minimum staffing and when the
  first hire triggers, the tools worth paying for, the licences and permits
  to confirm (never asserted, always with where to check), and a risk
  register. Feeds real costs back into the numbers. Use when the user says
  "how do I run this", "operations", "suppliers", "staffing", "SOPs", "what
  do I need to open", "permits", or "day one".
argument-hint: "[city or country]"
---

# pmf-ops

A plan that works on paper fails at 7am on a Monday. This makes the first
day, week and month runnable, and pushes the real costs back into the numbers.

## Step 1: the daily cycle

From `pmf/idea.md`, `pmf/offer.md` and `pmf/numbers.json`, write the day as a
list of steps from first thing to last (for a cart: prep, load, travel, set
up, serve, pack down, cash up, restock, clean). Mark which steps the customer
sees; those are where the brand's promise is kept or broken. For each step:
who does it, how long it takes, and which tool or supplier sits behind it.

## Step 2: suppliers and sourcing

For every input in `variable` and every fixed cost that needs a vendor: what
to source, 2 to 3 candidate sources found the same way `pmf-research` finds
things, and the exact questions to ask for a quote (unit price at what volume,
delivery cost and time, minimum order, payment terms, what happens on a bad
batch). Put the quote questions in a checklist the user can paste into an
email. Quotes replace estimates in `pmf/numbers.json`; rerun the numbers tool
after.

## Step 3: people

The minimum who and when: the founder's own hours per week by step, then each
role in the order it is needed, with the trigger that starts it ("a second
person when the queue at 8am loses regulars", "an accountant when the first
payroll month lands"). No org charts; triggers.

## Step 4: tools

Only what day one needs, each with a one-line reason and a monthly cost that
is already in `fixed_monthly`: payments, booking or ordering, accounting,
one place the customer list lives. Anything a spreadsheet genuinely covers,
the spreadsheet covers.

## Step 5: licences and permits

A checklist of what this business type usually needs where the user is
(business registration, food handling, signage, insurance, tax registration),
each with **where to confirm it**: the specific authority or a professional.
Never assert that a licence is or is not required; say what to check and with
whom. Costs of these go into `startup` in the numbers.

## Step 6: the risk register

The top 5 things that could stop the business in year 1 (a supplier failing, a
permit denied, the one person getting sick, a competitor copying, a platform
changing terms), each with the trigger that means it is happening, the
mitigation decided in advance, and who watches it. Real risks only; "the
economy" is not a register entry.

## Output

`pmf/ops.md`. If any cost changed from an estimate to a quote, update
`pmf/numbers.json` and rerun `pmf-numbers` before finishing.

Next: run the `pmf-launch` skill.
