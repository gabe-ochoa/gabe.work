# Guiding principles — gabe.work

The rules this site is built on. Read before changing anything. When a change
fights a principle, the principle wins, or we change the principle on purpose.

## 1. Purpose

This is a professional career hub. One job: show who Gabe is as an engineering
leader and the work he's done. It is not a personal blog, an art portfolio, a
shop, or a link-in-bio. Those live elsewhere. Writing in particular gets its
own site: the old blog is archived at `/how/` for inbound links only. Keep
this one focused.

The reader is usually a recruiter, a hiring manager, a peer, or someone about to
take a meeting with Gabe. They have two minutes. Earn them.

## 2. Voice

Canonical spec: `dotfiles/agent/guides/personal/writing-voice.md`. Calibrated
from Gabe's blog (gabe.work/how). Read it before writing copy. The short version:

- Narrative sentences that carry their own reasoning, with a short line to land
  the point. Not a wall of clipped fragments. Uniform sentence length is the
  single clearest sign a model wrote the copy, so vary it on purpose: a 4-word
  sentence should sit next to a 35-word one. Specific numbers. No hedging.
- Lead with the real noun, not the adjective. "Teams that ship," not
  "high-performing teams." Show the trait, don't label it.
- No corporate jargon. No "synergies," no "passionate about leveraging."
- Never use emdashes. Use periods, commas, or colons.
- No labels above headings or decorative slogans. Supporting text and captions
  must add facts, context, or instructions the reader needs. Remove repeated
  promises and summaries that only restate the heading or nearby copy. Keep
  functional navigation, source labels, demo instructions, and useful alt text.
  Run `voice-lint` on extracted prose, then review the rendered page for
  repetition the lint cannot judge.
- Lead with outcomes, not responsibilities. "Cut deploy time from 1.5 hours to
  5 minutes," not "responsible for deployment tooling."
- Every claim is true, defensible, and Gabe's to publish. If a number can't be
  backed up, cut it. If it's an employer's internal figure (dollars, revenue,
  growth rates) and it isn't in their public record, fuzz it to a magnitude
  ("seven figures", "multi-million") or get sign-off. Ratios and timelines
  ("2x load", "under 4 weeks") are safer than absolutes.
- **Never name an internal system or project.** This is the hard line, tighter
  than the numbers rule above. Codenames and pre-launch project names do not go
  on the site in any form. Describe the thing instead: "an in-house key-value
  database," never the codename. Verify before assuming a product name is
  public, because some ship under a different name than they were built under.
  Check the employer's own product pages and docs, not your memory.
- No team or engineer counts for Gabe's current org. They are internal
  specifics and they pull attention from the narrative. Some ambiguity helps.
  Describe what the org runs instead. (Gabe, 2026-11-18.)
- What is safe to be specific about: performance and cost characteristics
  ("2x load in under 10 minutes", "30% lower cost"), headcounts and org shape for past roles,
  interview counts, and timelines. Be concrete with these. The line is names and
  unfuzzed money, not specificity itself.

## 3. Content rules

- The résumé (`Readme.md` in the `gabe-ochoa/resume` repo) is the source of
  truth for facts. The site is a sharper, scannable cut of it, not a fork.
  When the résumé changes, reconcile the site.
- Reverse-chronological experience. Most recent first.
- Each role is the company, the dates, the title, then a short prose summary,
  2 to 3 sentences carrying the strongest numbers. No bullet walls on the site. Depth lives in the PDF.
- No stat-card grid. It reads as an AI template. The numbers live inside the
  Work summaries where they have context.
- Keep the PDF résumé current and linked. It is the one download that matters.

## 4. Design

Redesigned November 2026 because the previous look (off-white paper, grey
text, orange links, serif headings over sans body) read as agent-made.

- The page is set like an engineer's computation pad, which is what a
  mechanical engineer does their thinking on: green-tinted paper, a ruled left
  margin, DIN lettering for names and labels, a book serif for the prose. The
  reference is real and it is Gabe's. Keep it subtle. No grid under the text,
  no fake title blocks, no drafting props.
