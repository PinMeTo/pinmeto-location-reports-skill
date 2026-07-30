# Workflow Details

Exact MCP tool contracts for fetching PinMeTo analytics data.

**Target server version: PinMeTo Location MCP >= 4.0.0** (12 tools). Parameter names and
enum values below are taken from the server's input schemas. They are case-sensitive and
validated with Zod.

## Contents

- [How Parameter Errors Behave](#how-parameter-errors-behave)
- [Fetch Location Data](#fetch-location-data)
- [Fetch Google Metrics](#fetch-google-metrics)
- [Fetch Facebook & Apple Metrics](#fetch-facebook--apple-metrics)
- [Response Shapes](#response-shapes)
- [MCP Tool Reference](#mcp-tool-reference)

---

## How Parameter Errors Behave

Two different failure modes, and the silent one is more dangerous:

| Mistake | Result |
|---------|--------|
| Invalid **value** for a declared param (`aggregation="half_yearly"`) | Call fails with `-32602 Invalid params` |
| Unknown **param name** (`store_id` instead of `storeId`) | Silently stripped, call succeeds with wrong scope |

A stripped `storeId` means a single-location request returns **all locations**. Nothing errors,
and the report looks plausible. Verify parameter names against the tables below rather than
guessing from the report output.

---

## Fetch Location Data

```
Tool: pinmeto_get_locations
Purpose: List locations with pagination and filtering (5-min in-memory cache)

Parameters (all optional):
- fields: array of field names to include. Valid values include:
    "_id", "type", "site", "name", "location", "locationDescriptor", "storeId",
    "address", "openHours", "isAlwaysOpen", "specialOpenHours", "permanentlyClosed",
    "openingDate", "temporarilyClosedUntil", "temporarilyClosedMessage", "contact",
    "google", "fb", "networkCategories", "networkActionLinks", "networkAttributes",
    "networkServiceItems", "networkCustomName", "shortDescription", "longDescription",
    "customData", "wifiSsid", "serviceAreas"
- limit: 1-1000 (default 50)
- offset: >= 0 (default 0)
- permanentlyClosed: boolean
- type: "location" | "serviceArea"
- city: string (case-insensitive)
- country: string (case-insensitive)
- forceRefresh: boolean (default false, bypasses the 5-min cache)
- response_format: "json" | "markdown" (default "json")
```

**There is no `city`, `country`, or `region` field.** Geography lives inside `address`, so
request `fields: ["storeId", "name", "address"]` to get city and country. There is also no
`status` field and no `filters` object: use the `permanentlyClosed` boolean instead.

For a single location:
```
Tool: pinmeto_get_location
Parameters:
- storeId: "specific-store-id"   (REQUIRED, camelCase)
- response_format: "json" | "markdown"
```

To resolve a name or partial ID the user gave ("Store #47", "the Stockholm store") into a
real `storeId` before reporting on it:
```
Tool: pinmeto_search_locations
Parameters:
- query: string (REQUIRED - matches name, storeId, locationDescriptor, street, city, country)
- limit: 1-100 (default 20)
- response_format: "json" | "markdown"
```

---

## Fetch Google Metrics

### Google Insights (impressions, clicks, calls, direction requests)

```
Tool: pinmeto_get_google_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- aggregation: "total" | "daily" | "weekly" | "monthly" | "quarterly" | "half-yearly" | "yearly"
               (default "total")
- compare_with: "none" | "prior_period" | "prior_year" (default "none")
- storeId: (optional - omit for all locations)
- response_format: "json" | "markdown" (default "json")
```

**`half-yearly` uses a hyphen, not an underscore.** `half_yearly` is rejected outright.

Call twice only when the report needs both comparison sets: once with
`compare_with="prior_period"` and once with `compare_with="prior_year"`. Default to
`prior_year` alone.

### Google Ratings (aggregate statistics)

```
Tool: pinmeto_get_google_ratings
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- storeId: (optional)
- forceRefresh: boolean (default false)
- response_format: "json" | "markdown"

Returns: averageRating, totalReviews, distribution (star level -> count)
```

**No `aggregation` and no `compare_with` parameter.** Both are silently dropped. To compare
ratings across periods, call the tool once per period and compute the delta.

A location with zero reviews in range returns `averageRating: 0` (v4.0.0 relaxed the schema
floor for this). Treat 0 as "no data", not as a real rating, and exclude it from weighted
averages.

### Google Keywords

```
Tool: pinmeto_get_google_keywords
Parameters:
- from: "YYYY-MM" (REQUIRED - month precision, NOT YYYY-MM-DD)
- to: "YYYY-MM"   (REQUIRED - month precision, NOT YYYY-MM-DD)
- storeId: (optional)
- response_format: "json" | "markdown"

Returns: data: [{ keyword, value, locationCounts }]   // "value" is the impression count
```

**Dates are `YYYY-MM`.** Passing `YYYY-MM-DD` fails the format check.

**There is no `limit` parameter.** The tool returns the full keyword set already aggregated
across locations. Sort by `value` descending and take the top N in the skill, then classify
with `keyword-classification.md`.

### Google Review Insights (sentiment and rating statistics)

Prefer this over pulling raw reviews when the report needs sentiment breakdown or
per-location rating comparison. It aggregates server-side and returns far fewer tokens.

```
Tool: pinmeto_get_google_review_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- analysisType: "summary" | "comparison" | "issues" | "trends" | "themes" (REQUIRED)
- storeIds: array of store IDs (optional - note the plural, omit for all locations)
- samplingStrategy: "full" | "representative" | "recent_weighted" (default "full")
- skipConfirmation: boolean (default false)
- minRating / maxRating: 1-5 (optional)
- forceRefresh: boolean (default false)
- response_format: "json" | "markdown"
```

**Only `summary` and `comparison` do distinct work.** `issues`, `trends`, and `themes` are
accepted but return the same payload as `summary`, flagged with
`warningCode: "UNDIFFERENTIATED_ANALYSIS_TYPE"`. The server performs **no theme extraction
and no issue clustering.**

Consequences for report data:
- `reviews.sentiment` and `reviews.averageRating` come from `analysisType: "summary"`
- `reviews.topThemes` must be derived by reading raw review text from
  `pinmeto_get_google_reviews`. It is not available from any tool.

Large datasets: >1000 matched reviews returns `requiresConfirmation: true` with a
`largeDatasetWarning`. Re-call with `skipConfirmation: true` to proceed. >10000 requires a
`samplingStrategy` of `representative` or `recent_weighted`.

### Google Reviews (individual review text)

Use for pull quotes and for deriving `topThemes`.

```
Tool: pinmeto_get_google_reviews
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- storeId: (optional)
- limit: 1-500 (default 50)
- offset: >= 0 (default 0)
- minRating / maxRating: 1-5 (optional)
- hasResponse: boolean (optional - true for responded, false for unresponded)
- forceRefresh: boolean (default false)
- response_format: "json" | "markdown"

Returns: data: [{ storeId, rating, comment, date, ownerResponse, responseDate }]
         plus totalCount, hasMore, offset, limit
```

Check `hasMore` before treating the result as the complete set.

---

## Fetch Facebook & Apple Metrics

### Facebook Insights

```
Tool: pinmeto_get_facebook_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- aggregation: same enum as Google (default "total")
- compare_with: "none" | "prior_period" | "prior_year" (default "none")
- storeId: (optional)
- response_format: "json" | "markdown"
```

### Facebook Brandpage Insights (brand-level pages)

```
Tool: pinmeto_get_facebook_brandpage_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- aggregation: same enum as Google (default "total")
- compare_with: "none" | "prior_period" | "prior_year" (default "none")
- response_format: "json" | "markdown"
```

### Facebook Ratings

```
Tool: pinmeto_get_facebook_ratings
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- storeId: (optional)
- response_format: "json" | "markdown"
```

**No `aggregation` parameter.** There is also no Facebook reviews tool: raw review text is
Google-only.

### Apple Maps Insights

```
Tool: pinmeto_get_apple_insights
Parameters:
- from: "YYYY-MM-DD" (REQUIRED)
- to: "YYYY-MM-DD" (REQUIRED)
- aggregation: same enum as Google (default "total")
- compare_with: "none" | "prior_period" | "prior_year" (default "none")
- storeId: (optional)
- response_format: "json" | "markdown"
```

Apple has no ratings, reviews, or keywords tools.

---

## Response Shapes

All insights tools (Google, Facebook, Apple) return the **same** envelope. The shape of
`insights` depends on `aggregation`.

### With `aggregation="total"` (flattened)

```json
{
  "insights": [
    { "metric": "WEBSITE_CLICKS", "value": 189, "priorValue": 155, "delta": 34, "deltaPercent": 21.9 }
  ],
  "periodRange": { "from": "2025-10-01", "to": "2025-12-31" },
  "timeAggregation": "total",
  "compareWith": "prior_year",
  "priorPeriodRange": { "from": "2024-10-01", "to": "2024-12-31" }
}
```

### With any other aggregation (time series)

```json
{
  "insights": [
    {
      "metric": "WEBSITE_CLICKS",
      "values": [
        {
          "period": "2025-10",
          "periodLabel": "October 2025",
          "value": 62,
          "priorValue": 50,
          "priorPeriod": "2024-10",
          "priorPeriodLabel": "October 2024",
          "delta": 12,
          "deltaPercent": 24.0
        }
      ]
    }
  ],
  "timeAggregation": "monthly",
  "compareWith": "prior_year"
}
```

**Key points when parsing:**

- `insights` is an **array keyed by metric name**, not an object of metric fields. Find a
  metric with `insights.find(i => i.metric === "WEBSITE_CLICKS")`.
- Comparison fields are **flat** (`priorValue`, `delta`, `deltaPercent`). There is no nested
  `comparison` object and no `.prior` field.
- `deltaPercent` is `null` when `priorValue` is 0. Render "N/A", not "0%" or "Infinity".
- Use the server's `periodLabel` ("October 2025", "Q1 2024") for chart axis labels instead of
  reconstructing them from date strings.
- There is no total-views or total-actions metric. Sum the component metrics yourself.

### Warnings and errors

Every tool can return these alongside (or instead of) data:

| Field | Meaning |
|-------|---------|
| `warning` / `warningCode` | `INCOMPLETE_DATA` when the `to` date falls inside Google's ~10-day lag |
| `error` / `errorCode` | `RATE_LIMITED`, `NOT_FOUND`, `AUTH_INVALID_CREDENTIALS`, `NETWORK_ERROR`, ... |
| `retryable` | Whether retrying can succeed |
| `comparisonError` | Comparison fetch failed; current-period data is still valid |
| `cacheInfo` | `{ cached, ageSeconds, stale }` on ratings, reviews, review insights, locations |

Read `warningCode` rather than reimplementing the lag rule. Only retry when
`retryable` is `true`: retrying an `AUTH_INVALID_CREDENTIALS` or `NOT_FOUND` wastes time and
never succeeds.

---

## MCP Tool Reference

### The 12 tools in v4.0.0

| Tool | Scope |
|------|-------|
| `pinmeto_get_locations` | All locations, paginated and filterable |
| `pinmeto_get_location` | Single location by `storeId` |
| `pinmeto_search_locations` | Lightweight search by name/ID/address |
| `pinmeto_get_google_insights` | Google metrics |
| `pinmeto_get_google_ratings` | Google rating aggregates |
| `pinmeto_get_google_reviews` | Individual Google reviews |
| `pinmeto_get_google_review_insights` | Google sentiment and rating statistics |
| `pinmeto_get_google_keywords` | Google search keywords |
| `pinmeto_get_facebook_insights` | Facebook location metrics |
| `pinmeto_get_facebook_brandpage_insights` | Facebook brand-page metrics |
| `pinmeto_get_facebook_ratings` | Facebook rating aggregates |
| `pinmeto_get_apple_insights` | Apple Maps metrics |

Verify this list against the running server with:
```bash
node scripts/check_mcp_parity.js
```

No prompts and no sampling: the prompts capability was removed in v3.0.0 and MCP Sampling in
v4.0.0. Do not expect the server to call back into the client.

### Aggregation Options

| Value | Use Case | Token Reduction |
|-------|----------|-----------------|
| `total` | Single aggregate value (server default) | Maximum |
| `daily` | Day-by-day breakdown | None |
| `weekly` | Weekly trends | ~85% |
| `monthly` | Monthly reports | ~96% |
| `quarterly` | Quarterly reports | ~98% |
| `half-yearly` | H1/H2 reports | ~99% |
| `yearly` | Annual reports | ~99.7% |

### Comparison Types

The parameter is `compare_with`. `comparison_type` is not a parameter in any version.

| Value | Returns | Use For |
|-------|---------|---------|
| `none` | Current period only (default) | Raw data |
| `prior_period` | MoM, QoQ, HoH comparison | Recent trends |
| `prior_year` | YoY comparison | Seasonal context |

Insights tools only. Ratings, reviews, and keywords tools do not accept it.
