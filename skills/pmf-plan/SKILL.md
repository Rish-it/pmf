---
name: pmf-plan
description: >-
  Compiles everything the pack wrote into one decision document with a
  verdict that is computed, never written: Validated (the economics work and
  the latest real-world test met its criteria), Projected (the economics work
  but no real test has a result yet), Not yet (a check fails, with the
  numbers) or Incomplete (numbers.json missing or invalid). Leads with what
  is known, what is uncertain and the cheapest next action, and reads
  freshness from the state ledger. Use when the user says "write my business
  plan", "put it all together", "is it profitable", "give me the plan", or at
  the end of the pmf pack.
argument-hint: "[--min-coverage 0.8]"
---

# pmf-plan

Turn the recorded evidence into a decision the owner can use. The compiler
computes the verdict from real inputs; the written summary explains the
remaining decisions in plain words.

Tool in this skill's folder:

```bash
python3 <this skill's folder>/compile.py --dir pmf
python3 <this skill's folder>/compile.py --dir pmf --check
```

The compiler imports the same calculation engine as `pmf-numbers` and the
same outcome evaluator as `pmf-test`, so the plan cannot disagree with the
stages that produced it.

## Step 1: see what is there

`--check` prints the verdict, every computed check, the demand evidence line
and what blocks a full plan, and writes nothing. The verdicts and what
computes them:

- **Incomplete**: `numbers.json` is missing or invalid, or
  `experiments.json` is malformed, or a test has results without a lock or
  with criteria moved after the lock. The blockers are listed.
- **Not yet**: the economics fail a check (contribution, year 1 operating,
  break-even against capacity), the latest demand test or the latest
  retention test did not meet its criteria, or the demand test charged more
  than 10% under the plan price. A failed real test beats profitable projections, always; that is
  the point of the gate.
- **Projected**: the economics work; no real test has a result yet (planned
  tests and the simulated panel are context, not evidence).
- **Validated**: the economics work, the latest demand test met every
  criterion locked before it ran at the plan's price, and no later retention
  test failed. A retention pass alone never validates.

The simulated panel never gates the verdict: a simulated buy rate is not a
conversion forecast. Coverage below the bar (default 80%, `--min-coverage`)
is called noise in the report.

Exit code: 0 for Validated and Projected, 1 otherwise.

## Step 2: the plan document

`compile.py` writes `pmf/plan.md` itself. It contains, in order: the verdict
with projected economics, demand evidence and readiness; the checks table
(economics plus the latest test's criteria); the demand evidence table (every
logged test, planned or done); key numbers including cash needed and payback;
what remains uncertain (unrun tests, missed criteria, cost lines without a
source, open pressure-test conditions, and any recorded file whose inputs
changed); the cheapest next action; the conditions from the pressure test;
and the artifact index with each file's freshness.

Do not edit it by hand; when any input changes, rerun the tool. If the
freshness column shows STALE, the named stages must rerun first; a plan built
on stale inputs is not a plan.

## Step 3: the summary

Write `pmf/summary.md`, half a page, plain words, in this order:

1. **What we know**: the business in two sentences, the verdict, and the
   evidence behind it (the test ids and outcomes, the three load-bearing
   numbers).
2. **What remains uncertain**: the honest list, led by whatever would change
   the decision first (an unrun test, a missed criterion, an unsourced cost,
   a thin margin).
3. **The next cheapest action**, in one sentence, with the skill or real-world
   step that does it.

Then present the plan and the summary to the user in the same message,
verdict first. Never argue with a failing check; fix the input or report the
failure.

## Output

`pmf/plan.md` and `pmf/summary.md`. Record the fingerprints with the status
tool in the `pmf` skill's folder:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact plan.md --input numbers.json --input experiments.json --skill pmf-plan
```

That completes the pack. From here the loop is real: the next test's results
replace the panel's guesses, the numbers get real quotes, and any artifact
can be rerun with better inputs and recompiled.

Next: run `pmf-test` for the next real test (or `pmf-launch` once a test has
passed), then refresh the affected stages and compile again.
