# Privacy policy

Last updated 2026-10-15. Applies to the pmf skill pack
(https://github.com/Rish-it/pmf), published by Rishit Sharma.

## What pmf is

pmf is a set of instructions (skills) and six standard-library Python tools.
It runs inside your own coding agent, on your own machine. pmf has no
server, no account, no analytics and no telemetry. The publisher receives
nothing from your use of it.

## Data pmf handles

- **Your project files.** Every skill reads and writes only a `pmf/` folder
  in your project: your idea, research notes, numbers, test results and
  plans. These files stay on your machine. The Python tools never use the
  network.
- **Public research.** When you run `pmf-research`, your agent reads public
  web pages and public posts. It may record public names, handles, links
  and short quotes from public posts in `pmf/research/` (for example
  `leads.md`). It never looks up emails, phone numbers or private profiles,
  never logs in for you, and never contacts anyone.

## Services your agent may contact

Research queries and public URLs are sent by your agent to these services,
under their own terms and privacy policies:

- Exa search (`mcp.exa.ai`) and the Jina reader (`r.jina.ai`)
- Hacker News search (`hn.algolia.com`), Stack Exchange
  (`api.stackexchange.com`), V2EX (`www.v2ex.com`)
- GitHub (`api.github.com`), the Apple App Store reviews feed
  (`itunes.apple.com`), Trustpilot (through the Jina reader)
- Public pages and feeds the research reads, such as Product Hunt,
  jobs.a16z.com, Y Combinator, Crunchbase News, AlleyWatch and Tech:NYC
- Command-line tools or connectors you installed and authorised yourself
  (for example for X, Reddit or LinkedIn), only if present

pmf sends only public queries and public URLs to these services. Never
paste private data into a research request.

## Retention

The publisher retains nothing. Files in `pmf/` stay in your project until
you delete them.

## Children

pmf is not intended for users under 18.

## Contact

Questions or requests: open an issue at https://github.com/Rish-it/pmf/issues.
