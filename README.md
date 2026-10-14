# pmf: product-market fit skills for Claude Code, Codex and OpenCode

Thirteen product-market fit skills that take a business from idea to launch in
Claude Code, Codex and OpenCode: an adversarial pressure test, real market
research, a simulated buyer panel, the offer and its price, unit economics,
a real-world demand test with pre-set criteria, the smallest MVP with agentic
coding discipline, marketing, brand, operations, the launch and the compiled
plan.

One folder of skills, one state folder (`pmf/` in your project), one path from
"would this work" to a launched product. Free, MIT, standard-library Python
for the tools, nothing to sign up for.

## The thirteen

| skill | its job |
| --- | --- |
| `skills/pmf` | the front door: reads the state and its fingerprints, says what is fresh, stale or missing, routes |
| `skills/pmf-pressure` | three adversarial lenses (demand, moat, execution) score the idea and vote, with the kill list and a conditions checklist |
| `skills/pmf-research` | built-in platform routing and retries, competitors, prices, real complaints, buyer vocabulary and communities, every fact linked |
| `skills/pmf-panel` | a simulated panel of buyer agents (30 to start, scale up) with exact segment quotas, strict answer validation and before/after runs over the same buyers |
| `skills/pmf-offer` | the offer stack from the panel's objections, and the price from the four price answers, the competitor range and the margin floor |
| `skills/pmf-numbers` | unit economics: itemised costs with sources, contribution, break-even, margin, year 1 by month, cash needed, payback, red flags, what-if scenarios |
| `skills/pmf-test` | the evidence gate: the cheapest real-world test (pre-sale, pop-up, paid pilot, deposit waitlist) with criteria set before it runs, logged and computed |
| `skills/pmf-build` | the smallest real thing, only after a passed test (or a written decision): MVP scope, agentic coding discipline, two clean verification runs |
| `skills/pmf-marketing` | positioning, evidence-backed channels, a dated 30-day campaign, ten hooks, the CAC cap, three numbers to watch |
| `skills/pmf-brand` | name candidates with the checks to run, voice rules, the promise and taglines, the look brief |
| `skills/pmf-ops` | the daily cycle, suppliers, staffing triggers, tools, permits to confirm, the risk register |
| `skills/pmf-launch` | the dated countdown, the run sheet, and the first 30 days: the three numbers plus repeat purchase by cohort |
| `skills/pmf-plan` | compiles everything into `pmf/plan.md` with a verdict that is computed, never written |

## Install

### Claude Code

```
/plugin marketplace add Rish-it/pmf
/plugin install pmf@pmf
```

### Codex

```
codex plugin marketplace add Rish-it/pmf
codex plugin add pmf@pmf
```

### OpenCode, or any agent with a skills folder

```bash
git clone https://github.com/Rish-it/pmf.git
cd pmf
./install.sh
```

`install.sh` symlinks the thirteen skills into every agent's global skills
folder (`~/.claude/skills`, `~/.codex/skills`, `~/.config/opencode/skills`).
Use `--copy` to copy instead of symlink, `--uninstall` to remove them.

## How to use

Run them in roughly this order; each reads what the earlier ones wrote, all
inside a `pmf/` folder in your project:

```
pressure -> research -> panel -> offer -> numbers -> test -> build
                                        \-> marketing -> brand -> ops -> launch -> plan
```

Start with the `pmf` skill: it checks what is fresh, what has gone stale
since its inputs changed, and what is missing, then points at the next step.
Any single skill also runs alone when its inputs exist. Three things the pack
takes seriously:

1. **Research runs before the panel** whenever it can: a panel grounded in
   real complaints beats one grounded in guesses.
2. **The criteria are set before a test runs, never moved afterwards.** The
   outcome is computed from the actuals, not written by hand.
3. **Real evidence gates the verdict.** `pmf/plan.md` compiles to
   **Validated** only when the economics work and the latest real-world test
   met its pre-set criteria. It compiles to **Projected** when the numbers
   work but nothing real has been tested, **Not yet** when a check fails, and
   **Incomplete** when inputs are missing. A simulated buy rate never counts
   as real evidence; a failed test beats profitable projections, always.

`pmf/research/` feeds the panel's objections and the marketing copy.
`pmf-test` comes before `pmf-build`: build the smallest test rig first, learn
whether anyone pays, then build the product slice.

## The evidence gate

`pmf-test` turns a claim into a test: a pre-sale page with a refundable
deposit, a pop-up with real prices, three paid pilots, or a waitlist that
ends in a paid founding offer. Each test is written into
`pmf/experiments.json` with its method, audience, price and the go/no-go
criteria BEFORE it runs; `check` locks those criteria in
`pmf/experiments.lock.json`, and a result for an unlocked or edited test is
rejected. When the actuals land (exposure, paid conversions, refunds, cost,
notes), the tool computes the outcome: pass when every criterion is met,
mixed when some are, fail when none. Paid counts are net of refunds, a demand
test needs at least 5 paid, and rate bars are judged on the low end of a 95%
interval, so a tiny sample cannot pass on luck. After launch, the same log holds
retention tests (repeat purchase by cohort), because a first purchase is
interest and a repeat is a market.

`pmf/status.json` is the state ledger: every stage fingerprints what it wrote
and what it read. Change a price and the next `status.py check` marks the
panel, the economics, the plan and anything else downstream of that change as
stale, naming the stages to rerun. Previous panel runs are kept in
`pmf/panel/runs/` so a before-and-after comparison is always possible.

## Research access

