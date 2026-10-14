# Buyer discussions

Choose communities used by the target buyer. Search for named competitors,
alternatives, cancellations and recent buying triggers. Read the discussion
and replies before extracting objections. Separate a buyer's experience
from advertising, jokes and hearsay. Record evidence in `pmf/research/`.

## Twitter/X

If the twitter CLI is ready, use these read operations:

```bash
twitter search "QUERY" -n 10
twitter tweet URL_OR_ID
twitter user-posts @USERNAME -n 10
twitter article URL_OR_ID
```

The CLI requires explicitly supplied `TWITTER_AUTH_TOKEN` and `TWITTER_CT0`
in its child-process environment. A manager's saved credentials or doctor
check does not populate that environment. Never log the values or retrieve
them from browser storage. If search fails, retry once, then use a ready
`opencli twitter search "QUERY" -f yaml` adapter. A relevant public user's
posts or built-in search can provide limited coverage. Do not upgrade a
package during this retry chain.

## Reddit

Use a configured connector, or an authorized existing session:

```bash
opencli reddit search "QUERY" -f yaml
opencli reddit read POST_ID -f yaml
opencli reddit subreddit SUBREDDIT -f yaml
```

A configured rdt backend can use `rdt search "QUERY" --limit 10` and
`rdt read POST_ID`. Do not assume anonymous JSON endpoints or a new API
registration will work. If neither authenticated route is ready, use public
search to find readable threads and mark the coverage limit. A snippet is
not a replacement for the thread or its comments.

## XiaoHongShu

With an authorized existing session:

```bash
opencli xiaohongshu search "QUERY" -f yaml
opencli xiaohongshu note "NOTE_URL" -f yaml
opencli xiaohongshu comments NOTE_ID -f yaml
```

Keep the full URL and access token returned by search. A bare note ID can
fail even when the note exists. A configured MCP alternative offers
`xiaohongshu.check_login_status`, `xiaohongshu.search_feeds` with `keyword`,
and `xiaohongshu.get_feed_detail` with returned `feed_id` and `xsec_token`.
Check the connector schema and allow its documented startup timeout.
An existing xhs CLI can use `xhs search`, `xhs read` and `xhs comments`.
Use the returned URL or identifier format expected by that backend.
If a session is unavailable, record the gap and use accessible public
sources. Never bootstrap login or import cookies during research.

## Facebook and Instagram

Use only public content accessible through an authorized session:

```bash
opencli facebook search "QUERY" -f yaml
opencli facebook profile PAGE_NAME -f yaml
opencli instagram search "QUERY" -f yaml
opencli instagram profile USERNAME -f yaml
opencli instagram user USERNAME --limit 12 -f yaml
```

Instagram search finds accounts; select an account before reading its posts.
Do not describe it as keyword search over all posts. A groups adapter may
list accessible groups without supporting arbitrary group comments. Check
what was actually returned. Avoid private groups, personal feeds and saved
items. Login errors or rate limits end the current route.

## Hacker News and Stack Exchange

No login and no backend. Useful for software and B2B buyers:

```bash
curl --fail --max-time 30 "https://hn.algolia.com/api/v1/search?query=QUERY&hitsPerPage=20"
curl --fail --max-time 30 --compressed "https://api.stackexchange.com/2.3/search/advanced?q=QUERY&site=stackoverflow&pagesize=20"
```

Link each quote to its item page (`https://news.ycombinator.com/item?id=ID`
or the question URL), not to the API.

## V2EX

Public APIs can return a topic and its replies:

```bash
curl --fail --max-time 30 "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID"
curl --fail --max-time 30 "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1"
```

Find a relevant topic with public search or a node page first. Preserve its
canonical topic URL, author and date. Deduplicate cross-posts across all
communities. Count distinct buyers for each complaint theme, not the number
of times a phrase appears.
