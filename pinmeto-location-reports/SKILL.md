---
name: pinmeto-location-reports
description: "Generates professional PDF and PowerPoint reports from PinMeTo location analytics data. Use when requesting location performance reports, Google Business insights, Facebook metrics, Apple Maps analytics, keyword analysis, or executive summaries for multi-location brands."
---

# PinMeTo Location Analytics Reports

Generate professional, board-ready performance reports for enterprise multi-location brands using PinMeTo's analytics data.

## Quick Start

1. Confirm PinMeTo MCP server is connected
2. Parse user request for period type and date range
3. **Calculate `from` and `to` dates** (see Date Range Calculation below)
4. Fetch data using MCP tools - **ALWAYS include `from` and `to` parameters**
5. Generate PDF and/or PPTX output with PinMeTo branding

---

## ⚠️ CRITICAL: Required MCP Parameters

**ALL PinMeTo MCP tools require `from` and `to` date parameters. The server will reject calls without them.**

Every MCP tool call MUST include:
```json
{
  "from": "YYYY-MM-DD",
  "to": "YYYY-MM-DD"
}
```

**Example - Q4 2025 report:**
```json
pinmeto_get_google_insights({
  "from": "2025-10-01",
  "to": "2025-12-31",
  "aggregation": "quarterly",
  "compare_with": "prior_year"
})

pinmeto_get_google_ratings({
  "from": "2025-10-01",
  "to": "2025-12-31",
  "aggregation": "quarterly"
})

pinmeto_get_facebook_insights({
  "from": "2025-10-01",
  "to": "2025-12-31",
  "aggregation": "quarterly",
  "compare_with": "prior_year"
})
```

### Default Comparison Period

**Default to Year-over-Year (YoY) comparisons unless the user specifically requests otherwise.**

| User Request | Use `compare_with` |
|--------------|-------------------|
| "Q4 2025 report" (no comparison specified) | `"prior_year"` (YoY) |
| "Q4 2025 vs Q4 2024" | `"prior_year"` (YoY) |
| "Q4 2025 vs Q3 2025" or "QoQ comparison" | `"prior_period"` (QoQ) |
| "Compare to last month" or "MoM" | `"prior_period"` |

YoY comparisons are more meaningful for business reporting as they account for seasonality.

**Before EVERY MCP tool call, verify:**
- [ ] `from` parameter is set to start date (e.g., "2025-10-01")
- [ ] `to` parameter is set to end date (e.g., "2025-12-31")
- [ ] Both are strings in "YYYY-MM-DD" format

---

## Period Detection

Parse natural language to determine report type:

| Pattern | Report Type | Keywords |
|---------|-------------|----------|
| Monthly | 8-15 pages | "October 2024", "last month", "2024-10" |
| Quarterly | 10-18 pages | "Q3 2024", "Q1", "third quarter", "last quarter" |
| Half-Yearly | 12-20 pages | "H1 2024", "first half", "H2", "second half" |
| Yearly | 15-25 pages | "2024", "annual", "yearly", "year-end" |

### Date Range Calculation

Calculate `from` and `to` dates based on the period type. **Use these as the `from` and `to` parameters in ALL MCP calls.**

```python
# Monthly: First to last day of month
# October 2024:
from = "2024-10-01"
to = "2024-10-31"

# Quarterly: Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec
# Q4 2025:
from = "2025-10-01"
to = "2025-12-31"

# Half-Yearly: H1=Jan-Jun, H2=Jul-Dec
# H2 2025:
from = "2025-07-01"
to = "2025-12-31"

# Yearly: Full calendar year
# 2025:
from = "2025-01-01"
to = "2025-12-31"
```

**Store these dates at the start and use them for EVERY MCP tool call.**

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

**CRITICAL - Required Parameters for ALL MCP Tools:**

```
from: "YYYY-MM-DD"   # Start date (REQUIRED - never omit)
to: "YYYY-MM-DD"     # End date (REQUIRED - never omit)
```

Example for Q4 2025:
```json
{
  "from": "2025-10-01",
  "to": "2025-12-31",
  "aggregation": "quarterly",
  "compare_with": "prior_period"
}
```

**Key tips:**
- Always include both `from` and `to` dates - the MCP server will reject calls with missing dates
- Use `compare_with` (not `comparison_type`) for comparison data
- Call insights twice: once with `compare_with: "prior_period"`, once with `compare_with: "prior_year"`

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

## Data Schema for Report Generation

The PDF/PPTX generators expect data in this exact structure. **Field names must match exactly (camelCase).**

### Required Top-Level Fields

```json
{
  "companyName": "Brand Name",
  "title": "Location Analytics Report",
  "period": "Q4 2025",
  "priorPeriod": "Q3 2025",
  "dateRange": "October 1 - December 31, 2025",
  "priorDateRange": "July 1 - September 30, 2025"
}
```

### Executive Summary (Required)

The executive summary provides a narrative overview and structured highlights:

```json
"executiveSummary": {
  "narrative": "Q4 2025 demonstrated strong growth across key visibility metrics. Total views increased significantly driven by exceptional growth in desktop maps visibility (+43% QoQ, +712% YoY). Customer actions remained robust with direction requests up 17% quarter-over-quarter.",
  "highlights": [
    {
      "title": "Outstanding Maps Growth",
      "description": "Desktop maps impressions surged 712% year-over-year, indicating significantly improved local search visibility."
    },
    {
      "title": "Strong Action Growth",
      "description": "Website clicks increased 85% quarter-over-quarter, showing improved engagement and conversion potential."
    }
  ]
}
```

