---
name: pinmeto-location-reports
description: This skill should be used when the user asks to "create a quarterly report", "generate a Q4 report", "build a monthly location report", "make an annual report", "H1 report", "board presentation from our location data", or otherwise requests a PDF or PowerPoint performance report from PinMeTo location analytics. Covers Google Business Profile, Facebook, and Apple Maps metrics, keyword analysis, and review sentiment for multi-location brands. Requires the PinMeTo Location MCP server (>= 4.0.0) to be connected.
version: 1.2.0
license: Proprietary - (c) PinMeTo AB. See LICENSE.
---

# PinMeTo Location Analytics Reports

Generate professional, board-ready performance reports for enterprise multi-location brands
using PinMeTo's analytics data.

## Requirements

Requires **PinMeTo Location MCP >= 4.0.0** (12 tools). Earlier majors used different tool
names, parameters, and response shapes, and this skill's calls will fail or return wrong data
against them.

Confirm the server is connected before starting. To verify the tool surface matches what this
skill expects:
```bash
node scripts/check_mcp_parity.js
```

## Quick Start

1. Confirm the PinMeTo MCP server is connected
2. Parse the user request for period type and date range
3. Calculate `from` and `to` dates (see [Date Range Calculation](#date-range-calculation))
4. Fetch data using the MCP tools (see [MCP Call Rules](#mcp-call-rules))
5. Generate PDF and/or PPTX output with PinMeTo branding

---

## MCP Call Rules

Read [references/workflow-details.md](references/workflow-details.md) for the full parameter
contracts. These are the rules that break reports most often.

### Every insights call needs from, to, and a comparison

```json
pinmeto_get_google_insights({
  "from": "2025-10-01",
  "to": "2025-12-31",
  "aggregation": "quarterly",
  "compare_with": "prior_year"
})
```

`from` and `to` are required on every data tool. Both are strings; insights, ratings, reviews,
and review-insights tools take `YYYY-MM-DD`, **keywords take `YYYY-MM`**.

### Exact spellings that fail silently or loudly

| Correct | Wrong | Consequence if wrong |
|---------|-------|---------------------|
| `storeId` | `store_id` | **Silently returns all locations.** A single-store report gets brand-wide data |
| `half-yearly` | `half_yearly` | Call fails with `-32602` |
| `compare_with` | `comparison_type` | Comparison silently dropped, all changes read "N/A" |
| `YYYY-MM` for keywords | `YYYY-MM-DD` | Call fails validation |

Unknown parameter **names** are silently stripped; invalid **values** for a real parameter
fail loudly. The silent case is the dangerous one.

### Parameters that do not exist

- **`aggregation` and `compare_with` on ratings tools.** Ratings take only `from`, `to`,
  `storeId`, `forceRefresh`. For a rating delta, call once per period and subtract.
- **`limit` on the keywords tool.** It returns the full set; take the top N in the skill.
- **`filters` / `status` on `pinmeto_get_locations`.** Use `permanentlyClosed`, `type`,
  `city`, `country`.
- **`city` / `country` / `region` as location `fields`.** Geography is inside `address`.

### Default Comparison Period

Default to Year-over-Year unless the user asks otherwise. YoY accounts for seasonality, which
matters for retail and service brands.

| User Request | Use `compare_with` |
|--------------|-------------------|
| "Q4 2025 report" (no comparison specified) | `"prior_year"` (YoY) |
| "Q4 2025 vs Q4 2024" | `"prior_year"` (YoY) |
| "Q4 2025 vs Q3 2025" or "QoQ comparison" | `"prior_period"` (QoQ) |
| "Compare to last month" or "MoM" | `"prior_period"` |

Populating both `periodChange` and `yearChange` requires two insights calls, one per
comparison type. With a single YoY call, set `periodChange` to "N/A" rather than inventing it.

### Read the response, do not assume it

- `insights` is an array **keyed by metric name**. Comparison fields (`priorValue`, `delta`,
  `deltaPercent`) are **flat**, not nested under `comparison`.
- `deltaPercent` is `null` when the baseline is 0. Render "N/A".
- `warningCode: "INCOMPLETE_DATA"` means the range hit Google's reporting lag. Surface the
  `warning` text in the appendix rather than reimplementing the lag rule.
- Only retry when `retryable` is `true`.

---

## Period Detection

Parse natural language to determine report type:

| Report Type | Keywords |
|-------------|----------|
| Monthly | "October 2024", "last month", "2024-10" |
| Quarterly | "Q3 2024", "Q1", "third quarter", "last quarter" |
| Half-Yearly | "H1 2024", "first half", "H2", "second half" |
| Yearly | "2024", "annual", "yearly", "year-end" |

Always pass the detected type to the generators with `--period`. It is authoritative: it selects
the yearly three-column table layout (value plus YoY, no period-over-period column) and the
highlights heading. Without it the generators fall back to inferring the type from the free-text
period label, which is a guess.

**Page count is driven by the data, not the period.** Each platform, keywords, and reviews
section is emitted only when its data is present, so a report covering Google alone is far
shorter than one covering three platforms plus keywords and sentiment. A full report over all
sections runs about 9 pages. Do not promise a page count before seeing what the fetch returns.

### Date Range Calculation

Calculate `from` and `to` once, then use them for every MCP call in the report.

```python
# Monthly: first to last day of month. October 2024:
from = "2024-10-01";  to = "2024-10-31"

# Quarterly: Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec. Q4 2025:
from = "2025-10-01";  to = "2025-12-31"

# Half-Yearly: H1=Jan-Jun, H2=Jul-Dec. H2 2025:
from = "2025-07-01";  to = "2025-12-31"

# Yearly: full calendar year. 2025:
from = "2025-01-01";  to = "2025-12-31"

# Keywords only: same range at month precision. Q4 2025:
from = "2025-10";     to = "2025-12"
```

## Report Generation Workflow

### Step 1: Validate Request

- [ ] Location scope is clear (all locations vs specific store IDs)
- [ ] Output format confirmed (PDF, PPTX, or both)
- [ ] End date is not inside Google's ~10-day reporting lag

If the requested period ends within the last 10 days, warn the user that Google metrics may be
incomplete and suggest an earlier end date. The API also flags this itself with
`warningCode: "INCOMPLETE_DATA"`.

To report on a specific store the user named loosely ("Store #47", "the Stockholm one"),
resolve it to a real `storeId` with `pinmeto_search_locations` first.

### Steps 2-4: Fetch Data

Follow the fetch sequence in the period-specific reference file (see
[Reference Files](#reference-files)), which lists the calls in order with correct parameters.

Available tools:
- Locations: `pinmeto_get_locations`, `pinmeto_get_location`, `pinmeto_search_locations`
- Google: `pinmeto_get_google_insights`, `pinmeto_get_google_ratings`,
  `pinmeto_get_google_reviews`, `pinmeto_get_google_review_insights`,
  `pinmeto_get_google_keywords`
- Facebook: `pinmeto_get_facebook_insights`, `pinmeto_get_facebook_brandpage_insights`,
  `pinmeto_get_facebook_ratings`
- Apple Maps: `pinmeto_get_apple_insights`

Prefer `pinmeto_get_google_review_insights` over pulling every review when the report needs
sentiment: it aggregates server-side and costs far fewer tokens. Fetch raw reviews only for
pull quotes and theme identification.

For a scripted batch fetch of a full year:
```bash
node scripts/fetch_pinmeto_data.js --year 2025 --output report_data.json
```

### Step 5: Process & Analyze Data

1. **Calculate changes:** absolute (`current - previous`) and percent
   (`((current - previous) / previous) * 100`). Guard against a zero baseline.
2. **Sum the roll-ups:** Total Views and Total Actions are sums of component metrics, not API
   fields. See [references/metrics-glossary.md](references/metrics-glossary.md).
3. **Classify keywords** using [references/keyword-classification.md](references/keyword-classification.md).
4. **Aggregate multi-location:** sum totals, average ratings weighted by review count,
   excluding locations with no reviews.
5. **Generate insights:** top performers, declining metrics, trends.

### Step 5.5: Validate Data

```bash
python scripts/validate_report_data.py report_data.json
```

Fix all validation errors before generating. The schema is documented in
[references/data-schema.md](references/data-schema.md).

### Step 6: Generate Report

Read the period-specific reference file for report structure, then run the bundled generator
**directly from the skill directory**. Do not copy the scripts into the working directory or
rewrite them: they encode the branding and layout, and a copy will drift.

```bash
# Set once to the directory containing this SKILL.md
SKILL_DIR="/path/to/pinmeto-location-reports"

pip install reportlab python-pptx pillow matplotlib
# matplotlib is not optional in practice: generate_pdf.py imports it at module
# level, and generate_pptx.py silently degrades to text-based charts without it.

# PDF
python "$SKILL_DIR/scripts/generate_pdf.py" \
  --data report_data.json --output report.pdf --period quarterly

# PPTX
python "$SKILL_DIR/scripts/generate_pptx.py" \
  --data report_data.json --output report.pptx --period quarterly
```

`--period` accepts `monthly`, `quarterly`, `half-yearly`, or `yearly`, and takes precedence over
the period label in the data. Set `periodType` in the data JSON instead to make it self-describing.

### Step 7: Customer Review (Human-in-the-Loop)

Present a draft for review before finalizing.

**7.1 Generate a draft** with `--draft` to add a diagonal "DRAFT - PENDING REVIEW" watermark
to every page or slide:

```bash
python "$SKILL_DIR/scripts/generate_pdf.py" \
  --data report_data.json --output Brand_Q4_Report_DRAFT.pdf --period quarterly --draft
```

**7.2 Present for review** with a summary of the key data:

```
I've generated a draft Q4 2025 report with a DRAFT watermark.

File: Brand_Q4_2025_Report_DRAFT.pdf

Key data included:
- Total Views: 125,432 (+12% YoY)
- Total Actions: 8,234 (+8% YoY)
- Average Rating: 4.6 (+0.2)
- 12 locations analyzed

Note: Google data for the final 10 days of December may be incomplete.

Reply "approved" for the final version without the watermark, or tell me what to correct.
```

State any `dataWarnings` here. A platform that returned no data looks identical to a real
decline in the finished report.

**7.3 Review checklist** (full version in
[references/customer-review.md](references/customer-review.md)): executive summary accuracy, KPI
values, chart rendering, table completeness, text correctness, branding.

**7.4 Handle feedback:**
- Approved: regenerate without `--draft`
- Changes needed: update the data JSON or chart parameters, regenerate with `--draft`, repeat

### Step 8: Quality Check & Delivery

Work through [references/qa-checklist.md](references/qa-checklist.md) before delivering.

## Report Data Schema

The generators expect an exact JSON structure with camelCase field names. Full schema,
field sources, and common failures: [references/data-schema.md](references/data-schema.md).

## Brand Guidelines

Both generators hardcode the full palette, typeface, and chart tokens, so generating a report
needs none of it in context. Read [references/branding.md](references/branding.md) before editing
a generator's tokens, adding a chart type, or answering a brand question.

The four rules that get violated most often:

- **Montserrat is the only brand typeface.** It ships in `assets/fonts/`, so reports are on-brand
  on machines that never installed it. PDF embeds it; PPTX cannot, so deliver PDF when typography
  must be guaranteed.
- **Navy is `#000050`**, and it is the body ink. Not `#001334`.
- **Brand hues are not data colours.** `#3399FF` and `#FF8854` fall below the 3:1 contrast floor
  against a white chart surface. Charts use the validated tokens in `references/branding.md`.
- **Direction is never colour alone.** Every delta carries a triangle (▲ / ▼ / –) beside the
  status colour, so red-green colourblind readers can still tell a rise from a fall.

Never set body copy in white on Blue or Orange: white on Orange measures 2.0:1 and fails even
the large-text floor. Use Navy on both brand backgrounds.

## Reference Files

| File | Purpose |
|------|---------|
| `references/workflow-details.md` | MCP tool contracts, parameters, response shapes |
| `references/data-schema.md` | Report data JSON schema and field sources |
| `references/branding.md` | Colours, contrast ratios, typography, chart tokens, tone of voice |
| `references/monthly.md` | Monthly report structure (8-15 pages) |
| `references/quarterly.md` | Quarterly report structure (10-18 pages) |
| `references/half-yearly.md` | Half-yearly report structure (12-20 pages) |
| `references/yearly.md` | Yearly report structure (15-25 pages) |
| `references/metrics-glossary.md` | Metric keys and derived roll-ups |
| `references/keyword-classification.md` | Keyword categorization rules |
| `references/customer-review.md` | Customer review checklist |
| `references/qa-checklist.md` | Quality assurance checklist |

## Output Formats

### PDF Reports
- Multi-page document with headers/footers and the PinMeTo logo on each page
- Charts embedded as images, tables with brand styling
- Executive summary first, details following

### PowerPoint Presentations
- 16:9 aspect ratio (720pt x 405pt)
- Title slide with vertical logo, section dividers in brand colors
- Charts rendered as PNG images for Keynote and PowerPoint compatibility
- Recommendations slide with action items

## Example Usage

**Monthly report:**
> "Create a monthly report for October 2024"

**Quarterly report for a specific location:**
> "Generate Q3 2024 report for Store #47"

**Aggregated half-yearly:**
> "Create an H1 2024 executive summary for all locations"

**Annual board presentation:**
> "Generate 2024 yearly report as PowerPoint for the board meeting"
