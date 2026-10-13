---
name: pmf-plan
description: >-
  Compiles everything the pack wrote into one business plan with a verdict
  that is computed, never written: Profitable, Not yet (with the failing
  numbers) or Incomplete (with what is missing and which skill fills it), plus
  a half-page summary for a partner, lender or investor. Use when the user
  says "write my business plan", "put it all together", "is it profitable",
  "give me the plan", or at the end of the pmf pack.
argument-hint: "[--min-buy-rate 0.25]"
---

# pmf-plan

Turn the recorded evidence into a plan the owner can use. The compiler
calculates the verdict; the written summary explains the remaining decisions.

Tool in this skill's folder:

```bash
python3 <this skill's folder>/compile.py --dir pmf
```

## Step 1: see what is there

```bash
python3 <this skill's folder>/compile.py --dir pmf --check
```

prints the verdict, each computed check and the missing artifacts. The
checks, all computed from `pmf/numbers.json` and `pmf/panel/results.json`:

1. Each unit earns money before fixed costs.
2. Year 1 makes an operating profit.
3. The break-even fits inside capacity, when a capacity was given.
4. Enough simulated buyers buy (default bar 25%; change with `--min-buy-rate`
   and say why).

If an artifact is missing, name it and the skill that fills it. Never fill a
missing section from guesses, and never argue with a failing check: fix the
input or report the failure.

## Step 2: the summary

Write `pmf/summary.md`, half a page, plain words:

- Describe the proposed business and its first buyer in two sentences.
- The verdict and the three numbers behind it (contribution, break-even,
  year 1).
- Where the evidence agrees and disagrees: the research gap, the panel's buy
  rate and top objections, the pressure test's conditions, and any conflict
  between them (a real signal, not a problem to hide).
- The three next actions, in order, each pointing at a skill or a real-world
  step (usually the launch test).

## Step 3: the plan document

`compile.py` writes `pmf/plan.md` itself: the verdict, the checks table, the
key numbers and the artifact index. Do not edit it by hand; when any input
changes, rerun the tool. Present the plan and the summary to the user in the
same message, verdict first.

## Output

`pmf/plan.md` and `pmf/summary.md`.

That completes the pack. From here the loop is real: the launch test's results
replace the panel's, the numbers get real quotes, and any artifact can be
rerun with better inputs.

Next: run `pmf-launch` to collect real demand evidence, then refresh the
affected stages and compile again.