**Fields:**
- `narrative`: 2-3 sentence summary of the period's performance
- `highlights`: Array of key achievements, each with `title` and `description`

### KPIs Array

Each KPI **must** have a `name` field:

```json
"kpis": [
  {"name": "Total Views", "value": "6,685", "change": "+15% YoY"},
  {"name": "Customer Actions", "value": "1,531", "change": "+12%"},
  {"name": "Average Rating", "value": "3.2", "change": "No change"},
  {"name": "Total Reviews", "value": "4", "change": "+2"}
]
```

### Platform Metrics (google, facebook, apple)

Each platform section **must** have `insights` (key findings) and `metrics`. Each metric **must** have `name`, `value`, `periodChange`, and `yearChange`:

```json
"google": {
  "insights": [
    "Desktop maps views drove 60% of total impressions, up from 35% last quarter",
    "Direction requests show strong purchase intent with +17% QoQ growth",
    "Phone calls declined 3% QoQ but remain 5% above prior year levels"
  ],
  "metrics": [
    {"name": "Total Views", "value": 4200, "periodChange": "+8%", "yearChange": "+15%"},
    {"name": "Search Impressions", "value": 831, "periodChange": "+5%", "yearChange": "+18%"},
    {"name": "Website Clicks", "value": 189, "periodChange": "+12%", "yearChange": "+22%"}
  ],
  "chartData": [
    {"label": "Oct 2025", "value": 2500, "priorValue": 2300},
    {"label": "Nov 2025", "value": 2200, "priorValue": 2100}
  ]
}
```

**Key Insights Guidelines:**
- Include 2-3 insights per platform
- Focus on significant changes, trends, or notable patterns
- Reference specific metrics and percentage changes

### Keywords

```json
"keywords": {
  "insights": [
    "Branded searches account for 52% of impressions, indicating strong brand awareness",
    "Discovery keywords grew 15% YoY, showing expanding market reach",
    "Navigational searches suggest loyal customer base returning via direct search"
  ],
  "topKeywords": [
    {"keyword": "brand name", "impressions": 1973, "category": "Branded"},
    {"keyword": "service type", "impressions": 201, "category": "Discovery"}
  ],
  "categoryDistribution": [
    {"label": "Branded", "value": 85},
    {"label": "Discovery", "value": 12},
    {"label": "Navigational", "value": 3}
  ]
}
```

### Reviews

```json
"reviews": {
  "insights": [
    "Customer service consistently praised with 89 positive mentions",
    "Wait times flagged as key improvement area with 45 negative mentions",
    "Value perception strong with 56 positive mentions on pricing"
  ],
  "totalReviews": 4,
  "averageRating": 3.2,
  "ratingChange": "No change",
  "sentiment": {
    "positive": 50,
    "neutral": 25,
    "negative": 25
  },
  "topThemes": [
    {"theme": "Service quality", "mentions": 2, "sentiment": "positive"},
    {"theme": "Wait times", "mentions": 1, "sentiment": "negative"}
  ]
}
```

### Recommendations

```json
"recommendations": [
  {
    "title": "Improve Review Response Rate",
    "description": "Respond to all reviews within 24 hours to show customer engagement.",
    "impact": "Expected 10-15% improvement in customer satisfaction"
  }
]
```

### Appendix (Required)

The appendix provides data transparency and methodology documentation:

```json
"appendix": {
  "dataSources": [
    "Google Business Profile via PinMeTo API",
    "Facebook Pages via PinMeTo API",
    "Apple Maps Connect via PinMeTo API"
  ],
  "reportingPeriod": {
    "quarter": "Q4 2025",
    "dateRange": "October 1, 2025 - December 31, 2025",
    "dataFreshness": "January 9, 2026",
    "lagNote": "Google data has approximately 10-day reporting lag. Data for late December may be incomplete."
  },
  "calculationNotes": [
    "YoY (Year-over-Year) comparisons use Q4 2024 as the baseline",
    "QoQ (Quarter-over-Quarter) comparisons use Q3 2025 as the baseline",
    "Percentage changes calculated as: ((current - previous) / previous) × 100",
    "Average ratings are weighted by review count across locations",
    "Keyword categories assigned based on brand name presence and search intent"
  ],
  "locationCoverage": {
    "totalLocations": 45,
    "geographicCoverage": "12 countries (Sweden, Finland, Norway, Denmark, Germany, Netherlands, Belgium, France, UK, Spain, Portugal, Poland)",
    "locationsWithGoogleData": 45,
    "locationsWithReviews": 38
  }
}
```

**Fields:**
- `dataSources`: List of data sources used in the report
- `reportingPeriod`: Quarter, date range, data freshness date, and any lag notes
- `calculationNotes`: Methodology explanations for metrics and comparisons
- `locationCoverage`: Total locations, geographic scope, and data availability

**Critical:** If `name` field is missing from metrics, the table will show blank labels. If `periodChange`/`yearChange` are missing, columns will show "N/A".

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
