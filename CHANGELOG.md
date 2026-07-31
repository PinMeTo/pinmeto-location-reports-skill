# Changelog

All notable changes to the PinMeTo Location Analytics Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **`--period` is no longer inert.** Both generators wrote the caller's period type into the data
  dict (under two different key spellings, `period_type` and `periodType`) and never read it back.
  The report type was instead regex-guessed from the free-text `period` label, so an explicit
  `--period yearly` was discarded. An explicit type is now authoritative and selects the yearly
  three-column table layout and the highlights heading; label inference remains as a fallback.
- **Half-yearly reports were silently downgraded.** The label inference had no half-yearly branch,
  so "H1 2025" matched nothing, fell through to the quarterly layout, and lost its highlights
  heading. Added an `H1`/`H2` pattern plus a `Half-Year Highlights` label to both generators.
- **Table delta cells now carry a direction glyph.** The stat tiles drew a triangle beside every
  delta while the tables conveyed direction through colour and the +/- sign alone, leaving them a
  channel short for the readers the triangle exists for — despite the helper's own docstring
  claiming parity with the tiles. Cells are prefixed ▲/▼/– in both generators. The glyph is
  suppressed when the brand font is unavailable, since the base-14 fallback has no triangle and
  would render a black box; the signed value remains.
- **Draft watermark no longer clips.** Introduced by the Montserrat switch: at 60pt this string is
  845pt wide in Montserrat against 783pt in Helvetica, pushing it off the left edge. The size is
  now derived from the page, accounting for both the string width and its line height, since a
  rotated text block projects both onto each axis. Verified as zero ink on all four page borders
  across every page, and stable for A4 and Letter in either font.
- The PPTX watermark no longer risks wrapping to two lines: at 48pt bold the string slightly
  exceeds its 9in box, so word wrap is disabled and it overflows harmlessly instead.

### Changed

- Platform charts now span the full 495pt text column at 320pt tall, up from 450x220. Chart pages
  went from 73-79% vertical fill to 87-94% without changing the page count. Narrative pages are
  left alone deliberately: their whitespace tracks content length, and padding it would be worse
  than the gap.
- Reframed SKILL.md's period table, which presented per-period page ranges (8-15, 10-18, 12-20,
  15-25) as generator characteristics. Page count is driven by which sections have data — a
  full report runs about 9 pages, and dropping three sections yields 6 — so the ranges were not
  something the generator could honour. Documented `periodType` in the data schema.

### Fixed (earlier in this release)

- **Navy corrected to `#000050`.** The generators and reference files used `#001334`, which is
  not a PinMeTo colour. Both the Graphic Manual (May 2026) and the Brand Book specify `#000050`.
  The token is now named `NAVY` rather than `BLUE_MARINE` to match the brand's own name for it.
- **Typography now matches the documented spec.** SKILL.md claimed Montserrat headlines with
  Recursive Mono Linear body text and Arial/Georgia fallbacks. In reality `generate_pdf.py`
  hardcoded Helvetica throughout and `generate_pptx.py` set Arial, so no report had ever
  rendered in a brand typeface. Recursive Mono Linear was never a PinMeTo font at all.
- Corrected the documented Python dependencies. `generate_pdf.py` imports matplotlib at module
  level, making it a hard requirement that CLAUDE.md omitted. The asymmetry with
  `generate_pptx.py`, which degrades to text charts without matplotlib, is now documented.

### Added

- **Montserrat bundled in `assets/fonts/`** (Regular, SemiBold, Bold) under the SIL Open Font
  License. Registered with both ReportLab and matplotlib, so PDF pages and chart images share
  one typeface and reports render on-brand on machines that never installed Montserrat. A
  missing or unreadable TTF falls back to Helvetica document-wide with a warning on stderr
  rather than mixing families or aborting.
- `references/branding.md` — colours, measured contrast ratios, typography, chart tokens, logo
  rules, and tone of voice for generated narrative. Includes the Brand Book's text-on-brand
  ratios: white on Orange measures 2.0:1 and fails even the large-text floor.

### Changed

- Brand Guidelines moved out of SKILL.md into `references/branding.md`, cutting the body from
  2,094 to ~1,800 words. The generators hardcode every token, so producing a report no longer
  loads palette detail into context; it is read only when editing a generator or answering a
  brand question.
