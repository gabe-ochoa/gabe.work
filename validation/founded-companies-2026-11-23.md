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

## Web One description follow-up

Added Gabe's supplied description: buying, renting, and selling IPv4 addresses
like real estate. This adds no dates, financial results or market claims.

- Projects prose: voice-lint 100/100, no findings; git diff --check passed.
- site-snap at 1440px and 390px in light and dark: zero errors; the same
  existing mobile Work navigation tap-target warning remains.
- Visually reviewed exact Projects screenshots in all four combinations.
  Copy wraps cleanly and the existing visual identity is preserved.
- Rendered desktop and mobile decorative-copy deletion pass: no deletion
  needed. The new sentence explains the business, and all remaining
  supporting copy keeps the factual purpose recorded above.
- Resume PDF remains byte-for-byte unchanged.
- Screenshots: /tmp/gabe-work-web-one-description/projects-*.png.

## Kinoko business description follow-up

Replaced the Kinoko implementation details with "a video chat service for older
adults." This preserves the existing product purpose and audience while removing
the tech stack at Gabe's request. Web One and the resume are unchanged.

- Projects prose: voice-lint 100/100, no findings; git diff --check passed.
- site-snap at 1440px and 390px in light and dark: zero errors; the existing
  mobile Work navigation tap-target warning remains.
- Reviewed exact Projects screenshots in all four combinations: no clipping,
  clean wrapping, and existing typography, colors and layout preserved.
- Rendered desktop and mobile deletion pass: removed WebRTC, Go, TypeScript,
  Postgres, Raspberry Pi kiosk and peer-to-peer implementation details.
  Remaining copy identifies founder roles, businesses and their audiences.
- Resume PDF still matches HEAD byte for byte.
- Screenshots: /tmp/gabe-work-kinoko-business/projects-*.png.
