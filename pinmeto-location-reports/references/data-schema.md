# Report Data Schema

The structure `generate_pdf.py` and `generate_pptx.py` expect. **Field names must match
exactly (camelCase).**

Validate before generating:
```bash
python scripts/validate_report_data.py report_data.json
```

## Contents

- [Required Top-Level Fields](#required-top-level-fields)
- [Executive Summary](#executive-summary-required)
- [KPIs](#kpis-array)
- [Platform Metrics](#platform-metrics-google-facebook-apple)
- [Keywords](#keywords)
- [Reviews](#reviews)
- [Recommendations](#recommendations)
- [Appendix](#appendix-required)
- [Common Failures](#common-failures)

---

## Required Top-Level Fields

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

## Executive Summary (Required)

Narrative overview plus structured highlights.

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

## KPIs Array

Each KPI **must** have a `name` field:

```json
"kpis": [
  {"name": "Total Views", "value": "6,685", "change": "+15% YoY"},
  {"name": "Customer Actions", "value": "1,531", "change": "+12%"},
  {"name": "Average Rating", "value": "3.2", "change": "No change"},
  {"name": "Total Reviews", "value": "4", "change": "+2"}
]
```

## Platform Metrics (google, facebook, apple)

Each platform section **must** have `insights` (key findings) and `metrics`. Each metric
**must** have `name`, `value`, `periodChange`, and `yearChange`:

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

**Mapping from the API:** none of these report metrics exist as single API fields. `Total
Views` is the sum of four Google impression metrics, `Total Actions` the sum of three. Apple
metric names are discovered from the response rather than fixed. See
[metrics-glossary.md](metrics-glossary.md).

**Use "N/A" for unavailable changes**, never a fabricated number. `periodChange` requires a
second insights call with `compare_with="prior_period"`; if only `prior_year` was fetched,
`periodChange` is "N/A". A percent change against a zero baseline is also "N/A": the API
returns `deltaPercent: null` in that case.

For `chartData.label`, use the `periodLabel` the API returns ("October 2025", "Q1 2024")
rather than reconstructing labels from dates.

## Keywords

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

The API field is `value`, not `impressions`: rename it when building this section. Compute
`categoryDistribution` over the **full** keyword set, not just the top N, or the percentages
misrepresent the mix. Categories come from
[keyword-classification.md](keyword-classification.md).

## Reviews

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

**Where each field comes from:**

| Field | Source |
|-------|--------|
| `totalReviews`, `averageRating` | `pinmeto_get_google_ratings` |
| `sentiment` | `pinmeto_get_google_review_insights` (`analysisType: "summary"`) |
| `topThemes` | Derived by reading `comment` text from `pinmeto_get_google_reviews` |
| `ratingChange` | Two ratings calls (the tool has no `compare_with`) |

**`topThemes` cannot be fetched.** The MCP server performs no theme extraction: analysis
types `themes`, `issues`, and `trends` return the summary payload flagged
`UNDIFFERENTIATED_ANALYSIS_TYPE`. Read the raw review text and identify themes, or omit the
section.

**Omit `averageRating` when `totalReviews` is 0.** The API returns `averageRating: 0` for a
location with no reviews in range, and the validator rejects a 0 rating because valid ratings
are 1.0-5.0. Also exclude those locations from the weighted brand average.

**Sentiment percentages must sum to roughly 100** (the validator allows 95-105 for rounding).

## Recommendations

```json
"recommendations": [
  {
    "title": "Improve Review Response Rate",
    "description": "Respond to all reviews within 24 hours to show customer engagement.",
    "impact": "Expected 10-15% improvement in customer satisfaction"
  }
]
```

## Appendix (Required)

Data transparency and methodology documentation.

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
- `dataSources`: List of data sources actually used. Omit platforms that returned no data.
- `reportingPeriod`: Quarter (or period label), date range, data freshness date, and lag notes
- `calculationNotes`: Methodology explanations for metrics and comparisons
- `locationCoverage`: Total locations, geographic scope, and data availability

Populate `lagNote` from the API's own `warning` field when `warningCode` is
`INCOMPLETE_DATA`, rather than restating a generic lag rule.

## Optional: dataWarnings

`fetch_pinmeto_data.js` adds a top-level `dataWarnings` array recording anything the API
flagged or any platform that returned nothing. It is not rendered in the report. Read it
before delivering: it explains gaps that would otherwise look like real declines.

```json
"dataWarnings": [
  "Data for the last 10 days may be incomplete due to Google reporting lag.",
  "Review sentiment based on 1000 of 4200 reviews (representative)."
]
```

## Common Failures

| Symptom | Cause |
|---------|-------|
| Blank row labels in metric tables | Metric missing `name` |
| Columns show "N/A" unexpectedly | Missing `periodChange` / `yearChange` |
| Validation error on rating | `averageRating` outside 1.0-5.0, usually a 0 from a no-review location |
| Sentiment validation error | Percentages do not sum to ~100 |
| Missing Key Insights section | Platform section has no `insights` array |
| Percentages that read as absurd | Percent change computed against a zero baseline |
