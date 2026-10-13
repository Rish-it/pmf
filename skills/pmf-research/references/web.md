# Search, pages and feeds

Search for the job the buyer is trying to finish, alternatives, complaints
and the buying trigger. Include the city or language when relevant. Use
official price pages to verify costs and review pages to read buyer reports.
Search results identify URLs; open those URLs before quoting or recording a
price. Record inaccessible pages in `pmf/research/reach.md`.

## Search and page reads

Use the agent's built-in search and fetch first when available. A configured
Exa MCP backend can also search:

```bash
mcporter call exa.web_search_exa query="QUERY" numResults=5
```

For code examples, search official docs or GitHub. Check registered tools
instead of assuming an older code-context endpoint is available.

For a public page that a normal reader cannot parse, try the Jina endpoint:

```bash
curl --fail --location --max-time 30 "https://r.jina.ai/https://example.com/page"
```

Replace the sample with the actual public URL. Never send an authenticated
or private URL to a third-party reader. An error page or consent banner is
not source content. If the reader fails, use the host's collaborative
browser when available; otherwise report the failed read.

## Reviews and local businesses

For a local idea, check map listings, menus and local review pages for the
actual service area. For software, check app stores, product review sites
and public issue trackers. Read recent low ratings and mixed positive
reviews. Record counts only when visible. Keep currencies, plans and sizes
separate until there is a defensible comparison. Use the original review
URL when available, rather than a search URL.

## RSS

Fetch the publisher's feed with a page reader or a bounded HTTP read. Read
the RSS `item` or Atom `entry` title, publication date, link and description.
An installed feed reader can handle either format; no new dependency is
required merely to read XML. Follow entry links when the feed contains only
a summary. Treat episode audio as video-reference work, not as text already
read. Keep evidence and coverage notes inside `pmf/research/`.