- Renamed `references/client-review.md` to `references/customer-review.md` and replaced the
  human-relationship uses of "client" throughout. The Brand Book is explicit: "We avoid the term
  'client.' We use customer or user." Technical uses ("MCP client", "client-side") are unchanged.

### Removed

- `assets/templates/` — four HTML slide templates referenced by nothing: not SKILL.md, not any
  reference file, and not either generator. They were an abandoned HTML-rendering approach
  superseded by `generate_pptx.py`, and still carried the stale `#001334`.
- Dead code in both generators, verified unreachable and confirmed behaviour-neutral (text,
  fonts, span geometry, and PPTX shape tree are byte-identical before and after):
  - `create_bar_chart` and `create_line_chart` in `generate_pdf.py`, ReportLab-graphics chart
    builders superseded by the matplotlib path. Being unreachable, they had never been updated
    to the validated chart palette and still painted bars in `PINMETO_BLUE`/`PINMETO_LIGHT_BLUE`
    — the exact combination the skill's own notes record as having failed contrast validation.
  - `get_kpi_table_style` (`generate_pdf.py`) and `set_shape_fill` (`generate_pptx.py`).
  - The `get_previous_quarter` back-compat shim in both generators. Nothing imports either
    module — both are CLI entry points — so the deprecated alias had no caller to support.
  - Orphaned imports: `HorizontalLineChart`, `VerticalBarChart`, `Pie`, `Any`, `TA_RIGHT`,
    `landscape`, `cm`, `BaseDocTemplate`, `Frame`, `PageTemplate` (`generate_pdf.py`); `nsmap`
    and `parse_xml` (`generate_pptx.py`).

## [1.1.0] - 2026-07-30

### Fixed

- **Compatibility with PinMeTo Location MCP v4.0.0.** The skill was written against v1.x/v2
  tool contracts and had been silently broken since v3.0.0. Reference files and the fetch
  script are now aligned with the v4 tool surface.
- Aggregation value `half_yearly` corrected to `half-yearly`. The underscore form is rejected
  with `-32602`, so every half-yearly report failed on its first insights call.
- `store_id` corrected to `storeId` throughout. Unknown parameter names are silently stripped
  by the server, so single-location reports were being built from all-locations data with no
  error.
- `pinmeto_get_google_keywords` now called with `YYYY-MM` instead of `YYYY-MM-DD`.
- Location `fields` now use valid enum values; `city`, `country`, and `region` are not fields
  and live inside `address`.
- Removed parameters that do not exist and were being silently dropped: `aggregation` and
  `compare_with` on ratings tools, `limit` on the keywords tool, `filters`/`status` on
  `pinmeto_get_locations`.
- `fetch_pinmeto_data.js` rewritten against the v4 response envelope. It previously read a
  pre-v3 shape and wrote reports full of zeros without ever erroring: Google metrics via
  `insight.metrics.*`, comparisons via `insight.comparison.*.prior`, uppercase Facebook keys,
  and nested keyword data were all wrong.
- Percent change against a zero or absent baseline now renders "N/A" instead of Infinity or a
  fabricated figure.
- Weighted average rating excludes locations reporting `averageRating: 0`, which v4.0.0 returns
  for a location with no reviews in range.
- Retries now respect the server's `retryable` flag. Auth failures and 404s were retried three
  times with backoff.
- MCP server path is discovered by scanning the extensions directories instead of a hardcoded
  directory name that no longer exists. Overridable with `--server` or `PINMETO_MCP_PATH`.
- `fetch_pinmeto_data.js` output now conforms to the report data schema, so it passes
  `validate_report_data.py`. It previously emitted a top-level `highlights` array and no
  `appendix`, which the bundled validator rejected.
- Corrected the metric names in `references/metrics-glossary.md`, which documented API fields
  that do not exist. Real keys are `BUSINESS_IMPRESSIONS_*`, `WEBSITE_CLICKS`,
  `BUSINESS_DIRECTION_REQUESTS`, `CALL_CLICKS` for Google and lower_snake `page_*` for
  Facebook.
- Platform metric tables now use thousands separators. A table read `2400000` on the same page
  as a chart labelled `780,000` and a KPI card reading `2.4M`.
- Fixed wrapped text overlapping itself in PDF output. Six paragraph styles set `fontSize` but
  no `leading`, so they inherited ReportLab's default of 12; a wrapped 28pt cover title
  collided with the line beneath it. Same class of overlap as 1.0.1, which only reached the
  styles that already had `leading`.
