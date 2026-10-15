# SF and NYC AI brief

As of 2026-10-15. Stale after 2026-12-14 (60 days). A newer
`pmf/research/brief.md` in the user's project replaces this file; refresh as
[signals.md](signals.md) describes. Labels: F fact, I inference, S
speculation. "Capital" means money raised, "traction" means customers,
revenue, usage or a shipped product in use.

## Money

- F: North America drew $92B in Q3 2026 seed to growth, about two-thirds to
  AI; Cognition raised $2B; Stripe bought OpenRouter and Nvidia bought
  Hugging Face. [Crunchbase, Q3 2026](https://news.crunchbase.com/venture/q3-2026-north-america-startup-funding-falls-ai-exits-data/)
- F: NYC raised $837.9M over 34 deals in August 2026, its lightest month of
  the year; AI-native companies were in at least 17 of the 34.
  [AlleyWatch, 2026-09-02](https://www.alleywatch.com/2026/09/the-august-2026-new-york-venture-capital-funding-report/)
- F: 17 NYC Series A rounds in September 2026 totalled $405M: 41% to AI,
  enterprise, legal and automation, 32% to fintech and payments
  infrastructure. [Tech:NYC, 2026-10-06](https://www.blog.technyc.org/news/series-a-september-2026)

## Who builds what

| | San Francisco | New York |
| --- | --- | --- |
| Clusters (F) | labs and neolabs, RL environments and data, inference and sandboxes, agent infrastructure, coding agents | AI for regulated and vertical work: legal, finance, health, supply chain; stablecoin rails |
| Insider lists (F) | 45 of 92 Breakout List picks; about 50 of the RL-environment list mentions ([Breakout](https://breakoutlist.com/), 2026-09; [Pavlov's](https://pavlovslist.com/), 2026-01) | 20 of 92 Breakout picks; about 13 RL-environment mentions |
| Recent rounds (F, self-reported) | agent seeds of $4M to $10M in October 2026: Replicas, Monid, Uvi, Harbor | Melius $20M (agents for creative work, [TechCrunch, 2026-10-06](https://techcrunch.com/2026/10/06/ex-ramp-engineers-raise-20m-for-platform-melius-after-scrapping-their-first-product/)); Fragment $12M; Modal $750M Series D ([AlleyWatch, 2026-10-14](https://www.alleywatch.com/2026/10/the-alleywatch-startup-daily-funding-report-10-14-2026/)) |
| Buyer (I) | engineering teams and labs, buying speed and capability | enterprises with auditors, buying control and proof |

## Traction versus hype

- Traction (F): agent code volume is real and measured. Anthropic went from
  about 2,500 to over 30,000 merged changes a day between May and September
  2026 ([Anthropic, 2026-10-13](https://www.anthropic.com/engineering/redesigning-source-control));
  GitHub saw 7.38B commits in September 2026, five times a year earlier
  ([GitHub, 2026-10-06](https://github.blog/engineering/architecture-optimization/building-git-infrastructure-for-agent-scale-development/)).
- Capital, not yet traction (I): most agent-infrastructure seeds above
  disclose no customers or revenue.
- Hype flags (F): Tech Week recaps, recruiter threads and launch-day posts
  are promotional; vendor-run benchmarks measure the vendor's own product.

## Platforms absorbing agent tooling (dated)

Incumbents ship fast in this space; check these before calling a gap open.

- GitHub: Copilot code review can approve pull requests, counting toward
  required approvals, per path, public preview
  ([changelog, 2026-09-01](https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests/)).
- GitLab: server-side repository access for agents, a lifecycle context
  graph, and audit and approval for agent actions, in beta
  ([press release, 2026-06-10](https://about.gitlab.com/press/releases/2026-06-10-gitlab-announces-new-capabilities-to-give-enterprises-speed-control-at-agentic-scale/)).
- Cursor: Origin, a Git host for agents built from Graphite, with 20+
  integrations as of 2026-10-13 ([Cursor on X](https://x.com/i/status/2110075611633074295)).
- Entire: agent session capture per commit, and a distributed Git network
  preview ([Entire, 2026-07-08](https://entire.io/news/entire-launches-distributed-git-network-for-the-agent-era)).

## What companies hire for

Distinct companies with matching job titles on jobs.a16z.com, 2026-10-15
(floors; the board caps results):

| problem | companies | examples |
| --- | --- | --- |
| agent deployment, forward deployed | 29 | Decagon, Hebbia, Hippocratic AI, OpenAI |
| developer productivity, build, CI | 18 | Cursor, OpenAI, Sprig, Harvey, Braintrust |
| RL environments, post-training | 15 | Cognition, Mistral, Thinking Machines, Harvey |
| evals, agent quality | 14 | Cursor, Mistral, Exa, Abridge, Vals AI |
| identity and access | 8 | Applied Intuition, Harvey, Kong, Valon |
| AI governance, GRC, audit | 8 | Akasa, Decagon, OpenAI, SentiLink |
| agent and AI security | 5 | Cursor, OpenAI, Deel |

HN Who is hiring (October 2026, 393 comments) agrees on direction: agents
71, CI 43, MCP 24, evals 19; "merge queue" 0, "provenance" 0
([thread](https://news.ycombinator.com/item?id=49922569)).

## Dates to know

- a16z speedrun SR008 applications close 2026-11-01
  ([speedrun on X, 2026-10-12](https://x.com/i/status/2109669988571443234)).
