# Companies, hiring and market data

These sources can show budgets, alternatives, staffing needs and operating
constraints. They supplement buyer evidence. A job opening or repository
star is not proof that someone will pay for this product. Record the source
and the conclusion separately inside `pmf/research/`.

## GitHub

Use a configured GitHub connector or the authenticated gh CLI:

```bash
gh search repos "QUERY" --sort stars --limit 10
gh repo view OWNER/REPO
gh issue list --repo OWNER/REPO --state open --limit 20
gh issue view ISSUE_NUMBER --repo OWNER/REPO
```

For a software idea, inspect alternatives and recent issue discussions.
Verify whether a complaint affects the current version and whether it was
resolved. Fall back to public repository, release and issue pages if the
connector is unavailable. Research uses read commands only.

## LinkedIn

A configured connector can inspect public company and hiring evidence.
For a matching mcporter backend:

```bash
mcporter call linkedin.get_company_profile company_name="COMPANY" sections="posts,jobs"
mcporter call linkedin.search_jobs keywords="ROLE" location="REGION" max_pages=2
```

Check the registered schema first. Use public company and job pages through
the normal reader when the connector cannot access them. Do not start a
login flow or gather private profiles merely to fill a market report.

## Boss Zhipin

Use only an already configured boss CLI and an authorized browser session.
Verify the intended session is logged in; a local session-store status does
not prove the attached browser can read jobs. Discover flags with
`boss --help` and `boss search --help`. For a configured local endpoint:

```bash
boss --browser-source existing-browser --cdp-url http://localhost:9222 search "ROLE" --city CITY --page 1
```

The endpoint must be local and approved by the host's browser policy. Do not
launch or attach a different browser when the host requires its own preview.
Stop on `AUTH_EXPIRED`, `ACCOUNT_RISK` or `ENVIRONMENT_RISK`; do not refresh
tokens or retry risk errors. Treat challenges and missing access as coverage
gaps, not as a lack of jobs. Research never sends greetings or applications.

## Xueqiu

For a ready adapter and an authorized session:

```bash
opencli xueqiu whoami -f yaml
opencli xueqiu search "COMPANY" -f yaml
opencli xueqiu stock SYMBOL -f yaml
opencli xueqiu hot -f yaml
```

Require actual names, symbols or content, not only a successful status. A
bad-session response is not proof that a stock does not exist. If identity
works but quotes fail, report a data or adapter failure. Use issuer reports
and official exchange sources as a fallback. Timestamp quotes and note any
delay. Discussion sentiment does not establish this idea's unit economics.
