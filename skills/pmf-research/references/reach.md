# Research access

This is PMF's fetch workflow. Use the tools already available in the current
agent. A separate skill installation is not needed. The bundled Python
calculators remain offline; the agent's search, reader and platform tools
perform the network reads.

## Capability check

Inspect available search, fetch and connector tools first. For command-line
backends, check which are on this machine in one pass:

```bash
for c in gh twitter opencli rdt xhs yt-dlp bili boss mcporter; do command -v "$c" >/dev/null && echo "ready: $c"; done
```

Start with the no-install routes below; use a listed backend only when the
needed platform is not covered by them. Use the relevant read command below
to test the actual target. An installed program, a login flag or exit code zero does
not establish that the source was read: require non-empty target content.

Without that manager, check the needed CLI's `--help` or connector schema
and try one relevant read. Backend options vary by version. Never invent a
command or install, upgrade or configure tools as a side effect of research.
If the user requests setup, resolve the package from its official registry
or repository, explain its access needs, and follow the environment's
installation policy. Continue with public sources while setup is pending.

## No-install routes

These need only `curl` and the agent's own search and fetch. Checked on
2026-10-14; a route can close at any time, so require real content as above.

| Need | Route | Reference |
| --- | --- | --- |
| Web search | Exa's hosted MCP endpoint over HTTP, no key | [web.md](web.md) |
| Any public page, Trustpilot reviews | Jina reader | [web.md](web.md) |
| iPhone app reviews | App Store customer reviews feed | [web.md](web.md) |
| Developer and B2B talk | Hacker News search API, Stack Exchange API | [communities.md](communities.md) |
| GitHub repos and issues | public REST API, 60 requests an hour | [business.md](business.md) |
| V2EX | public topic API | [communities.md](communities.md) |

Not reachable without a backend or a session the user set up: Reddit
(anonymous reads are blocked, also through readers), Twitter/X, XiaoHongShu,
Facebook, Instagram, LinkedIn beyond public pages, Bluesky search, G2
(challenge page), and YouTube or Bilibili captions. Record these as coverage
gaps; never route around a block.

Queries and URLs sent to Exa or Jina go to a third party. Send public
queries and public URLs only.

## Source routing

| Source | First usable route | Fallback | Reference |
| --- | --- | --- | --- |
| Web search | built-in search or Exa connector | another available search tool | [web.md](web.md) |
| Web pages and review sites | built-in page reader | Jina reader, then collaborative browser | [web.md](web.md) |
| RSS | public feed reader | fetch XML and read entries | [web.md](web.md) |
| GitHub | GitHub connector or gh | public repository and issue pages | [business.md](business.md) |
| Twitter/X | twitter CLI with supplied credentials | OpenCLI with an authorized session, then public search | [communities.md](communities.md) |
| Reddit | Reddit connector or OpenCLI | authenticated rdt, then public search | [communities.md](communities.md) |
| XiaoHongShu | OpenCLI | configured MCP, then existing xhs CLI | [communities.md](communities.md) |
| Facebook | OpenCLI with an authorized session | accessible public pages | [communities.md](communities.md) |
| Instagram | OpenCLI with an authorized session | accessible public profiles | [communities.md](communities.md) |
| V2EX | public topic API | public topic pages | [communities.md](communities.md) |
| YouTube | yt-dlp captions | OpenCLI transcript, then configured transcription | [video.md](video.md) |
| Bilibili | bili for discovery, OpenCLI for subtitles | public pages, then configured audio transcription | [video.md](video.md) |
| Xiaoyuzhou | public episode or RSS transcript | configured audio transcription | [video.md](video.md) |
| LinkedIn | configured LinkedIn connector | public company and job pages | [business.md](business.md) |
| Boss Zhipin | configured boss CLI and authorized browser | public job pages | [business.md](business.md) |
| Xueqiu | OpenCLI with an authorized session | official exchange or issuer sources | [business.md](business.md) |

The order applies only to ready tools. Prefer a platform's already configured
connector when it provides the needed read. Commands in the references are
examples for installed backends; use real queries and IDs from returned
results. Check help when flags differ. Do not run sample placeholders.

## Failure handling

Retry a transient read once. If it still fails, switch to a ready fallback.
For an expired YouTube caption URL, the video reference allows three tries.
Keep platform calls within published limits; stop on rate limits and record
the gap rather than sending more requests. Do not treat a login challenge,
an empty result or a stale search index as evidence of no demand.

Use only sessions the user has authorized. Do not extract browser cookies,
automate login, solve access challenges or reveal credentials in outputs.
An account or environment risk error ends that route. A tool that reads
private account content is outside this skill's public-source scope.

If the host has a collaborative browser, use its preview tools for browser
work. CLI examples do not override the host's browser or access policy.
When no route yields real content, mark the source unavailable in
`pmf/research/reach.md` and continue with reachable evidence.
