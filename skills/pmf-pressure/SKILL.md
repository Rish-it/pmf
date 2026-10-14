---
name: pmf-pressure
description: >-
  Puts a business idea in front of three adversarial lenses before any money
  moves: the demand lens (do buyers need it now and pay for it today), the
  moat lens (what compounds, why it will not be copied) and the execution lens
  (can this founder ship the smallest version). Each lens scores the idea,
  names what would kill it and votes fund, fund with conditions, or pass. The
  conditions become the checklist the rest of the pack answers. Use when the
  user says "test my business idea", "would this work", "pressure-test this",
  "is this a good business", or starts the pmf pack on a new idea.
argument-hint: "<the business idea, or leave blank to use the conversation>"
---

# pmf-pressure

The first meeting, before a website, a lease or a line of code. One idea in,
three honest scores, a vote, and a conditions checklist the rest of the pack
has to satisfy.

If the user's message names the idea, use it. If it is blank, take the idea
from the conversation.

## Step 0: the idea file

Everything in the pack reads `pmf/idea.md` in the user's project. If it does
not exist, write it now:

```markdown
# <working business name>

- Problem and proposed solution: <one sentence>.
- First buyer: <specific customer and buying trigger>.
- Paid unit: <product or service, price and currency>.
- Route to the buyer: <region, discovery channel and delivery method>.
- Limits: <available cash, time, skills and fixed decisions>.
```

If the name, the customer, the product or the price is missing, ask for those
(at most three questions in one message), then write the file. Never invent a
budget, a market size or a competitor.

## Step 1: the brief

Write `pmf/pressure/brief.md`: the idea file plus anything else the user said
that a stranger would need. If you spawn sub-agents, they cannot see this
conversation, so the brief must stand on its own. Do not add your own opinion
to it.

## Step 2: the three lenses

Apply each lens to the brief and write one memo per lens. If you can spawn
sub-agents (Claude Code: the Agent tool; Codex and OpenCode: their own
sub-agent tools), launch all three in ONE message, one per lens. If you
cannot, apply the three lenses yourself, one memo each, clearly labeled.

The lenses, written here so every arrangement applies the same three:

- **Demand lens.** Is there a buyer with this problem right now? What do they
  do today instead? What trigger makes them start looking? Does money already
  change hands in this market, and at what price? A need without a current
  spend or a painful workaround is a warning.
- **Moat lens.** If it works, who copies it next month, and what stops them?
  What compounds over time (custom, data, brand, a niche nobody bothers with,
  a cost position)? "First mover" is not an answer. If the honest answer is
  "nothing yet", say that and name the smallest thing that could become one.
- **Execution lens.** Can THIS founder, with the stated budget, time and
  skills, ship the smallest version? What is the single riskiest operational
  step? Which one number must be true for the rest to matter (a price, a cost,
  a conversion rate), and how would we find out cheaply?

Each memo, in this shape:

```markdown
# <lens>
Score: <1-10> | Vote: FUND / FUND IF / PASS
## What is strong
## What would kill it (top 3, most dangerous first)
## The one number that must be true
## If FUND IF: the conditions
```

Scores are not flattery: a 7+ means you would put your own money in.

## Step 3: the chair's summary

Read the three memos and write `pmf/pressure.md`:

1. The vote, e.g. "2 fund if, 1 pass", and the average score.
2. The kill list: every risk the lenses named, deduplicated, ranked.
3. The conditions checklist: every FUND IF condition, as `- [ ]` checkboxes
   the later skills can satisfy (research answers the market ones, the panel
   the demand ones, the numbers the economics ones). `pmf-plan` counts these
   checkboxes, so keep one condition per line and tick it (`- [x]`) only when
   a recorded artifact actually satisfies it.
4. The one number each lens said must be true, in one table.

## Output

`pmf/idea.md`, `pmf/pressure/brief.md`, `pmf/pressure/<lens>.md` (or inline
memos if run solo), `pmf/pressure.md`. Record the fingerprints with the
status tool in the `pmf` skill's folder:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact pressure.md --input idea.md --skill pmf-pressure
```

Next: run the `pmf-research` skill. Its findings either retire the kill list
or confirm it.
