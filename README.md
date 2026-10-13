# pmf: product-market fit skills for Claude Code, Codex and OpenCode

Twelve product-market fit skills that take a business from idea to launch in
Claude Code, Codex and OpenCode: an adversarial pressure test, real market
research, a simulated buyer panel, the offer and its price, unit economics,
the smallest MVP with agentic coding discipline, marketing, brand,
operations, the launch and the compiled plan.

One folder of skills, one state folder (`pmf/` in your project), one path from
"would this work" to a launched product. Free, MIT, standard-library Python
for the tools, nothing to sign up for.

## The twelve

| skill | its job |
| --- | --- |
| `skills/pmf` | the front door: checks `pmf/`, says what to run next, routes |
| `skills/pmf-pressure` | three adversarial lenses (demand, moat, execution) score the idea and vote, with the kill list and a conditions checklist |
| `skills/pmf-research` | built-in platform routing and retries, competitors, prices, real complaints, buyer vocabulary and communities, every fact linked |
| `skills/pmf-panel` | a simulated panel of buyer agents (100 by default) tallies who buys, who passes, why, and at what prices |
| `skills/pmf-offer` | the offer stack from the panel's objections, and the price from the four price answers, the competitor range and the margin floor |
| `skills/pmf-numbers` | unit economics: contribution, break-even, margin, year 1 by month, cash needed, payback, what-ifs |
| `skills/pmf-build` | the smallest real thing: MVP scope, agentic coding discipline, two clean verification runs, a handoff record |
| `skills/pmf-marketing` | positioning, evidence-backed channels, a dated 30-day campaign, ten hooks, the CAC cap, three numbers to watch |
| `skills/pmf-brand` | name candidates with the checks to run, voice rules, the promise and taglines, the look brief |
| `skills/pmf-ops` | the daily cycle, suppliers, staffing triggers, tools, permits to confirm, the risk register |
| `skills/pmf-launch` | the cheapest real-world test first, then the dated countdown, the run sheet, the first 30 days |
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

`install.sh` symlinks the twelve skills into every agent's global skills
folder (`~/.claude/skills`, `~/.codex/skills`, `~/.config/opencode/skills`).
Use `--copy` to copy instead of symlink, `--uninstall` to remove them.

## How to use

Run them in roughly this order; each reads what the earlier ones wrote, all
inside a `pmf/` folder in your project:

```
pressure -> research -> panel -> offer -> numbers -> build
                          \-> marketing -> brand -> ops -> launch -> plan
```

Start with the `pmf` skill and it will look at what exists and point you at
the next step. Any single skill also runs alone when its inputs exist. Two
things the pack takes seriously: research runs before the panel whenever it
can (a panel grounded in real complaints beats one grounded in guesses), and
a real-world test always overrides the simulated panel.

`pmf-build` writes product code in your repo, not in `pmf/`: it scopes the
smallest slice first, then applies the reuse ladder (does it need to exist,
is it already here, standard library, native feature, installed dependency,
one line, only then the minimum), leaves one runnable check for non-trivial
logic, and verifies twice.

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
stages use this evidence for objections, pricing, channels and the launch
test. Missing access stays visible instead of becoming invented evidence.

## The tools

Four tools, standard-library Python 3.8+, no network, each with an example
input next to it and tests in `tests/`:

```bash
python3 skills/pmf-panel/panel.py init --customer pmf/customer.json --pitch pmf/pitch.md
python3 skills/pmf-offer/van_westendorp.py --panel pmf/panel --price 4.50
python3 skills/pmf-numbers/unit_economics.py pmf/numbers.json --out pmf/numbers.md
python3 skills/pmf-plan/compile.py --dir pmf
python3 -m unittest discover -s tests -v
```

Every number traces to an input; a missing field is an error, never a guess.

## A worked example

Cart & Grounds, a mobile coffee cart for office parks, from the example
files. Unit economics at 4.50 a drink and 1.60 of costs per drink:

- each drink leaves **2.90** after its own costs
- break-even is **44 drinks a day** against a capacity of 180
- the margin at 140 drinks a day is **44.3%**
- year 1 makes **71,850** on operations; the 18,500 startup spend is earned
  back in **month 5**; cash needed before that is **18,385**
- price 10% lower, or volume 20% lower, or cost 10% higher: the what-ifs are
  in the report, each with its number

The ten price answers in the example land the acceptable range at **4.25 to
5.75** (marginal cheapness to marginal expensiveness), so 4.50 sits within
it. Every figure above comes out of the tools, not the README.

## Fine print

**The panel is simulated buyers, not customers.** Language models lean
agreeable, so read the buy rate as an upper bound; it finds objections,
segments and wording cheaply before real money is spent, and the launch test
exists to replace it with real buyers. Panel quotes are research, never
testimonials.

**The numbers are only as good as the inputs.** The tools mark nothing as a
guess; you do. Estimates stay estimates until real quotes arrive, and
structure, payroll and tax belong with an accountant.

**Research uses public sources, with links.** No invented competitors,
prices, reviews or quotes, and no scraping against a site's terms.

**Not financial, legal or tax advice.** Permits, trademarks and claims depend
on where you are; the skills say what to check and where, a professional
confirms it.

## Files

```
skills/pmf/             SKILL.md
skills/pmf-pressure/    SKILL.md
skills/pmf-research/    SKILL.md, references/ (access, web, communities, video, business)
skills/pmf-panel/       SKILL.md, panel.py, customer.example.json, pitch.example.md
skills/pmf-offer/       SKILL.md, van_westendorp.py, prices.example.csv
skills/pmf-numbers/     SKILL.md, unit_economics.py, example.json
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
`customer.json`, `pitch.md`, `panel/`, `offer.md`, `numbers.json`,
`numbers.md`, `build.md`, `marketing.md`, `brand.md`, `ops.md`, `launch.md`,
`plan.md` and `summary.md`. Each file has one owning skill. Product code from
`pmf-build` lives in the project's normal source folders.

## License

MIT.
