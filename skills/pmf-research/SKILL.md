---
name: pmf-research
description: >-
  Finds what is worth building and researches the market for it, every fact
  linked and dated. Scout mode: with no idea yet, or when asked whether a
  product is worth building, reads funding, hiring, launches, incumbent
  changelogs and SF and NYC AI activity, checks whether a platform already
  shipped it, and returns opportunities with independent-source counts and a
  verdict from build to do not build. Market mode: for an idea, maps the
  competitors, prices, real complaints, buyer language and where buyers hang
  out. Carries its own platform routing, retries and fallbacks. Use when the
  user asks "what should I build", "what should I build in AI", "is X worth
  building", "should I start a company doing X", "what are YC and a16z
  funding", "what are AI companies hiring for", "map the SF or NYC AI scene",
  "who are my competitors", "is this market crowded", "what do buyers
  complain about", "find the gap", "market research", or after the pressure
  test.
argument-hint: "[city, market or niche to focus on]"
---

# pmf-research

Every buyer already solves this problem somehow. This skill finds out how,
what they pay, what they hate, and in which words they say it, so the rest of
the pack stops guessing.

## The rules

- **Public sources only, every fact linked.** Websites, price pages, menus,
  app stores, map listings, review sites, communities, video, news. If a
  source cannot be reached, say so. Never invent a competitor, a price, a
  rating, a review or a quote.
- **Read only.** Follow each site's access rules and request limits. Do not
  post, comment, contact buyers or change an account during research.
- **Quotes are verbatim, short, linked, dated.** They are research material,
  never testimonials.
- **Where a fact is thin, mark it thin.** One review is an anecdote; three or
  more is a theme.

## Which mode

- **Market mode** (the default, Steps 0 to 6 below): an idea exists in
  `pmf/idea.md`, and this skill maps its competitors, buyers and gap.
- **Scout mode**: there is no idea yet, or the question is whether a kind of
  product is worth building at all. Read
  [references/scout.md](references/scout.md) in this skill's folder and
  follow it instead of Steps 1 to 6. It writes
  `pmf/research/opportunities.md` and uses Step 0's access rules.

## Step 0: choose sources and check access

Read [references/reach.md](references/reach.md) in this skill's folder.
It contains the capability check, the platform table and the retry rules.
Open the matching reference before fetching from a platform. These are part
of this skill; do not hand the task to another research skill.

Pick sources for this buyer and region: a search engine for discovery,
official pages for prices, and buyer discussions or reviews for demand.
Include video or regional communities when they matter to the idea. Do not
visit all platforms just because they are listed. Batch independent reads
when the available tools support it; keep each platform's retries serial.

Write `pmf/research/reach.md` as you work: platform, backend, query or URL,
access date, useful content found, failed attempts, and coverage limits.
Report the sources being checked in plain words. Empty output is a failed
read even if the command succeeds. A search snippet is a lead, not a quote.

If a backend is missing, follow the reference's fallback and keep going.
Use built-in search and page reading when no specialist backend is ready.
Describe the resulting gaps; never replace missing evidence with a guess.

## Step 1: who is there

Read `pmf/idea.md`. If it is missing and the user has an idea, run
`pmf-pressure` to capture it before researching; if they have none, use
scout mode. Classify the alternatives:

| type | what it means |
| --- | --- |
| Direct | sells the same thing to the same buyer |
| Indirect | a different product for the same job |
| Substitute | how buyers cope without a business: DIY, forums, a spreadsheet |

Aim for 5 to 10 direct and indirect, plus the main substitutes. For a local
business, search the map for the exact area; for online, search how a buyer
would ("best <thing> for <who>", "<thing> alternative").

## Step 2: the facts

One row per competitor in `pmf/research/competitors.csv`:

`name,type,url,location_or_channel,price_of_comparable_item,what_it_sells,positioning_line,rating,review_count,source_date`