PMF includes its research workflow. `pmf-research` checks available tools,
selects sources for the buyer and region, reads actual content, retries
failed reads through ready alternatives, and records what could not be
verified. No separate research skill is required.

The bundled references cover web search, pages, reviews, RSS, GitHub,
Twitter/X, Reddit, XiaoHongShu, Facebook, Instagram, V2EX, YouTube, Bilibili,
Xiaoyuzhou, LinkedIn, Boss Zhipin and Xueqiu. They include caption and audio
transcription routes, session checks and platform-specific failure rules.
Built-in search and readers work without installing extra tools. Specialist
CLIs and connectors are optional runtime backends; the pack does not bundle
them or create logins. Transcription needs a configured provider and
authorization to send the audio and incur any cost.

`pmf/research/reach.md` records each platform, backend, query or URL, access
date, useful content, failures and coverage limits. The findings live beside
it in `competitors.csv`, `complaints.md`, `voice.md` and `market.md`. Later
stages use this evidence for objections, pricing, channels and the test
design. Missing access stays visible instead of becoming invented evidence.

## The tools

Six tools, standard-library Python 3.8+, no network, each with tests in
`tests/` (and an example input where one helps):

```bash
python3 skills/pmf/status.py check --dir pmf
python3 skills/pmf-panel/panel.py init --customer pmf/customer.json --pitch pmf/pitch.md
python3 skills/pmf-offer/van_westendorp.py --panel pmf/panel --price 4.50
python3 skills/pmf-numbers/unit_economics.py pmf/numbers.json --out pmf/numbers.md
python3 skills/pmf-test/experiments.py check --dir pmf
python3 skills/pmf-plan/compile.py --dir pmf
python3 -m unittest discover -s tests -v
```

Every number traces to an input; a missing field is an error, never a guess;
impossible volumes (a plan above capacity) are refused; and the plan compiler
reuses the same calculation engine as the numbers report and the same outcome
evaluator as the test log, so nothing drifts.

## A worked example

Cart & Grounds, a mobile coffee cart for office parks, from the example
files. Unit economics at 4.50 a drink, with 1.60 of itemised per-drink costs
(three lines, two with a source):

- each drink leaves **2.90** after its own costs
- break-even is **44 drinks a day** against a capacity of 180
- the margin at 140 drinks a day is **44.3%**
- year 1 makes **71,850** on operations; the **18,500** startup spend is
  earned back in **month 5**; the cash needed is **18,500**, because the
  startup spend itself is the deepest point before the months turn positive
- the winter scenario (volume -35%) still leaves **30,742.50** for year 1

The ten price answers in the example land the acceptable range at **4.25 to
5.75** (marginal cheapness to marginal expensiveness), so 4.50 sits within
it.

Then the gate: the example's first test (E1) put a pre-sale page in front of
480 park workers with a refundable 4.50 deposit and a pre-set bar of at least
10 paid buyers at no more than 25.00 cost per paying buyer. Twelve paid
(2.5%), the test cost 150.00, and the tool computes **PASS**, so the plan
compiles to **Validated**. Change the actuals to three paid and the same
healthy projections compile to **Not yet**: the real result controls the
verdict. Every figure above comes out of the tools, not the README.

## Fine print

**The panel is simulated buyers, not customers.** Language models lean
agreeable, so read the buy rate as an upper bound with no known mapping to
real conversion; it finds objections, segments and wording cheaply before
real money is spent, and `pmf-test` exists to replace it with real buyers.
Panel quotes are research, never testimonials.

**A test result is one data point, not proof of product-market fit.** Read a
pass as permission to take the next step and a repeat purchase as the
beginning of a market.

**The numbers are only as good as the inputs.** The tools mark nothing as a
guess; you do. Cost lines without a source are called assumptions in the
plan. Estimates stay estimates until real quotes arrive, and structure,
payroll and tax belong with an accountant.

**Research uses public sources, with links.** No invented competitors,
prices, reviews or quotes, and no scraping against a site's terms.

**Not financial, legal or tax advice.** Permits, trademarks and claims depend
on where you are; the skills say what to check and where, a professional
confirms it.

## Files

```
skills/pmf/             SKILL.md, status.py (the state ledger)
skills/pmf-pressure/    SKILL.md
skills/pmf-research/    SKILL.md, references/ (access, web, communities, video, business)
skills/pmf-panel/       SKILL.md, panel.py, customer.example.json, pitch.example.md
skills/pmf-offer/       SKILL.md, van_westendorp.py, prices.example.csv
skills/pmf-numbers/     SKILL.md, unit_economics.py, example.json
skills/pmf-test/        SKILL.md, experiments.py, experiments.example.json
skills/pmf-build/       SKILL.md
skills/pmf-marketing/   SKILL.md
skills/pmf-brand/       SKILL.md
skills/pmf-ops/         SKILL.md
skills/pmf-launch/      SKILL.md
skills/pmf-plan/        SKILL.md, compile.py
tests/                  the tests for every tool and for this repo's own rules
install.sh              put the skills in every agent's skills folder
```

Your own files live in `pmf/` in your project. The skills read each other's.
The state contract is `idea.md`, `pressure.md`, `pressure/`, `research/`,
`customer.json`, `pitch.md`, `panel/` (with `runs/`), `offer.md`,
`numbers.json`, `numbers.md`, `experiments.json`, `experiments.lock.json`,
`test.md`, `build.md`,
`marketing.md`, `brand.md`, `ops.md`, `launch.md`, `plan.md`, `summary.md`
and `status.json` (the ledger the `pmf` skill owns). Each file has one owning
skill. Product code from `pmf-build` lives in the project's normal source
folders.

## License

MIT.