- Homepage layout: the name is the masthead. Section labels sit in the ruled
  margin and the content sits to its right (about 42rem). On a phone the margin
  collapses and labels sit above their content. Inner pages keep one 42rem column.
- Still a document, not a landing page. No hero art, no buttons, no card
  grids, no sticky chrome.
- One accent color (`--accent`, pad green). It rules lines and underlines
  links. Body text and links stay ink-colored. Never two accents.
- DIN for display (`--font-display`), serif for text (`--font-text`), mono
  only for code. Dates are DIN with tabular figures, not mono.
- System fonts only. No web-font network request. The stacks name the DIN and
  serif each platform ships (DIN Alternate and Charter on Apple, Bahnschrift and
  Sitka on Windows), so check a fallback platform before changing them.
- Respect `prefers-color-scheme`. Light and dark must both look deliberate.
- The page should look finished on a phone first. Then scale up.
- Favicon, app icons, and `assets/og.png` are rendered from the same palette
  and type. Regenerate them if either changes.

## 5. Technical constraints

- **Static and zero-dependency.** Plain HTML and CSS. No framework, no bundler,
  no npm. The *served* site has zero dependencies and zero runtime build.
- **One sanctioned build step: the retired "How" archive.** `build.py` maintains
  the archived blog pages and their redirect stubs. It is pure Python stdlib, no
  install, no network, and its output is plain static HTML committed to the repo.
  No new posts get published here; new writing goes to a separate site, and once
  it exists the archive pages become redirects and this build goes away. Don't
  add a second build or any dependency. If a change to the main pages needs a
  build, it's the wrong change.
- **No JavaScript** unless it earns its place. The site works fully without it.
  Default to none. The one sanctioned exception: a tiny inline script that
  reassembles the email address so scrapers can't harvest it from source. It
  degrades to a readable `<noscript>` fallback. Don't strip it. Don't add a
  second script without a reason this good.
- **The email never appears as plain text in the served HTML.** No `mailto:` in
  source, none in the JSON-LD. Keep it that way.
- **No third-party requests.** No CDN fonts, no analytics that phone home, no
  trackers, no external scripts. The page loads from its own origin only. The
  one exception: analytics is self-hosted Plausible on Gabe's own
  infrastructure (`analytics.1365prospect.nyc`). Different hostname, same
  owner, no third party sees the data. Nothing else gets this exception.
- Fast: the whole page is a few KB. Keep it that way. Optimize images before
  adding them.
- Accessible: semantic HTML, real landmarks, alt text, visible focus states,
  AA contrast in both themes, keyboard-navigable.

## 6. Growth

- Default answer to "should we add a page/section/feature" is no. The strength
  of this site is restraint.
- Good reasons to grow: a detailed case study for a flagship project. Each new
  thing must carry its weight and follow every principle above.
- **The "How" blog is retired.** The pages at `/how/` stay served so old links
  keep working, but they are noindexed, out of the nav, and out of the sitemap.
  New writing belongs on a separate site, not here. When that site exists, the
  archive pages become redirect stubs to it and `posts/` moves out of this repo.
- One page is a feature, not a limitation. Stay single-page until there's a real
  reason not to.

## 7. The bar

Before shipping a change, ask: does this make the work clearer to someone with
two minutes, or just busier? Ship the first. Cut the second.

## 8. Personal AI system stories (October 2026)

Gabe authorized /ai/ as a place to explain personal tools and agent workflows
to friends. These illustrated system stories are a deliberate exception to
the career-only and single-page scope. The retired /how/ archive stays retired.

Small, dependency-free local scripts may power these demos. Reading the stories
must still work without JavaScript. Demos use fictional data and clearly label
preset model responses. They do not access private accounts, call models or
execute real operations. Keep the existing typography, themes and accessibility
requirements. A dedicated homepage index and navigation link make these stories easy to find.
Keep the career introduction focused.
