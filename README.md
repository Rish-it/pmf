# pmf: product-market fit skills for Claude Code, Codex and OpenCode

![pmf](assets/icon.svg)

Thirteen agent skills that take a business idea to launch on real evidence, in Claude Code, Codex and OpenCode: a pressure test, sourced market research, a buyer panel, the offer and its price, unit economics, a real demand test with criteria locked before it runs, the smallest MVP, marketing, brand, operations, launch and a computed verdict.

[![tests](https://github.com/Rish-it/pmf/actions/workflows/tests.yml/badge.svg)](https://github.com/Rish-it/pmf/actions/workflows/tests.yml)
![license: MIT](https://img.shields.io/badge/license-MIT-0A4D8C)
![python: stdlib only](https://img.shields.io/badge/python-stdlib%20only-0A4D8C)

Most idea checks end in an opinion. This pack ends in `pmf/plan.md`, a
verdict computed from your numbers and from what real buyers did:

**Verdict: Validated**

| check | result | the numbers |
| --- | --- | --- |
| Each unit earns money | pass | contribution 2.90 per drink |
| Year 1 makes an operating profit | pass | year 1 operating 71850.00 |
| Break-even fits capacity | pass | break-even 44 per day against capacity 180 |
| Real test E1: min_paid | pass | 11 paid after refunds against a bar of 10 |
| Real test E1: price | pass | tested at 4.50 against a plan price of 4.50 |

A simulated panel can never produce that verdict. Only a real test can, one
whose bar was written down before it ran.

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

## Start

Tell your agent:

> Run pmf on my idea: a mobile coffee cart for office parks.

The `pmf` skill reads the state folder, says what is done, stale or missing,
and runs the next stage. Everything lands in a `pmf/` folder in your project,
so you can stop and pick up later. Any stage also runs on its own once its
inputs exist.

```
pressure -> research -> panel -> offer -> numbers -> test -> build
                                        \-> marketing -> brand -> ops -> launch -> plan
```

## The thirteen

| skill | its job |
| --- | --- |
| `skills/pmf` | the front door: reads the state and its fingerprints, says what is fresh, stale or missing, routes |
| `skills/pmf-pressure` | three adversarial lenses (demand, moat, execution) score the idea and vote, with the kill list and a conditions checklist |
| `skills/pmf-research` | competitors, prices, real complaints, buyer vocabulary, communities and people asking for a fix right now, every fact linked; scout mode finds what is worth building from funding, hiring, launches and incumbent moves |
| `skills/pmf-panel` | a simulated panel of buyer agents (30 to start) with exact segment quotas, strict answers, objections traced to real quotes, and before/after runs over the same buyers |
| `skills/pmf-offer` | the offer stack from the panel's objections, and the price from the four price answers, the competitor range and the margin floor |
| `skills/pmf-numbers` | unit economics: itemised costs with sources, contribution, break-even, margin, year 1 by month, cash needed, payback, red flags, what-if scenarios |
| `skills/pmf-test` | the evidence gate: the cheapest real test (pre-sale, pop-up, paid pilot, deposit waitlist, founder outbound) with criteria locked before it runs |
| `skills/pmf-build` | the smallest real thing, only after a passed test (or a written decision): MVP scope, agentic coding discipline, two clean verification runs |
| `skills/pmf-marketing` | positioning, evidence-backed channels, a dated 30-day campaign, ten hooks, the CAC cap, three numbers to watch |
| `skills/pmf-brand` | name candidates with the checks to run, voice rules, the promise and taglines, the look brief |
| `skills/pmf-ops` | the daily cycle, suppliers, staffing triggers, tools, permits to confirm, the risk register |
| `skills/pmf-launch` | the dated countdown, the run sheet, and the first 30 days: the three numbers plus repeat purchase by cohort |
| `skills/pmf-plan` | compiles everything into `pmf/plan.md` with a verdict that is computed, never written |

## How the verdict is computed

| verdict | when |
| --- | --- |
| **Validated** | the economics work, the latest demand test met every criterion locked before it ran, at the plan's price, and no later retention test failed |
| **Projected** | the economics work, but nothing real has been tested yet |
| **Not yet** | an economics check fails, or the latest real test missed its bar |
| **Incomplete** | an input is missing or invalid, or a test's criteria moved after they were locked |

A failed real test beats profitable projections, always. The simulated panel
finds objections and wording; it never gates the verdict.

## The evidence gate

`pmf-test` turns a claim into a test: a pre-sale page with a refundable
deposit, a pop-up at real prices, three paid pilots, a waitlist that ends in
a paid founding offer, or personal messages the founder sends to people found
asking for a fix. Each test goes into `pmf/experiments.json` with its method,
audience, price and go/no-go criteria before it runs.

- **Locked criteria.** `check` fingerprints every planned test into
  `pmf/experiments.lock.json`. Results on a test that was never locked, or
  whose criteria, price or dates changed after the lock, are rejected.
- **No luck passes.** A demand test needs at least 5 paid buyers, paid is
  counted after refunds, and rate bars are judged on the low end of a 95%
  interval, so one friend or a cohort of two cannot clear a bar.
- **The plan's price.** A test charging more than 10% under the plan price
  cannot validate that plan.
- **The whole record.** The latest demand test and the latest retention test
  both count, so a later pass cannot hide an earlier failure.

`pmf/status.json` is the state ledger: every stage fingerprints what it wrote
and what it read. Change a price and `status.py check` marks the panel, the
economics, the tests and the plan as stale, naming the stages to rerun.
Previous panel runs stay in `pmf/panel/runs/` for before-and-after
comparisons.

## Research access

`pmf-research` carries its own research workflow; nothing else needs
installing. It checks which tools are present, picks sources for the buyer
and region, reads the actual content, retries through ready alternatives,
and writes down what it could not reach.

- **No install needed:** the agent's own search and page reader, plus Exa
  search, App Store and Trustpilot reviews, Hacker News, Stack Exchange,
  GitHub and V2EX over plain `curl`.
- **When present:** command-line tools and connectors for Twitter/X, Reddit,
  XiaoHongShu, Facebook, Instagram, YouTube, Bilibili, Xiaoyuzhou, LinkedIn,
  Boss Zhipin and Xueqiu, with session checks and per-platform failure rules.
  The pack never installs them or logs in for you.

`pmf/research/reach.md` records each platform, backend, query or URL, access
date, useful content, failures and coverage limits. The findings sit beside
it in `competitors.csv`, `complaints.md`, `voice.md`, `market.md` and
`leads.md` (people showing a public buying signal, for the outbound test).
Missing access stays visible instead of becoming invented evidence.

With no idea yet, scout mode asks what is worth building. It reads funding
trackers, portfolio job boards, launches, founder writing and incumbent
changelogs, checks whether a platform has already shipped the idea, and
writes `opportunities.md`: each opportunity with its independent-source
count, a verdict from build to do not build, a 90-day plan and the claims
behind it, every one linked and dated. A dated SF and NYC brief ships with
the skill and is refreshed into `pmf/research/brief.md`.

## Data and privacy

pmf has no server, account or telemetry; its six tools run offline and
everything it writes stays in `pmf/` in your project. During research your
agent sends public queries and public URLs to Exa search (`mcp.exa.ai`),
the Jina reader (`r.jina.ai`), Hacker News search (`hn.algolia.com`),
Stack Exchange, V2EX, GitHub, the App Store reviews feed and the public
pages it reads, plus any tools you installed yourself. Details are in
[PRIVACY.md](PRIVACY.md).

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
impossible volumes are refused; and the plan compiler reuses the same
calculation engine as the numbers report and the same outcome evaluator as
the test log, so nothing drifts.

## A worked example

Cart & Grounds, a mobile coffee cart for office parks, from the example
files. At 4.50 a drink with 1.60 of itemised per-drink costs:

- each drink leaves **2.90** after its own costs
- break-even is **44 drinks a day** against a capacity of 180
- the margin at 140 drinks a day is **44.3%**
- year 1 makes **71,850** on operations; the **18,500** startup spend is
  earned back in **month 5**, and the cash needed is **18,500**
- the winter scenario (volume -35%) still leaves **30,742.50** for year 1
- the ten price answers put the acceptable range at **4.25 to 5.75**

Then the gate. Test E1 put a pre-sale page with a refundable 4.50 deposit in
front of 480 park workers, with a bar locked in advance: at least 10 paid, at
no more than 25.00 per paying buyer. Fourteen paid and three asked for
refunds, so **11** count; the test cost 150.00, or **13.64** per paying buyer.
The outcome is **PASS** and the plan compiles to **Validated**. Make it three
paid and the same healthy projections compile to **Not yet**. Every figure
here comes out of the tools.

## Fine print

**The panel is simulated buyers, not customers.** Language models lean
agreeable, so read its buy rate as an upper bound with no known mapping to
real conversion. Objections traced to real buyer quotes make it sharper;
`pmf-test` exists to replace it with real buyers. Panel quotes are research,
never testimonials.

**A test result is one data point, not proof of product-market fit.** Read a
pass as permission to take the next step, and a repeat purchase as the
beginning of a market.

**The numbers are only as good as the inputs.** Cost lines without a source
are called assumptions in the plan. Structure, payroll and tax belong with an
accountant.

**Research uses public sources, with links.** No invented competitors,
prices, reviews or quotes, no scraping against a site's terms, and no
messages sent on your behalf.

**Not financial, legal or tax advice.** Permits, trademarks and claims depend
on where you are; the skills say what to check, a professional confirms it.

## Files

```
skills/pmf/             SKILL.md, status.py (the state ledger)
skills/pmf-pressure/    SKILL.md
skills/pmf-research/    SKILL.md, references/ (access, web, communities, video, business,
                        scout, signals, brief)
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
assets/                 the icon
tests/                  the tests for every tool and for this repo's own rules
install.sh              put the skills in every agent's skills folder
PRIVACY.md              what pmf handles and which services research contacts
```

Your own files live in `pmf/` in your project. The state contract is
`idea.md`, `pressure.md`, `pressure/`, `research/`, `customer.json`,
`pitch.md`, `panel/` (with `runs/`), `offer.md`, `numbers.json`,
`numbers.md`, `experiments.json`, `experiments.lock.json`, `replies.md`,
`test.md`, `build.md`, `marketing.md`, `brand.md`, `ops.md`, `launch.md`,
`plan.md`, `summary.md` and `status.json` (the ledger the `pmf` skill owns).
Each file has one owning skill. Product code from `pmf-build` lives in the
project's normal source folders.

## License

MIT.
