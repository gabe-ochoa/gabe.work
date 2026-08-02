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

- **Add or change a role:** edit the `<li class="work__item">` blocks in `index.html`.
  Each role is a one-line head (org · title, dates) plus a short prose summary.
- **Replace the résumé:** drop a new PDF at `assets/gabe-ochoa-resume.pdf`.
- **Change the look:** the design tokens (colors, fonts, spacing) are CSS custom
  properties at the top of `styles.css`. The accent color lives in `--accent`.

Preview locally by opening `index.html` in a browser, or:

```sh
python3 -m http.server 8000   # then visit http://localhost:8000
```

## The retired "How" blog

The blog at `/how/` is retired. The pages stay served so old links keep
working, but they are noindexed, out of the nav, and out of the sitemap. New
writing will live on a separate site; `posts/*.md` is the migration source for
it. Once that site exists, the `/how/` pages become redirect stubs and
`posts/` plus `build.py` move out of this repo.

Until then, `build.py` (zero-dependency Python stdlib) regenerates the archive
pages, `404.html`, and `sitemap.xml`:

```sh
python3 build.py
```

The generated files are committed to the repo; GitHub Pages serves them as-is.
Rebuild and commit both the markdown source and the generated output.

## Principles

How this site should look, read, and grow is documented in
[`PRINCIPLES.md`](./PRINCIPLES.md). Read it before making changes.

## Managing with Claude

There's a `gabe-work` skill that knows how to edit content, keep the résumé in
sync, follow the principles, and deploy. Just ask Claude to update the site.

## Deploy

Push to the default branch. GitHub Pages serves the root. Custom domain
`gabe.work` is set via the `CNAME` file plus the repo's Pages settings.
