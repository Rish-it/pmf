# pmf: notes for agents working in this repo

This repo is a skill pack: twelve agent skills that take a business idea from
"would this work" to a launched product, plus four standard-library Python
tools and their tests. It works in Claude Code, Codex and OpenCode from one
`skills/` folder.

## Hard rules

- **Harness neutrality.** Skill files must never contain `$ARGUMENTS`,
  `${CLAUDE_SKILL_DIR}` or any other harness-specific variable. A skill's own
  folder is referred to as "this skill's folder" and the tools are run with the
  agent resolving that path. `tests/test_repo.py` enforces this.
- **Tools are stdlib only**, Python 3.8+, and never touch the network. A
  missing input is an error, never a guess.
- **Tests.** Every non-trivial behavior has a test in `tests/`. Run:
  `python3 -m unittest discover -s tests -v`
- **Style.** ASCII only, no em-dashes (test-enforced). Short sentences, plain
  words, no marketing voice inside skill files.
- **Commits.** Atomic, imperative, no AI or tool attribution anywhere.
- **License.** MIT. Keep it.

## Layout

```
skills/pmf/            front door: state check + routing
skills/pmf-*/          the twelve skills, one stage each
skills/pmf-research/   + references/ (platform access, retries and evidence)
skills/pmf-panel/      + panel.py (buyer cards, answers, tally)
skills/pmf-offer/      + van_westendorp.py (price range)
skills/pmf-numbers/    + unit_economics.py (margins, break-even, year 1)
skills/pmf-plan/       + compile.py (plan + computed verdict)
tests/                 the tests for every tool and for this repo's rules
.reference/            local study material, gitignored, never shipped
```

## Adding or changing a skill

1. One folder per skill under `skills/`, named `pmf-<stage>`.
2. `SKILL.md` frontmatter: `name` (matches the folder) and a `description`
   that says what it does and when to use it, including trigger phrases.
3. The skill reads and writes only the state contract: a `pmf/` folder in the
   user's project. Never invent a file outside it.
4. End the skill with a `Next:` line naming the natural following skill.
5. Update the table in `README.md` and the skill list in `tests/test_repo.py`.
6. If the skill ships a tool, the tool lives in the skill's folder, has its
   own tests and an example input next to it.

## The state contract

Every skill in the pack reads and writes one `pmf/` folder in the user's
project: `idea.md`, `pressure.md`, `pressure/`, `research/`, `customer.json`, `pitch.md`,
`panel/`, `offer.md`, `numbers.json`, `numbers.md`, `build.md`,
`marketing.md`, `brand.md`, `ops.md`, `launch.md`, `plan.md`, `summary.md`.
Two skills never write the same file. If you need new state, add a file and
document it here and in the README.

`pmf-research` owns `research/competitors.csv`, `research/complaints.md`,
`research/voice.md`, `research/market.md` and `research/reach.md`. The last
file records platform access, backends, failed reads and coverage limits.
Its platform workflow lives in this pack. Optional runtime backends do not
change the standard-library-only, offline rule for the four Python tools.
`pmf-build` writes its state to `build.md` and product code to the project's
normal source folders.
