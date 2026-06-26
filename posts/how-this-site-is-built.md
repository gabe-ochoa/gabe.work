---
title: How this site is built
date: 2026-06-25
description: A static site with no build for the pages and a tiny build for the writing. Here is why.
draft: true
---

This site is plain HTML and CSS. No framework. No bundler. No npm. The pages you
read are the files on disk, served straight from GitHub Pages.

That is a choice, not a limitation.

## Why no build

Most of the site is one page. A single page does not need a toolchain. The cost
of a framework is real: dependencies that rot, a build that breaks, a thing to
maintain forever. For a professional site that changes a few times a year, that
trade is bad. So the rule is simple. If a change needs a build step, it is
probably the wrong change.

## Why the blog bends that rule

Writing is different. A blog wants markdown, not hand-written HTML for every
post. So there is one small exception: a single Python file, `build.py`, that
turns markdown into HTML. No dependencies. It runs anywhere Python 3 runs.

```
python3 build.py
```

The output is still pure static HTML. The served site never gains a dependency.
The build only exists on my machine, before deploy.

## The one piece of JavaScript

There is exactly one script on the whole site. It reassembles my email address
so scrapers cannot harvest it from the source. Everything else works with
JavaScript turned off.

That is the whole system. Boring on purpose.
