---
name: pmf
description: >-
  The front door to the PMF pack: thirteen product-market fit skills that take
  a business from idea to launch, working in Claude Code, Codex and OpenCode.
  Checks what already exists in the project's pmf/ folder, what has gone
  stale since it was recorded, says what to run next, and routes to the right
  stage skill: pressure test, research, buyer panel, offer and price, unit
  economics, the real-world demand test, MVP build, marketing, brand,
  operations, launch and the compiled plan. Use when the user says "go to
  market", "launch my business", "validate my idea", "is this a good
  business", "run the pmf pack", "pmf", or asks what to do next with a
  business idea.
argument-hint: "[what the user wants to do, or leave blank]"
---

# pmf

The front door. One folder of skills, one state folder (`pmf/` in the user's
project), one path from idea to launch. This skill routes; the stage skills do
the work.

## The path

| step | skill | writes | needs first |
| --- | --- | --- | --- |
| 1 | `pmf-pressure` | `pmf/idea.md`, `pmf/pressure.md` | nothing |
| 2 | `pmf-research` | `pmf/research/` | idea |
| 3 | `pmf-panel` | `pmf/customer.json`, `pmf/pitch.md`, `pmf/panel/` | research (preferred) |
| 4 | `pmf-offer` | `pmf/offer.md` | panel, numbers (costs) |
| 5 | `pmf-numbers` | `pmf/numbers.json`, `pmf/numbers.md` | offer (price) |
| 6 | `pmf-test` | `pmf/experiments.json`, `pmf/test.md` | offer, numbers |
| 7 | `pmf-build` | `pmf/build.md` | a passed test (or a written decision to skip it) |
| 8 | `pmf-marketing` | `pmf/marketing.md` | panel, numbers |
| 9 | `pmf-brand` | `pmf/brand.md` | marketing |
| 10 | `pmf-ops` | `pmf/ops.md` | offer, numbers |
| 11 | `pmf-launch` | `pmf/launch.md` | a passed test, everything above |
| 12 | `pmf-plan` | `pmf/plan.md`, `pmf/summary.md` | numbers, experiments |

Steps 8 to 10 can run in any order once 1 to 7 exist. Any single skill can be
run alone if its inputs exist. Step 6 is the gate: it is the first real
evidence, and it comes before the build and the launch, not after.

## What to do

1. Look at the state. Two commands, in this order:
   - `ls pmf/` for which files exist (never guess);
   - `python3 <this skill's folder>/status.py check --dir pmf` for what has
     gone stale since it was recorded.
2. Tell the user, in a few lines: what is done and fresh, what is stale and
   must be refreshed, what is missing, and the next step with its one-line
   reason. Recommend the earliest stale or missing stage.
3. Stale beats missing: an artifact whose inputs changed (a price, a pitch, a
   customer profile) must be rerun before anything downstream of it counts.
   The `status.py check` output names the stages to rerun.
4. If the user named a stage ("price this", "run the panel"), skip to that
   skill, and say which inputs it expects.
5. When routing to a skill, actually run that skill's workflow. Do not
   summarize the pack instead of doing the work.

## Rules

- All state lives in `pmf/` in the user's project. Nothing outside it.
- Research before the panel when it is affordable; a panel grounded in real
  complaints is worth several grounded in guesses.
- Market searches, buyer discussions and source URLs route to `pmf-research`.
  Its bundled references handle platform access and fallbacks within PMF.
  Later stages reuse that evidence and request a refresh when it is stale.
- The real-world test in `pmf-test` is the evidence gate: its computed result
  gates the compiled verdict, and it overrides the simulated panel, always.
  Say so when they disagree.
- A stage that reruns records fresh fingerprints with
  `python3 <this skill's folder>/status.py record ...` so the next change can
  invalidate the right files.
- The pack is honest about itself: the panel is simulated, the buy rate is
  not a conversion forecast, the numbers are estimates until real quotes
  arrive, and none of it is financial, legal or tax advice. Never present it
  as more than that.

Next: run the earliest stale or missing stage, starting with `pmf-pressure`
for a new idea. `pmf-research` answers a market question on its own.