`positioning_line` is their own headline, copied within the source's quote
limit. Price is for the closest comparable item. Record its currency,
billing period, inclusions and source URL in `pmf/research/market.md` so
unlike prices are not mixed. Leave unavailable fields empty and explain
them in that report. Never treat a missing price as zero.

## Step 3: what their customers say

For the top 3 to 5 competitors, read reviews (1 to 3 stars first, then the
"love it, but..." 4 stars) and community threads. Write
`pmf/research/complaints.md`: each recurring complaint as a theme with a
count of distinct buyers, source links, and short verbatim quotes per theme.
Deduplicate cross-posts and repeated subtitle lines. Record the source date
when visible, and the access date. Separate paid promotion from buyer
reports. Distinguish observed behavior from stated intent.
Include the compliments too, briefly: what buyers already love is what the
offer must not throw away.

## Step 4: the voice bank

The most reusable output. Write `pmf/research/voice.md`: verbatim phrases
from real buyers, each tagged and linked.

- `[objection]` what stops them today ("the last one broke in a month")
- `[desire]` what they say they want, in their words
- `[trigger]` what makes them start looking ("when the old one died")
- `[words]` the vocabulary they use (never use a word they do not)

The panel writes real objections from this bank, marketing writes hooks from
it, the offer answers it. This file is why research runs before everything.

## Step 5: where they hang out

A short list of the places this buyer already is: communities, forums,
channels, channels types (with sizes when visible), local spots. Only what
you actually found, linked. This feeds `pmf-marketing` directly; a generic
channel list is worth nothing here.

## Step 5b: who is looking right now

A list of real people or organisations showing a buying signal in public,
for the real test in `pmf-test`. Write `pmf/research/leads.md`, one row each:

`| who | signal | link | date | why they fit |`

Signals worth a row, strongest first:

- asking for a recommendation or an alternative ("anyone know a cart that
  delivers to the office?", "alternative to <competitor>")
- complaining in public about a competitor, or about coping without one
- a job post or a project that names the problem this business solves
- a change that starts the search: a new office, a funding round, a move, a
  tool being retired

`who` is the public name, handle or organisation exactly as posted, with the
link to the public post. Do not look up emails, phone numbers or private
profiles, do not buy lists, and do not contact anyone from this skill. Aim
for 20 to 50 rows for a B2B or service idea; for a walk-in business, list
the places and groups instead of people. Under 10 rows, say the list is thin.

## Step 6: the gap and the threat

Write `pmf/research/market.md`:

1. The competitor table (from the CSV), sorted by how directly each competes.
2. The price range: lowest, median, highest for the comparable item.
3. A positioning map in text: two axes that matter to this buyer, where each
   competitor sits.
4. The complaints ranked, with links.
5. **The gap**: what nobody does well that this business could, tied to the
   evidence. If there is no gap, say so plainly; it is the most useful result
   this skill can give.
6. The threat: who could copy this fastest, and how.
7. Coverage: which buyer groups and platforms were reached, what could not
   be read, and how those gaps limit the conclusions. Link `reach.md`.

## Output

`pmf/research/competitors.csv`, `pmf/research/complaints.md`,
`pmf/research/voice.md`, `pmf/research/market.md`, `pmf/research/reach.md`,
and `pmf/research/leads.md` when Step 5b found anyone. Scout mode writes
`pmf/research/opportunities.md`, `pmf/research/reach.md`, and
`pmf/research/brief.md` when it refreshed the SF and NYC brief.
Record the fingerprints with the status tool in the `pmf` skill's folder:

```bash
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact research/reach.md --input idea.md --skill pmf-research
python3 <the pmf skill's folder>/status.py record --dir pmf \
  --artifact research/market.md --input idea.md --skill pmf-research
```

In scout mode, record `research/opportunities.md` the same way, without
`--input`, since no idea exists yet.

Next: run the `pmf-panel` skill. Its objections come from the voice bank; its
pitch answers the gap. After scout mode, run `pmf-pressure` on the chosen
opportunity instead.
