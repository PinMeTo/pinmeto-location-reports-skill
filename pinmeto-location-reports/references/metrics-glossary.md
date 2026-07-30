# Platform Metrics Glossary

Definitions for the metrics available through PinMeTo Location MCP >= 4.0.0.

The **Metric key** column is the literal string in the `metric` field of each entry in the
`insights` array. Match on it exactly: it is case-sensitive, and Google uses SCREAMING_SNAKE
while Facebook uses lower_snake.

There are no pre-summed totals. Metrics like Total Views and Total Actions are sums the skill
computes from the component metrics below.

## Contents

- [Google Business Profile Metrics](#google-business-profile-metrics)
- [Facebook Metrics](#facebook-metrics)
- [Apple Maps Metrics](#apple-maps-metrics)
- [Comparison Metrics](#comparison-metrics)
- [Aggregation Levels](#aggregation-levels)
- [Industry Benchmarks](#industry-benchmarks-reference)
- [Data Freshness Notes](#data-freshness-notes)

---

## Google Business Profile Metrics

### Impressions

Google reports impressions split by surface (Search vs Maps) and device (desktop vs mobile).
All four are separate metrics: there is no combined views metric.

| Metric | Metric key | Definition |
|--------|------------|------------|
| Desktop Search Impressions | `BUSINESS_IMPRESSIONS_DESKTOP_SEARCH` | Profile shown in Google Search on desktop |
| Mobile Search Impressions | `BUSINESS_IMPRESSIONS_MOBILE_SEARCH` | Profile shown in Google Search on mobile |
| Desktop Maps Impressions | `BUSINESS_IMPRESSIONS_DESKTOP_MAPS` | Profile shown in Google Maps on desktop |
| Mobile Maps Impressions | `BUSINESS_IMPRESSIONS_MOBILE_MAPS` | Profile shown in Google Maps on mobile |

**Derived roll-ups (computed by the skill, not returned by the API):**

| Report metric | Formula |
|---------------|---------|
| Total Views | sum of all four impression metrics |
| Search Impressions | `BUSINESS_IMPRESSIONS_DESKTOP_SEARCH + BUSINESS_IMPRESSIONS_MOBILE_SEARCH` |
| Maps Impressions | `BUSINESS_IMPRESSIONS_DESKTOP_MAPS + BUSINESS_IMPRESSIONS_MOBILE_MAPS` |
| Mobile Share | `(mobile impressions / total impressions) * 100` |

**Note:** Google's direct/discovery/branded search breakdown is **not** available through this
API. Search intent is inferred from keyword data instead: see
[keyword-classification.md](keyword-classification.md).

### Customer Actions

| Metric | Metric key | Definition |
|--------|------------|------------|
| Website Clicks | `WEBSITE_CLICKS` | Clicks on the website link in the profile |
| Direction Requests | `BUSINESS_DIRECTION_REQUESTS` | Clicks on "Get Directions" |
| Phone Calls | `CALL_CLICKS` | Clicks on the phone number |

**Derived roll-ups:**

| Report metric | Formula |
|---------------|---------|
| Total Actions | `WEBSITE_CLICKS + BUSINESS_DIRECTION_REQUESTS + CALL_CLICKS` |
| View-to-Action Rate | `(Total Actions / Total Views) * 100` |

### Ratings

From `pinmeto_get_google_ratings`. This is a separate tool with its own response shape, not
part of the insights metric list.

| Field | Definition |
|-------|------------|
| `averageRating` | Mean rating, 0.0-5.0. **0 means no reviews in range, not a real score** |
| `totalReviews` | Review count in range |
| `distribution` | Object keyed by star level as a string |

**Distribution format** (keys are bare star numbers, not `N_star`):
```json
{ "1": 5, "2": 10, "3": 25, "4": 100, "5": 360 }
```

Single-location queries return one object; multi-location queries return an array where each
entry also carries `storeId`. Locations with no reviews are omitted from the all-locations
response but return `averageRating: 0` when queried individually. Exclude those from weighted
averages.

### Review Sentiment

From `pinmeto_get_google_review_insights` with `analysisType: "summary"` or `"comparison"`.
Returns rating and sentiment statistics computed server-side.

**The server does no theme extraction.** `analysisType` values `issues`, `trends`, and
`themes` return the summary payload flagged with
`warningCode: "UNDIFFERENTIATED_ANALYSIS_TYPE"`. The report's `topThemes` must be derived by
reading raw `comment` text from `pinmeto_get_google_reviews`.

### Keywords

From `pinmeto_get_google_keywords`. Already aggregated across locations.

| Field | Definition |
|-------|------------|
| `keyword` | Search term that surfaced the business |
| `value` | Impression count. **The field is `value`, not `impressions`** |
| `locationCounts` | Number of locations this keyword surfaced for |
| Category | Assigned by the skill: Branded, Discovery, or Navigational |

## Facebook Metrics

### Page Metrics

Keys are lower_snake_case. Available from both `pinmeto_get_facebook_insights` (per location)
and `pinmeto_get_facebook_brandpage_insights` (brand-level pages).

| Metric | Metric key | Definition |
|--------|------------|------------|
| Page Impressions | `page_impressions` | Total content impressions |
| Page Reach | `page_impressions_unique` | Unique users who saw content |
| Organic Impressions | `page_impressions_organic` | Impressions from unpaid distribution |
| Organic Reach | `page_impressions_organic_unique` | Unique users reached organically |
| Paid Impressions | `page_impressions_paid` | Impressions from paid distribution |
| Paid Reach | `page_impressions_paid_unique` | Unique users reached via paid |
| Total Actions | `page_total_actions` | Actions taken on the page |
| Page Fans | `page_fans` | Total follower count |
| Fans Gained | `page_fan_adds` | New followers in period |
| Fans Lost | `page_fan_removes` | Followers lost in period |

**Derived roll-ups:**

| Report metric | Formula |
|---------------|---------|
| Net Fan Growth | `page_fan_adds - page_fan_removes` |
| Organic Share | `(page_impressions_organic / page_impressions) * 100` |

**Not available:** per-reaction, comment, share, click, or check-in breakdowns. Engagement is
only exposed as the aggregate `page_total_actions`.

### Facebook Ratings

From `pinmeto_get_facebook_ratings`. Same response shape as Google ratings
(`averageRating`, `totalReviews`, `distribution`).

**There is no Facebook reviews tool.** Individual review text is Google-only, so
Facebook cannot contribute pull quotes or themes.

## Apple Maps Metrics

From `pinmeto_get_apple_insights`. Same insights envelope as Google and Facebook.

**Apple metric keys are passed through from the PinMeTo API and are not enumerated by the MCP
server.** Do not hardcode key names for Apple. Read the actual keys from the response:

```
insights.map(i => i.metric)   // discover available Apple metrics at runtime
```

Build the Apple report section from whatever keys come back, converting each to a readable
label. Apple has no ratings, reviews, or keywords tools, so the Apple section covers visibility
and actions only.

## Comparison Metrics

Set with the `compare_with` parameter on insights tools only (`prior_period` or `prior_year`).
Ratings, reviews, and keywords tools do not accept it.

| Field | Definition |
|-------|------------|
| `value` | Current period metric value |
| `priorValue` | Comparison period metric value |
| `delta` | Absolute change (`value - priorValue`) |
| `deltaPercent` | Percentage change. **`null` when `priorValue` is 0** |
| `priorPeriod` / `priorPeriodLabel` | Prior period identifier and readable label |
| `priorPeriodRange` | Date range of the comparison period (top level of the response) |

These fields sit **flat** on each insight (when `aggregation="total"`) or on each entry of the
`values` array (any other aggregation). There is no nested `comparison` object.

Render `deltaPercent: null` as "N/A". Computing a percentage against a zero baseline yields
Infinity and prints as garbage in the report.

**Comparison Types:**
- `prior_period`: Previous equivalent period (month vs month, quarter vs quarter)
- `prior_year`: Same period from previous year

## Aggregation Levels

| Level | Granularity | Use Case |
|-------|-------------|----------|
| `total` | Single aggregate | Quick summaries |
| `daily` | Day-by-day | Detailed analysis |
| `weekly` | Week-by-week | Short-term trends |
| `monthly` | Month-by-month | Standard reporting |
| `quarterly` | Quarter-by-quarter | Business reviews |
| `half-yearly` | 6-month periods | Strategic reviews |
| `yearly` | Year-by-year | Annual reporting |

## Industry Benchmarks (Reference)

| Metric | Good | Excellent | Industry Leader |
|--------|------|-----------|-----------------|
| Average Rating | 4.0+ | 4.5+ | 4.8+ |
| View-to-Action Rate | 3%+ | 5%+ | 8%+ |
| Discovery Search % | 30%+ | 40%+ | 50%+ |
| Review Response Rate | 50%+ | 80%+ | 95%+ |

*Benchmarks vary by industry. These are general guidelines for retail/service businesses.*

## Data Freshness Notes

- **Google**: ~10-day reporting lag for most metrics
- **Facebook**: Near real-time, 1-2 day lag for some metrics
- **Apple**: Variable lag, typically 3-7 days

The Google tools detect the lag themselves. Rather than reimplementing the date rule, read the
response: `warningCode: "INCOMPLETE_DATA"` with a human-readable `warning` means the `to` date
falls inside the lag window. Surface that warning in the report's appendix `lagNote` and tell
the user which part of the period may be incomplete.

Facebook and Apple do not emit lag warnings, so judge those date ranges manually.
