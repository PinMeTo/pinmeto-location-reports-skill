---
name: pinmeto-location-analytics
description: Generates professional PDF and PowerPoint reports from PinMeTo location analytics data. Use when requesting location performance reports, Google Business insights, Facebook metrics, Apple Maps analytics, keyword analysis, or executive summaries for multi-location brands. Supports monthly, quarterly, half-yearly, and yearly formats.
allowed-tools:
  - Read
  - Glob
  - Bash(python:*)
  - Bash(node:*)
  - Write
---

# PinMeTo Location Analytics Reports

Generate professional, board-ready performance reports for enterprise multi-location brands using PinMeTo's analytics data.

## Quick Start

1. Confirm PinMeTo MCP server is connected
2. Parse user request for period type and date range
3. Validate dates (Google has ~10-day data lag)
4. Fetch data using MCP tools
5. Generate PDF and/or PPTX output with PinMeTo branding

## Period Detection

Parse natural language to determine report type:

| Pattern | Report Type | Keywords |
|---------|-------------|----------|
| Monthly | 8-15 pages | "October 2024", "last month", "2024-10" |
| Quarterly | 10-18 pages | "Q3 2024", "Q1", "third quarter", "last quarter" |
| Half-Yearly | 12-20 pages | "H1 2024", "first half", "H2", "second half" |
| Yearly | 15-25 pages | "2024", "annual", "yearly", "year-end" |

### Date Range Calculation

```python
# Monthly: First to last day of month
start = "2024-10-01", end = "2024-10-31"

# Quarterly: Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec
# Q3 2024:
start = "2024-07-01", end = "2024-09-30"

# Half-Yearly: H1=Jan-Jun, H2=Jul-Dec
# H1 2024:
start = "2024-01-01", end = "2024-06-30"

# Yearly: Full calendar year
start = "2024-01-01", end = "2024-12-31"
```

## Report Generation Workflow

### Step 1: Validate Request

Check before proceeding:
- [ ] Date range is valid (end date <= today - 10 days for Google data)
- [ ] Location scope is clear (all locations vs specific store IDs)
- [ ] Output format confirmed (PDF, PPTX, or both)

**Google Data Lag Warning:** Google metrics have ~10-day reporting delay. If user requests data from the last 10 days, warn them and suggest adjusting the end date.

### Steps 2-4: Fetch Data

See [references/workflow-details.md](references/workflow-details.md) for detailed MCP tool calls:
- Location data: `pinmeto_get_locations`, `pinmeto_get_location`
- Google metrics: `pinmeto_get_google_insights`, `pinmeto_get_google_ratings`, `pinmeto_get_google_keywords`, `pinmeto_get_google_reviews`
- Facebook metrics: `pinmeto_get_facebook_insights`, `pinmeto_get_facebook_brandpage_insights`, `pinmeto_get_facebook_ratings`
- Apple Maps: `pinmeto_get_apple_insights`

**Key tip:** Call Google/Facebook insights twice (once with `prior_period`, once with `prior_year`) to get both comparison sets.

### Step 5: Process & Analyze Data

1. **Calculate Changes:** For each metric, compute:
   - Absolute change: `current - previous`
   - Percent change: `((current - previous) / previous) * 100`

2. **Classify Keywords:** Apply rules from `references/keyword-classification.md`:
   - Branded: Contains brand name
   - Discovery: Generic category searches
   - Navigational: Location-intent ("near me")

3. **Aggregate Multi-Location:** Sum totals, average ratings (weighted by review count)

4. **Generate Insights:** Identify:
   - Top performers (locations, keywords)
   - Areas needing attention (declining metrics)
   - Trends (improving/declining over time)

### Step 5.5: Validate Data

Run validation before generating report:
```bash
python scripts/validate_report_data.py report_data.json
```

Fix any validation errors before proceeding to generation.

### Step 6: Generate Report

Read the appropriate reference file for report structure:
- Monthly: `references/monthly.md`
- Quarterly: `references/quarterly.md`
- Half-Yearly: `references/half-yearly.md`
- Yearly: `references/yearly.md`

**For PDF:** Use `scripts/generate_pdf.py` patterns or generate with reportlab directly.

**For PPTX:** Use html2pptx workflow with `assets/templates/` for slide layouts.

### Step 7: Quality Check

Run through `references/qa-checklist.md` before delivering.

## Brand Guidelines

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Blue (Primary) | `#3399FF` | Headers, links, primary elements |
| Orange (Accent) | `#FF8854` | Highlights, CTAs, emphasis |
| Blue Marine (Dark) | `#001334` | Dark backgrounds, text |
| Light Blue | `#bbd9fa` | Secondary backgrounds |
| Grey | `#F2F3F4` | Light backgrounds |
| Mid Grey | `#333333` | Body text |

### Typography
- **Headlines:** Montserrat (Bold/SemiBold) - all headers and short text
- **Body Text:** Recursive Mono Linear - only for long text paragraphs
- **Fallbacks:** Arial (headlines), Georgia (body)

### Logo Usage
- Use landscape version for report headers/footers
- Use vertical version for cover pages
- Logos in `assets/logos/` (SVG and JPG formats)
- Maintain clear space around logo (minimum: logo height)
- Never stretch, recolor, or rearrange logo elements

## Reference Files

| File | Purpose |
|------|---------|
| `references/workflow-details.md` | MCP tool calls and aggregation options |
| `references/monthly.md` | Monthly report structure (8-15 pages) |
| `references/quarterly.md` | Quarterly report structure (10-18 pages) |
| `references/half-yearly.md` | Half-yearly report structure (12-20 pages) |
| `references/yearly.md` | Yearly report structure (15-25 pages) |
| `references/metrics-glossary.md` | Platform metrics definitions |
| `references/keyword-classification.md` | Keyword categorization rules |
| `references/qa-checklist.md` | Quality assurance checklist |

## Output Formats

### PDF Reports
- Multi-page document with headers/footers
- PinMeTo logo on each page
- Charts embedded as images
- Tables with brand styling
- Executive summary first, details following

### PowerPoint Presentations
- 16:9 aspect ratio (720pt x 405pt)
- Title slide with vertical logo
- Section dividers with brand colors
- Chart slides with PptxGenJS
- Recommendations slide with action items

## Example Usage

**Monthly report:**
> "Create a monthly report for October 2024"

**Quarterly report for specific location:**
> "Generate Q3 2024 report for Store #47"

**Aggregated half-yearly:**
> "Create an H1 2024 executive summary for all locations"

**Annual board presentation:**
> "Generate 2024 yearly report as PowerPoint for the board meeting"
