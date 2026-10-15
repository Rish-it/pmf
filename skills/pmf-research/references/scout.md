# Scout mode: what is worth building

Use this when there is no idea yet, or when the user asks whether a kind of
product is worth building: "what should I build in AI", "is an agent-native
version of X worth building", "what are YC and a16z funding", "what are AI
companies hiring for", "map the SF or NYC AI scene". The result is a short
list of opportunities with evidence, and a plain verdict on each, including
"do not build".

Read [signals.md](signals.md) for the sources and commands, and
[brief.md](brief.md) for the dated SF and NYC context. Fetch rules, retries
and coverage logging stay in [reach.md](reach.md).

## Evidence rules

- **Every factual claim has a link and a date.** The date is when the source
  published it; if the page shows none, write the access date and say so. A
  claim without a source is written as "unverified" and cannot support a
  verdict.
- **Label each claim.** F for what a source states, I for your inference from
  sources, S for speculation. Never present an I or S as an F.
- **Count independent sources.** Sources are independent when different
  organisations or authors produced them. Coverage of one announcement counts
  once; a company's own launch post counts once. Record the count and the
  platform types (web, X, Reddit, HN, job boards, GitHub, filings).
- **Lists and essays are pointers.** A curated list, a vote, a founder essay
  or an investor thesis tells you where to look. It is never the only proof
  of demand. Say so when a list's author invests in the companies it ranks.
- **Funding is capital, not traction.** Traction is paying customers, revenue,
  usage numbers or a shipped product people use. Say which one you have.
- **Self-reported numbers are labelled self-reported.** Benchmarks run by the
  vendor of the product being measured are flagged.

## Step 1: frame the question

Write the question in one line, the segment it is for (for example "teams of
50 to 500 engineers using coding agents") and the as-of date. If the user
named a case, such as a company's internal tool, read the primary source in
full first and write down what was built, why existing tools fell short, and
what the authors themselves say about who else needs it. With no case,
collect the signals first, then list 3 to 8 candidate problems that several
signals point at; many cheap candidates beat one polished one.

## Step 2: collect signals

Use at least three of the five signal types in [signals.md](signals.md):
funding, hiring, launches, buyer pain, and incumbent moves. One signal type
alone never supports a verdict. Buyer pain is direct or proxy; Step 4 says
how each counts.

## Step 3: the absorption check

This step decides most verdicts. For each candidate, search the last six
months of the incumbents' own changelogs, docs and launch posts: the main
platforms in the category (for developer tools, GitHub, GitLab, the AI labs
and the leading coding agents), the best-funded startups found in Step 2, and
open-source copies of any widely shared design. Record each hit with its
date and whether it is shipped, in preview, or announced.

A candidate is **absorbed** for a segment when an incumbent shipped or
previewed its core job for that segment. Look for what the incumbent's
version leaves out: a segment it does not reach (self-hosted, a regulated
industry, another platform), a buyer it does not serve, or a gap its own
docs or users name. Only a named, sourced gap keeps a candidate alive.

## Step 4: judge each opportunity

| verdict | when |
| --- | --- |
| Build | 3 or more independent sources across 2 or more platform types, buyer pain in buyers' own words, and no incumbent has absorbed the core job for the target segment |
| Build narrow | the core is absorbed, but a sourced gap remains for a named segment; build only for that segment |
| Join | the evidence is strong, a funded startup owns it, and it is hiring; name the teams |
| Watch | promising but fewer than 3 independent sources, or demand only from lists and essays |
| Do not build | absorbed with no sourced gap, or no buyer pain found |

Read the table top to bottom; the first row that fits is the verdict.

Buyer pain comes in two strengths. Direct: buyers describe the problem or
ask for a fix in their own words. Proxy: job posts that describe the
problem, and teams that built the tool in-house. Investor theses and lists
are not pain. With proxy pain only, the best verdict is Build narrow, and
the first 90 days must start with interviews that can kill the idea.

"Do not build" is a useful answer. Say it in the first line when the
evidence points there.

## Step 5: write `pmf/research/opportunities.md`

```markdown
# Opportunities: <question>
As of <date>. Verdict: <one line, including "do not build" if that is the answer>.

## <opportunity name> - <verdict>
- Independent sources: <n> (<platform types>)
- What exists: <products, incumbents and their shipped or previewed features, dated>
- The gap that is left: <sourced, or "none found">
- Buyer and pain: <who, linked; say whether the pain is direct or proxy>
- Price anchors: <what buyers pay today for nearby tools, linked>
- Integrations and security needs: <platforms it must work with, controls buyers need>
- Why now: <dated signals>
- Moat, and who could absorb it: <how fast, with evidence>
- What would change this verdict: <specific events or findings>
- First 90 days: <weeks 1-2, 3-6, 7-12; each with a measurable result>
- Design-partner targets: <organisations with a public signal, each linked and dated; no personal contact data>

## Claims
| id | claim | label | source | date |
| --- | --- | --- | --- | --- |

## Coverage
<sources reached, failed reads, rate limits, and how they limit the verdict>
```

Keep the part above the claims table under about 1,000 words; the table
holds the detail. Also
write the access log to `pmf/research/reach.md` as reach.md describes.

Design-partner targets are organisations, chosen because a public post, job
listing or launch shows the pain. Name the signal and link it. Do not look up
emails, phone numbers or private profiles, and do not contact anyone.

## Step 6: self-check before returning

Answer each line; fix the file until every answer is yes.

1. Does every claim row have its own full link (never "same" or "above")
   and a date, or say "unverified"?
2. Is every claim labelled F, I or S?
3. Does every opportunity state its independent-source count and platforms?
4. Is any verdict resting on a single source, or on lists and essays alone?
   If so, downgrade it to Watch. Is a Build resting on proxy pain only? If
   so, downgrade it to Build narrow.
5. Was the absorption check run, with dated incumbent results?
6. Does the Coverage section name every failed or rate-limited read?
7. Is the brief you used (`pmf/research/brief.md` if present, else this
   skill's brief.md) older than 60 days? If so, refresh the parts you used or
   say they are stale.
8. Does the file contain any personal contact details? Remove them.

## What this mode declines

It does not look up personal contact details, send messages, scrape logged-in
or private content, or predict investment returns. When a request asks for
one of these, do the public-evidence part, say what was left out and why,
and offer the nearest allowed step: for outreach, that is the founder
outbound test in `pmf-test`, where the user reviews each draft and sends it
by hand to people who posted in public.

Next: hand the chosen opportunity to the `pmf-pressure` skill, which writes
`pmf/idea.md`; then run this skill again in its normal mode on that idea.
