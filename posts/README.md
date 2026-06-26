# Writing posts for "How"

Posts live here as markdown. Run `python3 build.py` from the repo root to
generate the HTML into `how/`. Nothing is published until you build and push.

## A post looks like this

```
---
title: How we scaled Data Streams Monitoring to $5M ARR
date: 2026-06-26
description: One sentence that shows up in the list, the RSS feed, and link previews.
draft: true
---

Your first paragraph. Write like you talk. Short sentences. Concrete nouns.

## A section heading

More text.
```

## Frontmatter fields

- `title` — required. Also the page `<h1>`.
- `date` — required, `YYYY-MM-DD`. Controls ordering (newest first) and the feed.
- `description` — one line. Shows in the post list, RSS, and social previews.
- `draft` — `true` keeps it out of the published build. Omit (or `false`) to publish.
- `slug` — optional. Defaults to the filename. Sets the URL: `/how/<slug>/`.

## Supported markdown

A deliberate, small subset for prose:

- `##` to `######` headings (the post title is already the `<h1>`, so start at `##`)
- **bold** with `**` , *italic* with `*`, `inline code` with backticks
- links `[text](url)` and images `![alt](url)`
- `-` or `1.` lists (single level)
- `>` blockquotes
- fenced code blocks with triple backticks
- `---` for a horizontal rule

The converter does NOT do smart quotes or emdash substitution. What you type is
what ships, which keeps the no-emdash rule intact. Voice rules live in
`PRINCIPLES.md` and `dotfiles/agent/guides/personal/writing-voice.md`.

## Workflow

1. Draft a `.md` here (start with `draft: true`).
2. `python3 build.py --drafts` to preview drafts, or `python3 build.py` for the real build.
3. Preview locally: `python3 -m http.server 8000`, visit `http://localhost:8000/how/`.
4. When it's ready, flip `draft` off, rebuild, commit, push.
