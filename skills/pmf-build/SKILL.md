---
name: pmf-build
description: >-
  Builds the smallest real thing the plan needs, with agentic coding
  discipline: understand first, then the reuse ladder (does it need to exist,
  is it already here, standard library, native feature, installed
  dependency, one line, only then the minimum), one runnable check for every
  non-trivial piece, two clean verification runs, task-only diff, root-cause
  fixes, no AI attribution in commits. Ships a waitlist page, a booking flow,
  the core product slice or the pre-day-one checklist for a physical
  business, and records what was deliberately skipped. Use when the user says
  "build the MVP", "make the landing page", "build the app", "ship it",
  "start building", or after the numbers work.
argument-hint: "[what to build, if the user named it]"
---

# pmf-build

Build the first useful version within the plan's budget. Keep the scope
small, reuse what the project already has, and verify the user can finish
the core action before handing it over.

## Step 0: read, then propose

Read `pmf/offer.md` (what is sold), `pmf/numbers.json` (what the build may
cost), `pmf/test.md` and `pmf/experiments.json` (did real buyers pay?),
`pmf/research/market.md` (why this is different), `pmf/panel/results.md`
(what the first users will care about). If offer or numbers are missing, say
so and stop; building before those is spending before thinking.

Build only on evidence: `compile.py --check` in the `pmf-plan` skill's
folder must say Validated (the latest demand test passed its locked
criteria at the plan price). If it failed or has not run, say so and recommend
`pmf-test` instead. If the user chooses to build anyway, record that decision
in `pmf/build.md` in one line ("building without a passed test, because ...");
the compiled verdict will not count it as validated.

Propose 2 or 3 slices, smallest first, for example:

1. A one-page site with a waitlist and the offer's promise.
2. The single most valuable user action end to end (booking, ordering, the
   first report), ugly but real.
3. Payments or accounts, only once someone real has used 2.

Write the chosen scope to `pmf/build.md` BEFORE writing any product code:
what is in, what is deliberately out and when it would come back, and the
definition of done in one line (the thing a user can do when this is
finished).

## Step 1: build

Work in the user's project, never inside `pmf/`. The rules, in order:

- **Understand first.** Read the project's own instructions and conventions,
  find where the change belongs, trace the flow it touches end to end. The
  ladder shortens the solution, never the reading.
- **The ladder.** Does this need to exist? Is it already in this codebase?
  Does the standard library do it? A native platform feature? An installed
  dependency? One line? Only then: the minimum code that works.
- **No unrequested anything**: no abstraction with one user, no config for a
  constant, no dependency that a few lines replace, no scaffolding for later.
  Deletion over addition. Boring over clever. Fewest files.
- **House rules**: a task branch, a task-only diff (no reformatting the
  neighborhood), the repo's existing patterns and test setup, selective
  staging, commits only when the user asks.
- **Bugs are root-cause fixes**: grep every caller, fix the shared place once.
- **Mark deliberate simplifications** with a `pmf:` comment naming the
  ceiling and the upgrade trigger (for example `# pmf: single-process
  queue; move to a real queue past 100 jobs/day`).
- **Never cut**: validation at trust boundaries, error handling that prevents
  data loss, security, accessibility basics, anything the user explicitly
  asked for.
- **One runnable check** for every non-trivial piece (a branch, a loop, a
  parser, a money path): the smallest thing that fails if the logic breaks,
  reusing the project's test setup when it has one.

## Step 2: verify twice

Run the strongest relevant check in two separate clean runs (tests, build,
typecheck, or the actual flow by hand) and report both results. Fix and rerun
both after any change; a passing run before a fix proves nothing about after.
If something is flaky, investigate instead of rerunning until green.

## Step 3: handoff

Update `pmf/build.md`: what shipped, how to run it, the two verification
runs, the skipped list with its upgrade triggers, and the next slice. Point at
deployment options if the plan needs the thing public, and let the user decide
before any spend. Commits and code contain no AI, model or tool attribution.

For a physical or offline business, there is no code: produce `pmf/build.md`
as the pre-day-one checklist (fit-out, equipment, first stock, permits from
`pmf-ops`), same standard of smallest-that-works.

## Output

`pmf/build.md`. Record the fingerprint with the status tool in the `pmf`
skill's folder:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact build.md --input offer.md --input numbers.json --skill pmf-build
```

Next: run the `pmf-marketing` skill.
