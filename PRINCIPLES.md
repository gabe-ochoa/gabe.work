# Guiding principles — gabe.work

The rules this site is built on. Read before changing anything. When a change
fights a principle, the principle wins, or we change the principle on purpose.

## 1. Purpose

This is a professional career hub. One job: show who Gabe is as an engineering
leader and the work he's done. It is not a personal blog, an art portfolio, a
shop, or a link-in-bio. Those can live elsewhere. Keep this one focused.

The reader is usually a recruiter, a hiring manager, a peer, or someone about to
take a meeting with Gabe. They have two minutes. Earn them.

## 2. Voice

- Short sentences. Specific numbers. No hedging.
- No corporate jargon. No "synergies," no "passionate about leveraging."
- Never use emdashes. Use periods, commas, or colons.
- Lead with outcomes, not responsibilities. "Scaled DSM to $5M ARR," not
  "responsible for revenue growth."
- Every claim is true and defensible. If a number can't be backed up, cut it.

## 3. Content rules

- The résumé (`Readme.md` in the `gabe-ochoa/resume` repo) is the source of
  truth for facts. The site is a sharper, scannable cut of it, not a fork.
  When the résumé changes, reconcile the site.
- Reverse-chronological experience. Most recent first.
- Trim bullets ruthlessly. 3 to 6 per role on the site. Depth lives in the PDF.
- "Selected impact" holds the four strongest, most quantified wins. If a new win
  beats one, swap it. Four cards, no more.
- Keep the PDF résumé current and linked. It is the one download that matters.

## 4. Design

- Minimal and typographic. Whitespace and hierarchy do the work, not decoration.
- One accent color (`--accent`, currently ember). Used sparingly: labels, links,
  one button, the impact stat sources. Never two accents.
- Serif for display (name, headings, stats). Sans for body. Mono for labels.
- System fonts only. No web-font network request. Fast and offline-safe.
- Respect `prefers-color-scheme`. Light and dark must both look deliberate.
- The page should look finished on a phone first. Then scale up.

## 5. Technical constraints

- **Static, zero-dependency, no build.** Plain HTML and CSS. This is a hard rule.
  No framework, no bundler, no npm. If a change needs a build step, it's the
  wrong change.
- **No JavaScript** unless it earns its place. The site works fully without it.
  Default to none.
- **No third-party requests.** No CDN fonts, no analytics that phone home, no
  trackers, no external scripts. The page loads from its own origin only.
- Fast: the whole page is a few KB. Keep it that way. Optimize images before
  adding them.
- Accessible: semantic HTML, real landmarks, alt text, visible focus states,
  AA contrast in both themes, keyboard-navigable.

## 6. Growth

- Default answer to "should we add a page/section/feature" is no. The strength
  of this site is restraint.
- Good reasons to grow: a writing/talks section if Gabe starts publishing
  regularly; a detailed case study for a flagship project. Each new thing must
  carry its weight and follow every principle above.
- One page is a feature, not a limitation. Stay single-page until there's a real
  reason not to.

## 7. The bar

Before shipping a change, ask: does this make the work clearer to someone with
two minutes, or just busier? Ship the first. Cut the second.
