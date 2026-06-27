#!/usr/bin/env python3
"""
build.py · the "How" blog generator for gabe.work.

Zero dependencies. Pure Python 3 stdlib. No pip install, no node, no network.
Reads markdown posts from posts/*.md and writes static HTML into how/, plus an
RSS feed and a sitemap. The served site stays pure static HTML/CSS.

Run it:
    python3 build.py            # build published posts
    python3 build.py --drafts   # also build posts marked draft: true

The markdown converter is a deliberate, small subset suited to prose (see
posts/README.md). It does NOT do smart-quote or emdash conversion: literal text
passes through unchanged, which keeps the no-emdash rule intact.
"""

import os
import re
import sys
import glob
import html
from datetime import datetime

# ---- config ----------------------------------------------------------------
SITE_URL = "https://gabe.work"
BLOG_BASE = "/how"          # URL path for the blog
OUT_DIR = "how"             # output directory (mirrors BLOG_BASE)
AUTHOR = "Gabe Ochoa"
BLOG_TITLE = "How"
BLOG_TAGLINE = "An archive of writing on building things: the decisions, the dead ends, and what shipped."

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
RFC822_M = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
RFC822_D = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ---- markdown subset -------------------------------------------------------
def _inline(text):
    """Render inline markdown. text is raw (unescaped) markdown."""
    # 1) pull code spans out so nothing else touches them
    spans = []

    def _stash(m):
        spans.append(html.escape(m.group(1)))
        return "\x00%d\x00" % (len(spans) - 1)

    text = re.sub(r"`([^`]+)`", _stash, text)

    # 2) escape the rest of the text
    text = html.escape(text, quote=False)

    # 3) images before links (overlapping syntax)
    text = re.sub(r"!\[([^\]]*)\]\(((?:[^()\s]|\([^()\s]*\))+)\)",
                  r'<img src="\2" alt="\1" loading="lazy">', text)
    # 4) links
    text = re.sub(r"\[([^\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)",
                  r'<a href="\2">\1</a>', text)
    # 5) bold then italic
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", text)

    # 6) restore code spans
    text = re.sub(r"\x00(\d+)\x00", lambda m: "<code>%s</code>" % spans[int(m.group(1))], text)
    return text


def md_to_html(md):
    """Convert a markdown body (the deliberate prose subset) to HTML."""
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # fenced code block
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            cls = ' class="language-%s"' % html.escape(lang) if lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (cls, html.escape("\n".join(buf))))
            continue

        # blank line
        if line.strip() == "":
            i += 1
            continue

        # horizontal rule
        if re.match(r"^\s*(---|\*\*\*|___)\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # heading (downshifted by one: '#' -> h2, so the page keeps one h1)
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = min(len(m.group(1)) + 1, 6)
            out.append("<h%d>%s</h%d>" % (level, _inline(m.group(2).strip()), level))
            i += 1
            continue

        # blockquote
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % _inline(" ".join(buf).strip()))
            continue

        # unordered list
        if re.match(r"^\s*[-*+]\s+", line):
            buf = []
            while i < n and re.match(r"^\s*[-*+]\s+", lines[i]):
                buf.append(_inline(re.sub(r"^\s*[-*+]\s+", "", lines[i])))
                i += 1
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in buf))
            continue

        # ordered list
        if re.match(r"^\s*\d+\.\s+", line):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append(_inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % x for x in buf))
            continue

        # paragraph (gather consecutive non-blank, non-special lines)
        buf = []
        while i < n and lines[i].strip() != "" and not re.match(
                r"^\s*(```|#{1,6}\s|>|[-*+]\s|\d+\.\s|---|\*\*\*|___)", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % _inline(" ".join(buf)))

    return "\n".join(out)


# ---- frontmatter -----------------------------------------------------------
def parse_post(path):
    raw = open(path, encoding="utf-8").read()
    meta = {}
    body = raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            block = raw[3:end].strip()
            body = raw[end + 4:].lstrip("\n")
            for ln in block.split("\n"):
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
    slug = meta.get("slug") or os.path.splitext(os.path.basename(path))[0]
    slug = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")
    meta["slug"] = slug
    meta["draft"] = str(meta.get("draft", "")).lower() in ("true", "yes", "1")
    meta["redirect_from"] = [x.strip() for x in meta.get("redirect_from", "").split(",") if x.strip()]
    meta["body_html"] = md_to_html(body)
    # date
    d = meta.get("date", "")
    try:
        meta["dt"] = datetime.strptime(d, "%Y-%m-%d")
    except ValueError:
        meta["dt"] = None
    return meta


