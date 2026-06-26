# gabe.work

Gabe Ochoa's professional site. A single-page, static, zero-dependency portfolio
hosted on GitHub Pages at [gabe.work](https://gabe.work).

## Stack

- Plain HTML + CSS. **No build step, no JS, no framework, no dependencies.**
- `index.html` — all content.
- `styles.css` — all styling (light/dark via `prefers-color-scheme`).
- `assets/` — résumé PDF, favicon, social image.
- Deployed as-is by GitHub Pages. `.nojekyll` skips Jekyll processing.

## Editing

Everything is hand-editable. There is nothing to compile or run.

- **Add or change a role:** edit the `<article class="role">` blocks in `index.html`.
- **Update a headline stat:** edit the `.impact-card` blocks.
- **Replace the résumé:** drop a new PDF at `assets/gabe-ochoa-resume.pdf`.
- **Change the look:** the design tokens (colors, fonts, spacing) are CSS custom
  properties at the top of `styles.css`. The accent color lives in `--accent`.

Preview locally by opening `index.html` in a browser, or:

```sh
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Principles

How this site should look, read, and grow is documented in
[`PRINCIPLES.md`](./PRINCIPLES.md). Read it before making changes.

## Managing with Claude

There's a `gabe-work` skill that knows how to edit content, keep the résumé in
sync, follow the principles, and deploy. Just ask Claude to update the site.

## Deploy

Push to the default branch. GitHub Pages serves the root. Custom domain
`gabe.work` is set via the `CNAME` file plus the repo's Pages settings.
