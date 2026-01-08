---
name: pinmeto-location-analytics
description: Generate board-ready executive reports (PDF and PowerPoint) from PinMeTo Location Analytics data. Use when users request location performance reports, multi-location brand analytics, Google Business Profile insights, Facebook page metrics, Apple Maps analytics, keyword analysis, rating/review reports, or executive summaries. Supports monthly (8-15 pages), quarterly (10-18 pages), half-yearly (12-20 pages), and yearly (15-25 pages) report formats with period-appropriate comparisons (MoM, QoQ, HoH, YoY). Requires PinMeTo Location MCP server connection.
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

### Step 2: Fetch Location Data

```
Tool: pinmeto_get_locations
Purpose: Get list of all locations with basic info

Parameters:
- fields: ["store_id", "name", "city", "country", "status"]
- filters: {"status": "active"} (optional - filter to active only)
```

For single location reports:
```
Tool: pinmeto_get_location
Parameters:
- store_id: "specific-store-id"
```

### Step 3: Fetch Google Metrics

**Google Insights (views, searches, actions):**
```
Tool: pinmeto_get_google_insights
Parameters:
- start_date: "YYYY-MM-DD"
- end_date: "YYYY-MM-DD"
- aggregation: "monthly" | "quarterly" | "half_yearly" | "yearly"
- comparison_type: "prior_period" (MoM/QoQ) OR "prior_year" (YoY)
- store_id: (optional - omit for all locations)
```

Call twice: once with `comparison_type: "prior_period"` and once with `comparison_type: "prior_year"` to get both comparison sets.

**Google Ratings:**
```
Tool: pinmeto_get_google_ratings
Parameters:
- start_date, end_date, aggregation (same as above)
- store_id: (optional)

Returns: averageRating, totalReviews, distribution (1-5 stars)
```

**Google Keywords:**
```
Tool: pinmeto_get_google_keywords
Parameters:
- start_date, end_date
- limit: 10 (monthly) | 15 (quarterly) | 20 (half-yearly) | 25 (yearly)
- store_id: (optional)

Process results with keyword classification rules.
```

**Google Reviews (for sentiment context):**
```
Tool: pinmeto_get_google_reviews
Parameters:
- start_date, end_date
- store_id: (optional)
- limit: 50 (recent reviews for sentiment summary)
```

### Step 4: Fetch Facebook & Apple Metrics

**Facebook Insights:**
```
Tool: pinmeto_get_facebook_insights
Parameters:
- start_date, end_date
- aggregation: same as Google
- comparison_type: "prior_period" | "prior_year"
- store_id: (optional)
```

**Facebook Brandpage Insights (all pages):**
```
Tool: pinmeto_get_facebook_brandpage_insights
Parameters:
- start_date, end_date
```

**Facebook Ratings:**
```
Tool: pinmeto_get_facebook_ratings
Parameters:
- start_date, end_date, aggregation
- store_id: (optional)
```

**Apple Maps Insights:**
```
Tool: pinmeto_get_apple_insights
Parameters:
- start_date, end_date
- aggregation: same as others
- store_id: (optional)
```

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

## MCP Tool Reference

### Aggregation Options

| Value | Use Case | Token Reduction |
|-------|----------|-----------------|
| `total` | Single aggregate value | Maximum |
| `daily` | Day-by-day breakdown | None |
| `weekly` | Weekly trends | ~85% |
| `monthly` | Monthly reports | ~96% |
| `quarterly` | Quarterly reports | ~98% |
| `half_yearly` | H1/H2 reports | ~99% |
| `yearly` | Annual reports | ~99.7% |

### Comparison Types

| Value | Returns | Use For |
|-------|---------|---------|
| `none` | Current period only | Raw data |
| `prior_period` | MoM, QoQ, HoH comparison | Recent trends |
| `prior_year` | YoY comparison | Seasonal context |

### Response Fields (with comparison)

When `comparison_type` is set:
- `value`: Current period metric
- `priorValue`: Comparison period metric
- `delta`: Absolute change
- `deltaPercent`: Percentage change
- `priorPeriodRange`: Date range of comparison

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