def human_date(dt):
    return "%s %d, %d" % (MONTHS[dt.month], dt.day, dt.year) if dt else ""


def rfc822(dt):
    return "%s, %02d %s %d 00:00:00 +0000" % (
        RFC822_D[dt.weekday()], dt.day, RFC822_M[dt.month], dt.year)


# ---- templates -------------------------------------------------------------
NAV = '''  <header class="site-header">
    <nav class="nav" aria-label="Primary">
      <a class="nav__brand" href="/">Gabe&nbsp;Ochoa</a>
      <ul class="nav__links">
        <li><a href="/#about">About</a></li>
        <li><a href="/#experience">Experience</a></li>
        <li><a href="{blog}/">How</a></li>
        <li><a href="/#contact">Contact</a></li>
        <li><a class="nav__resume" href="/assets/gabe-ochoa-resume.pdf">Résumé</a></li>
      </ul>
    </nav>
  </header>'''.replace("{blog}", BLOG_BASE)

FOOTER = '''  <footer class="site-footer">
    <p>© 2026 Gabe Ochoa · Built static, hosted on GitHub Pages.</p>
  </footer>'''


def page(title, description, canonical, body, extra_head=""):
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="author" content="Gabe Ochoa" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{site}/assets/og.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="canonical" href="{canonical}" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="/assets/favicon.ico" sizes="32x32" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <meta name="theme-color" content="#18181b" />
  <link rel="alternate" type="application/rss+xml" title="How · Gabe Ochoa" href="{blog}/feed.xml" />
  <link rel="stylesheet" href="/styles.css" />
  <script defer data-domain="gabe.work" src="https://analytics.1365prospect.nyc/js/script.js"></script>
{extra}</head>
<body>
{nav}

  <main>
{body}
  </main>

{footer}
</body>
</html>
'''.format(title=html.escape(title), desc=html.escape(description),
           canonical=canonical, site=SITE_URL, blog=BLOG_BASE,
           nav=NAV, footer=FOOTER, body=body, extra=extra_head)


def render_post(p):
    canonical = "%s%s/%s/" % (SITE_URL, BLOG_BASE, p["slug"])
    dt = p["dt"]
    iso = dt.strftime("%Y-%m-%d") if dt else ""
    body = '''    <article class="post">
      <p class="section__label"><a href="{blog}/">How</a></p>
      <h1 class="post__title">{title}</h1>
      <p class="post__meta"><time datetime="{iso}">{date}</time> · {author}</p>
      <div class="prose post__body">
{content}
      </div>
      <p class="post__back"><a href="{blog}/">← All posts</a></p>
    </article>'''.format(blog=BLOG_BASE, title=html.escape(p.get("title", "Untitled")),
                         iso=iso, date=human_date(dt), author=AUTHOR,
                         content=p["body_html"])
    return page(p.get("title", "Untitled") + " · How · Gabe Ochoa",
                p.get("description", ""), canonical, body)


def render_index(posts):
    if posts:
        items = "\n".join('''        <li class="post-list__item">
          <a class="post-list__link" href="{blog}/{slug}/">
            <span class="post-list__title">{title}</span>
            <time class="post-list__date" datetime="{iso}">{date}</time>
          </a>
          <p class="post-list__desc">{desc}</p>
        </li>'''.format(blog=BLOG_BASE, slug=p["slug"],
                        title=html.escape(p.get("title", "Untitled")),
                        iso=p["dt"].strftime("%Y-%m-%d") if p["dt"] else "",
                        date=human_date(p["dt"]),
                        desc=html.escape(p.get("description", "")))
                        for p in posts)
        listing = '      <ul class="post-list">\n%s\n      </ul>' % items
    else:
        listing = '      <p class="post-list__empty">Coming soon. First post in the works.</p>'

    body = '''    <section class="hero hero--blog">
      <p class="eyebrow">Writing</p>
      <h1 class="hero__title">How</h1>
      <p class="hero__lede">{tagline}</p>
    </section>
    <section class="section">
{listing}
      <p class="experience__footnote"><a href="{blog}/feed.xml">RSS feed</a></p>
    </section>'''.format(tagline=html.escape(BLOG_TAGLINE), listing=listing, blog=BLOG_BASE)

    return page("How · Writing by Gabe Ochoa", BLOG_TAGLINE,
                "%s%s/" % (SITE_URL, BLOG_BASE), body)


def render_feed(posts):
    items = []
    for p in posts:
        link = "%s%s/%s/" % (SITE_URL, BLOG_BASE, p["slug"])
        items.append('''  <item>
    <title>{title}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <pubDate>{pub}</pubDate>
    <description>{desc}</description>
  </item>'''.format(title=html.escape(p.get("title", "Untitled")), link=link,
                    pub=rfc822(p["dt"]) if p["dt"] else "",
                    desc=html.escape(p.get("description", ""))))
    built = rfc822(posts[0]["dt"]) if posts and posts[0]["dt"] else ""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>How · Gabe Ochoa</title>
  <link>{site}{blog}/</link>
  <description>{tagline}</description>
  <language>en-us</language>
  <lastBuildDate>{built}</lastBuildDate>
{items}
</channel>
</rss>
'''.format(site=SITE_URL, blog=BLOG_BASE, tagline=html.escape(BLOG_TAGLINE),
           built=built, items="\n".join(items))


