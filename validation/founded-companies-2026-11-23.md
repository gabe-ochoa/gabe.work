# Founded companies website update

Date: 2026-11-23

Added Web One as founded and Kinoko Chat as cofounded in the Projects section.
Moved the existing Kinoko description into the founder paragraph so it appears
once and is separate from the Built by Experiment products. Founder attribution
comes from Gabe's request; the technical cofounder role and product description
are also present in the existing resume source. No Web One dates or business
claims were added. The resume PDF and resume source were not edited.

Validation:

- Extracted Projects prose: voice-lint 100/100, no findings.
- git diff --check passed. Resume PDF matches HEAD byte for byte.
- site-snap at 1440px and 390px in light and dark: zero errors.
  Existing warning: the Work navigation link is narrower than 40px on mobile.
- Visually reviewed the homepage and exact Projects section at both widths
  in both themes. Text wraps without clipping; existing colors, typography,
  layout and other project descriptions remain unchanged.
- Decorative-copy deletion pass on rendered desktop and mobile: removed the
  separate Kinoko list entry to avoid repeating its description. Retained the
  Built by Experiment introduction because it identifies ownership of those
  three products. The added paragraph identifies founder roles and the existing
  Kinoko product facts. No eyebrows, kickers or decorative lines were added.

Preview command: site-snap http://127.0.0.1:8013/#projects --dark --wait-ms 2500
Exact section screenshots: /tmp/gabe-work-founded-companies/projects-*.png.
Rollback: revert the website-update commit.
