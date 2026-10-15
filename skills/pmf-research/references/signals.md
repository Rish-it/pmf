# Ecosystem signals: sources and commands

Scout mode reads five signal types. Each source below was checked on
2026-10-15; require real content as [reach.md](reach.md) says, and log every
read in `pmf/research/reach.md`.

## Standing sources

| source | what it gives | refresh | weakness |
| --- | --- | --- | --- |
| [Crunchbase News quarterly reports](https://news.crunchbase.com/) | funding totals, AI share, largest rounds and exits by region | quarterly | headline data; deal pages may need an account |
| [AlleyWatch](https://www.alleywatch.com/) and [Tech:NYC blog](https://www.blog.technyc.org/) | NYC daily deals, monthly totals, Series A cohorts with sectors | daily, monthly | NYC only; company-reported amounts |
| [YC RFS](https://www.ycombinator.com/rfs), [YC Launches](https://www.ycombinator.com/launches), [yc-oss API](https://yc-oss.github.io/api/batches/summer-2026.json) | what YC asks for, what each batch launches, batch data as JSON | per batch, daily | YC's frame; API lists fewer companies than YC's headlines |
| [jobs.a16z.com](https://jobs.a16z.com/) and [HN Who is hiring](https://news.ycombinator.com/submitted?id=whoishiring) | what companies pay engineers to build in-house | daily, monthly | a16z portfolio skews late-stage; HN skews small teams |
| [Frontier List](https://frontierlist.com/), [Breakout List](https://breakoutlist.com/), [Pavlov's List](https://pavlovslist.com/) | insider votes with counts, team size, HQ; who is breaking out | weekly to monthly | survey of one network, mostly SF; author invests in some picks |
| Incumbent changelogs: [GitHub changelog](https://github.blog/changelog/), [GitLab blog](https://about.gitlab.com/blog/), lab engineering blogs | what platforms just shipped or previewed | daily | written by the vendor |
| [Product Hunt feed](https://www.producthunt.com/feed) and [Latent Space](https://www.latent.space/archive) | daily launches; AI engineering news and analysis | daily, weekly | launches are not demand; newsletter has a point of view |

Founder writing on how to build (Paul Graham's essays, Chris Barber's
essays, investor blogs such as Bessemer Atlas and Menlo Ventures'
perspective reports) explains methods and theses. Use it to frame
questions; it is never the proof.

## Funding

Search the trackers above, then open the company's own announcement for the
amount, lead investor, date and what the money is for. A funding round shows
where capital is going, not that buyers pay.

```bash
curl --fail --max-time 30 "https://r.jina.ai/https://www.alleywatch.com/category/business/nyc-ai/"
mcporter call exa.web_search_exa query="agent infrastructure startup raises seed October 2026" numResults=8
```

## Hiring

Job posts are buyer pain written by the people who own the problem. Count
companies, not postings.

1. Query the board with several phrasings of one problem. jobs.a16z.com
   filters server-side with `?q=`; it returns at most about 24 jobs and
   matches loosely ("source control" also returns "technical sourcer"):

   ```bash
   curl -sS --max-time 30 -A "Mozilla/5.0" "https://jobs.a16z.com/jobs?q=developer%20productivity" \
     | grep -oE 'jobs/[a-z0-9-]+/[a-f0-9-]{36}--[a-z0-9-]+' | sort -u
   ```

   The path holds the company and the title. Keep only titles that name the
   problem; drop the rest by hand and say how many you dropped.
2. Count distinct companies per problem. Treat counts as floors: the board
   caps results and titles hide work that only the description names.
3. Read three or more descriptions per problem through the page reader.
   Record the posted date, and flag posts older than six months as stale.
   Quote the lines that describe the pain.
4. Cross-check with a second board. HN Who is hiring through the Algolia API
   gives counts per monthly thread:

   ```bash
   curl -sS "https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&hitsPerPage=3"
   curl -sS "https://hn.algolia.com/api/v1/search?tags=comment,story_THREAD_ID&query=evals&hitsPerPage=0"
   ```

   Read `nbHits`; open a sample of matching comments before relying on it.
   Other portfolio boards (for example jobs.sequoiacap.com) read the same
   way through the page reader.
5. LinkedIn job search is too loose for counts: check how many returned
   titles are on topic, and if fewer than half are, use it only to find
   single postings.

Write the table: problem, number of companies, example companies, posting
dates, and whether tools for it look thin or crowded (from the launch and
incumbent signals).

## Launches

Product Hunt's feed is Atom; read it with a direct request, since readers
return an empty page:

```bash
curl -sS --max-time 30 -A "Mozilla/5.0" "https://www.producthunt.com/feed"
```

Use YC Launches, Show HN (`https://hn.algolia.com/api/v1/search?tags=show_hn&query=QUERY`)
and GitHub (`gh search repos "QUERY" --sort stars`) for developer tools.
Record stars and dates, and say that stars are attention, not adoption.

## Buyer pain

Communities and reviews as in [communities.md](communities.md). Named
entities make better queries than generic phrases: search for the product,
the incumbent or the post people are reacting to. In-house builds described
publicly (an engineering blog showing a company built the tool itself) are
strong pain signals and weak buying signals: they also show buyers who may
keep building.

## Incumbent moves

For each candidate, search the incumbents' changelogs and docs for the last
six months, plus open-source copies of any widely shared design:

```bash
mcporter call exa.web_search_exa query="INCUMBENT changelog FEATURE 2026" numResults=8
gh search repos "DESIGN NAME" --sort updated --limit 10
```

Open the primary changelog entry and record its date and status (shipped,
public preview, private beta, announced). This feeds the absorption check in
[scout.md](scout.md).

## SF and NYC

Start from [brief.md](brief.md). Refresh it when it is older than 60 days or
when the question is about "now":

1. Regional money: the latest Crunchbase quarterly report, AlleyWatch's last
   monthly report and Tech:NYC's last Series A post. Find the newest one from
   the site's own listing or search; never guess a report's URL from its
   name, and say when the next report is not out yet.
2. Who insiders rate: the newest Frontier List and Breakout List pages, with
   vote and respondent counts and the HQ split.
3. What is launching and hiring: YC Launches, the hiring method above.
4. Events: `luma.com/sf` and `luma.com/nyc` (read the page's embedded
   `__NEXT_DATA__` JSON with a direct request) and the Frontier List event
   host survey. Events show where people gather, not demand.
5. Write the refreshed brief to `pmf/research/brief.md` in the user's
   project, in the same shape and under about 600 words, with a new as-of
   date. Never edit the copy in this skill's folder; a newer
   `pmf/research/brief.md` takes precedence over it.