def render_sitemap(posts):
    urls = ["%s/" % SITE_URL, "%s%s/" % (SITE_URL, BLOG_BASE)]
    urls += ["%s%s/%s/" % (SITE_URL, BLOG_BASE, p["slug"]) for p in posts]
    body = "\n".join("  <url><loc>%s</loc></url>" % u for u in urls)
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
%s
</urlset>
''' % body


def render_redirect(new_rel, canonical):
    # Static meta-refresh stub for an old URL. Relative target so it works on
    # http now and https later. Canonical points search engines at the new URL.
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            '  <meta charset="utf-8">\n'
            '  <title>Redirecting…</title>\n'
            '  <link rel="canonical" href="%s">\n'
            '  <meta name="robots" content="noindex">\n'
            '  <meta http-equiv="refresh" content="0; url=%s">\n'
            '  <script>location.replace("%s")</script>\n'
            '</head>\n<body>\n'
            '  <p>This post moved. <a href="%s">Continue to it</a>.</p>\n'
            '</body>\n</html>\n') % (canonical, new_rel, new_rel, new_rel)


def render_404():
    body = '''    <section class="hero">
      <p class="eyebrow">404</p>
      <h1 class="hero__title">That page moved on.</h1>
      <p class="hero__lede">The link is dead or never existed. The old blog lived on
      a different host, so some bookmarks won't resolve here anymore.</p>
      <div class="hero__actions">
        <a class="btn btn--primary" href="/">Home</a>
        <a class="btn" href="{blog}/">Read "How"</a>
      </div>
    </section>'''.format(blog=BLOG_BASE)
    return page("Page not found · Gabe Ochoa", "Page not found.", SITE_URL + "/404", body)


# ---- build -----------------------------------------------------------------
def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  wrote", os.path.relpath(path, ROOT))


def main():
    include_drafts = "--drafts" in sys.argv
    paths = sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")))
    posts = []
    for path in paths:
        if os.path.basename(path).lower() == "readme.md":
            continue
        p = parse_post(path)
        if p["draft"] and not include_drafts:
            print("  skip draft:", p["slug"])
            continue
        posts.append(p)

    # newest first
    posts.sort(key=lambda p: (p["dt"] or datetime.min), reverse=True)

    print("Building %d post(s)%s..." % (len(posts), " (incl. drafts)" if include_drafts else ""))
    for p in posts:
        write(os.path.join(ROOT, OUT_DIR, p["slug"], "index.html"), render_post(p))
    nredir = 0
    for p in posts:
        new_rel = "%s/%s/" % (BLOG_BASE, p["slug"])
        canonical = SITE_URL + new_rel
        for old in p["redirect_from"]:
            write(os.path.join(ROOT, old.strip("/"), "index.html"),
                  render_redirect(new_rel, canonical))
            nredir += 1
    if nredir:
        print("  wrote %d redirect stub(s)" % nredir)
    write(os.path.join(ROOT, OUT_DIR, "index.html"), render_index(posts))
    write(os.path.join(ROOT, OUT_DIR, "feed.xml"), render_feed(posts))
    write(os.path.join(ROOT, "sitemap.xml"), render_sitemap(posts))
    write(os.path.join(ROOT, "404.html"), render_404())
    print("Done.")


if __name__ == "__main__":
    main()
