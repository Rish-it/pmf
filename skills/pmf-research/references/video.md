# Video and audio evidence

Use videos and podcasts when buyers discuss the problem there. Record the
source URL, speaker, date and timestamps. Automated transcripts can contain
errors; verify a short quote against captions or audio when possible. A
creator's opinion is not a customer review. Save useful evidence and any
temporary subtitle or audio files under `pmf/research/`.

## YouTube

An installed yt-dlp can discover a few videos and fetch metadata:

```bash
yt-dlp --dump-json "ytsearch5:QUERY"
yt-dlp --dump-json "VIDEO_URL"
```

Fetch captions without downloading the video:

```bash
yt-dlp --write-sub --write-auto-sub --sub-langs "en.*" --skip-download -o "pmf/research/%(id)s" "VIDEO_URL"
```

Choose subtitle languages for the buyer's region. Read the resulting VTT
files and remove overlapping lines before counting themes. If no real
caption text arrives, try an available
`opencli youtube transcript "VIDEO_URL" -f yaml` adapter. For a reported
expired or empty caption URL, retry that adapter at most three times.
Other failures follow the normal single-retry limit.

A configured transcription connector or CLI can process a concrete public URL
or a local audio file, writing to `pmf/research/transcript.txt`. Use it only
when a provider is configured and the user has authorized the
audio transfer and any cost. Do not pass a search expression as a video URL.
Keep the selected provider; do not enable cross-provider fallback silently.
Without an authorized transcription route, mark the transcript unavailable.
Tool health alone never proves that this video's captions were retrieved.

## Bilibili

Use the bili backend for discovery and metadata:

```bash
bili search "QUERY" --type video -n 5
bili video VIDEO_ID
opencli bilibili subtitle VIDEO_ID
```

An available OpenCLI adapter can also search and read metadata. Do not use
the YouTube yt-dlp route for this platform. If no captions are accessible,
check `bili audio --help` for its output option before fetching audio; keep
files inside `pmf/research/` and use an authorized transcription provider.
If those controls are unavailable, stop at the verified metadata and public
page, and report the missing transcript.

## Xiaoyuzhou and other podcasts

Open the public episode page or RSS entry. Prefer the publisher's transcript
or show notes, clearly distinguishing them from the full episode. If only
audio exists, use its public audio URL with the configured transcription
route above. Installed platform adapters may supply a transcript; discover
their read command with help rather than assuming a fixed script path.
Do not silently add a second model call to polish text that will be quoted.
Keep the original transcript as the evidence and summaries as analysis.