- `appendix.reportingPeriod.quarter` renamed to `period`, with `quarter` still accepted as a
  legacy alias. The rendered label is now "Period:" for every report type, instead of
  "Quarter: Full Year 2025" on yearly reports.

### Added

- `scripts/check_mcp_parity.js`: compares the connected server's tool surface, parameter names,
  enum values, and date formats against the contract the skill assumes, exiting non-zero on
  drift. Run with `npm run check-mcp`.
- `tests/parse_shapes.test.js`: 31 assertions covering v4 response parsing, with fixtures
  generated by the MCP server's own transform pipeline. Run with `npm test`.
- `references/data-schema.md`: the report data schema, extracted from SKILL.md and AGENTS.md,
  including where each field comes from and common failure modes.
- `pinmeto_get_google_review_insights` adopted for review sentiment, including large-dataset
  confirmation handling. Documents that the server performs no theme extraction, so
  `reviews.topThemes` must be derived from raw review text.
- `dataWarnings` in fetched output, recording API warnings and platforms that returned nothing,
  so data gaps are not mistaken for real declines.

### Changed

- **Redesigned the Performance Metrics tiles, tables, and charts.** Colour choices were
  validated with the dataviz skill's palette validator rather than by eye.
  - Stat tiles: label above value, value in ink instead of brand blue (text should not wear a
    data colour), a single accent rule instead of a full outline, and a row of four instead of
    a 2x2 block. A KPI carrying `max` renders a star rating, so a 4.3 shows as 4.3 / 5 with
    four filled stars and a fifth filled to exactly 30% (not rounded to a half star, which
    would overstate it). Stars use a validated amber; brand orange measures 2.3:1 on the
    tile surface.
  - Delta indicators now carry a triangle as well as a colour. The previous green/orange pair
    measured ΔE 1.8 under protanopia, meaning red-green colourblind readers could not
    distinguish a rise from a fall. The new pair measures ΔE 9.6.
  - Chart marks moved to a validated trio (`#1F7AE0`, `#E8690B`, `#5B4B8A`). The brand's own
    blue/orange/light-blue trio failed three checks: `#bbd9fa` reads gray, and both brand hues
    fall below 3:1 against a white chart surface. Brand blue remains the heading/rule accent.
  - Tables: tinted header with ink text instead of a saturated blue block, hairline row rules
    instead of a box around every cell, and change columns now coloured by direction so the
    table agrees with the tiles.
  - Bar charts: capped bar width with a gap between paired bars, only the current series
    directly labelled, and a recessive solid grid carrying the rest.
  - Category and sentiment breakdowns render as labelled horizontal bars instead of pies. Both
    distributions routinely have close values (52% vs 38%), where arc length stops being
    comparable and the reader is left matching legend swatches. This also removed a page break
    that had been orphaning the chart onto a page of its own.
- SKILL.md restructured for progressive disclosure: consolidated the three repeated copies of
  the parameter rules into one section, moved the report data schema to `references/`, and
  rewrote the frontmatter description in third person with concrete trigger phrases.
- Report generators are now invoked in place from the skill directory rather than copied into
  the working directory, which wasted context and risked drift.
- Google data-lag handling now reads the API's own `warningCode: INCOMPLETE_DATA` instead of
  reimplementing the 10-day rule.
- Removed unused npm dependencies (`chart.js`, `chartjs-node-canvas`, `pptxgenjs`). The
  generators are pure Python and the Node scripts use built-in modules only.

## [1.0.2] - 2025-01-16

### Added
- Automated release workflow via GitHub Actions
- Installation instructions in README with direct download links
- Release badges showing version and download count
- CHANGELOG.md for version tracking
- Updated publishing documentation with automated workflow

## [1.0.1] - 2025-01-12

### Fixed
- Support for yearly report period format in PDF/PPTX generators
- Text overlap and missing logo issues in PDF/PPTX generation

## [1.0.0] - 2025-01-09

### Added
- Initial release
- PDF report generation with ReportLab
- PowerPoint report generation with python-pptx
- Support for monthly, quarterly, half-yearly, and yearly reports
- Integration with PinMeTo MCP server
- Professional branding and layouts
- Chart generation for analytics data

[Unreleased]: https://github.com/PinMeTo/pinmeto-location-reports-skill/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/PinMeTo/pinmeto-location-reports-skill/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/PinMeTo/pinmeto-location-reports-skill/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/PinMeTo/pinmeto-location-reports-skill/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/tag/v1.0.0
