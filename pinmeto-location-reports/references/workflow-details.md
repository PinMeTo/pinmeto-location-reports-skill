# Workflow Details

Detailed MCP tool calls for fetching PinMeTo analytics data.

## Contents

- [Fetch Location Data](#fetch-location-data)
- [Fetch Google Metrics](#fetch-google-metrics)
- [Fetch Facebook & Apple Metrics](#fetch-facebook--apple-metrics)
- [MCP Tool Reference](#mcp-tool-reference)

---

## Fetch Location Data

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

---

## Fetch Google Metrics

### Google Insights (views, searches, actions)

```
Tool: pinmeto_get_google_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED - start date)
- to: "YYYY-MM-DD" (REQUIRED - end date)
- aggregation: "monthly" | "quarterly" | "half_yearly" | "yearly"
- compare_with: "prior_period" (MoM/QoQ) OR "prior_year" (YoY)
- store_id: (optional - omit for all locations)
- response_format: "json" (recommended)
```

**IMPORTANT:** Both `from` and `to` are required. Never omit these parameters.

Call twice: once with `compare_with: "prior_period"` and once with `compare_with: "prior_year"` to get both comparison sets.

### Google Ratings

```
Tool: pinmeto_get_google_ratings
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- aggregation: "monthly" | "quarterly" | "half_yearly" | "yearly"
- store_id: (optional)

Returns: averageRating, totalReviews, distribution (1-5 stars)
```

### Google Keywords

```
Tool: pinmeto_get_google_keywords
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- limit: 10 (monthly) | 15 (quarterly) | 20 (half-yearly) | 25 (yearly)
- store_id: (optional)

Process results with keyword classification rules.
```

### Google Reviews (for sentiment context)

```
Tool: pinmeto_get_google_reviews
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- store_id: (optional)
- limit: 50 (recent reviews for sentiment summary)
```

---

## Fetch Facebook & Apple Metrics

### Facebook Insights

```
Tool: pinmeto_get_facebook_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- aggregation: "monthly" | "quarterly" | "half_yearly" | "yearly"
- compare_with: "prior_period" | "prior_year"
- store_id: (optional)
```

### Facebook Brandpage Insights (all pages)

```
Tool: pinmeto_get_facebook_brandpage_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
```

### Facebook Ratings

```
Tool: pinmeto_get_facebook_ratings
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- aggregation: "monthly" | "quarterly" | "half_yearly" | "yearly"
- store_id: (optional)
```

### Apple Maps Insights

```
Tool: pinmeto_get_apple_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- aggregation: "monthly" | "quarterly" | "half_yearly" | "yearly"
- store_id: (optional)
```

---

## MCP Tool Reference

### MCP Server

Server name: `pinmeto-location-mcp`

Use this prefix for fully qualified tool references if needed.

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
