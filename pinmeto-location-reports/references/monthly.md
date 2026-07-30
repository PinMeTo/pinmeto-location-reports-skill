# Monthly Location Analytics Report Structure

## Report Parameters

| Parameter | Value |
|-----------|-------|
| Page Count | 8-15 pages |
| Top Keywords | 10 |
| Comparisons | MoM (prior_period) + YoY (prior_year) |
| Aggregation | monthly |

## MCP Data Fetching Sequence

**IMPORTANT:** All MCP tools require `from` and `to` date parameters.

**DEFAULT:** Use `compare_with="prior_year"` (YoY) unless user specifically requests MoM comparison.

For December 2025: `from: "2025-12-01"`, `to: "2025-12-31"`

```
1. pinmeto_get_locations(fields=["storeId", "name", "address"])

2. pinmeto_get_google_insights(from="2025-12-01", to="2025-12-31", aggregation="monthly", compare_with="prior_year")

3. pinmeto_get_google_ratings(from="2025-12-01", to="2025-12-31")

4. pinmeto_get_google_keywords(from="2025-12", to="2025-12")   // YYYY-MM; take top 10 client-side

5. pinmeto_get_google_review_insights(from="2025-12-01", to="2025-12-31", analysisType="summary")

6. pinmeto_get_google_reviews(from="2025-12-01", to="2025-12-31", limit=30)   // themes + pull quotes

7. pinmeto_get_facebook_insights(from="2025-12-01", to="2025-12-31", aggregation="monthly", compare_with="prior_year")

8. pinmeto_get_facebook_ratings(from="2025-12-01", to="2025-12-31")

9. pinmeto_get_apple_insights(from="2025-12-01", to="2025-12-31", aggregation="monthly", compare_with="prior_year")
```

Ratings tools take no `aggregation`. Keywords take `YYYY-MM` and have no `limit`. See
[workflow-details.md](workflow-details.md) for the full parameter contracts.

**Note:** Only add a second call with `compare_with="prior_period"` if user explicitly requests MoM comparison.

## Report Structure

### Page 1: Cover Page

**Content:**
- Report Title: "[Brand Name] Location Analytics"
- Subtitle: "[Month] [Year] Performance Report"
- PinMeTo logo (vertical version, top-left)
- Date generated
- Confidentiality notice (optional)

**Design:**
- Background: Blue Marine (#001334)
- Title: White, Montserrat Bold 42pt
- Subtitle: Blue (#3399FF), Montserrat 24pt

### Page 2: Executive Summary (1 page)

**Content:**
- 3-5 key highlights as bullet points
- Overall performance indicator (up/down/stable)
- Critical metrics summary table

**Template:**
```
## Executive Summary

### Performance Highlights

- [Metric 1]: [Value] ([+/-X%] MoM, [+/-X%] YoY)
- [Metric 2]: [Value] ([+/-X%] MoM, [+/-X%] YoY)
- [Metric 3]: [Value] ([+/-X%] MoM, [+/-X%] YoY)

### Key Insights

1. [Most significant finding with context]
2. [Second most significant finding]
3. [Action item or opportunity identified]

### Quick Metrics

| Metric | This Month | MoM Change | YoY Change |
|--------|------------|------------|------------|
| Total Views | X | +X% | +X% |
| Total Actions | X | +X% | +X% |
| Avg Rating | X.X | +X.X | +X.X |
```

### Page 3: Executive Dashboard (1 page)

**Content:**
- 4-6 KPI cards with sparklines
- Mini charts showing MoM trends
- Color-coded performance indicators

**KPI Cards to Include:**
1. Total Profile Views (Search + Maps)
2. Customer Actions (Website + Directions + Calls)
3. Average Rating
4. Review Count
5. Discovery Searches
6. Direct Searches

**Design:**
- Card background: Grey (#F2F3F4)
- Positive change: Green
- Negative change: Orange (#FF8854)
- Neutral: Mid Grey (#333333)

### Pages 4-5: Google Business Profile Performance (2 pages)

**Page 4 - Views & Searches:**

```
## Google Business Profile - Visibility

### Profile Views

| Metric | [Month] | vs Last Month | vs Last Year |
|--------|---------|---------------|--------------|
| Search Views | X | +X% | +X% |
| Maps Views | X | +X% | +X% |
| **Total Views** | X | +X% | +X% |

### Search Performance

| Search Type | [Month] | vs Last Month | vs Last Year |
|-------------|---------|---------------|--------------|
| Direct Searches | X | +X% | +X% |
| Discovery Searches | X | +X% | +X% |
| Branded Searches | X | +X% | +X% |

[Line chart: Daily views trend for the month]
```

**Page 5 - Actions:**

```
## Google Business Profile - Customer Actions

### Action Breakdown

| Action Type | [Month] | vs Last Month | vs Last Year |
|-------------|---------|---------------|--------------|
| Website Clicks | X | +X% | +X% |
| Direction Requests | X | +X% | +X% |
| Phone Calls | X | +X% | +X% |
| **Total Actions** | X | +X% | +X% |

### Conversion Rate
Actions / Views = X.X%

[Bar chart: Actions by type comparison]
```

### Page 6: Google Ratings & Reviews (1 page)

```
## Ratings & Reviews

### Rating Summary

| Metric | [Month] | vs Last Month | vs Last Year |
|--------|---------|---------------|--------------|
| Average Rating | X.X | +X.X | +X.X |
| Total Reviews | X | +X | +X |
| New Reviews | X | - | - |

### Rating Distribution

| Stars | Count | Percentage |
|-------|-------|------------|
| 5 | X | X% |
| 4 | X | X% |
| 3 | X | X% |
| 2 | X | X% |
| 1 | X | X% |

[Horizontal bar chart: Rating distribution]

### Review Sentiment Summary
[Brief 2-3 sentence summary of recent review themes]
```

### Page 7: Keyword Analysis (1 page)

```
## Search Keywords - Top 10

### Keyword Performance

| Rank | Keyword | Impressions | Type |
|------|---------|-------------|------|
| 1 | [keyword] | X | Branded/Discovery/Navigational |
| 2 | [keyword] | X | ... |
| ... | ... | ... | ... |
| 10 | [keyword] | X | ... |

### Keyword Distribution

| Category | Count | % of Total |
|----------|-------|------------|
| Branded | X | X% |
| Discovery | X | X% |
| Navigational | X | X% |

[Pie chart: Keyword category distribution]
```

### Page 8: Facebook Performance (1 page)

```
## Facebook Page Performance

### Page Metrics

| Metric | [Month] | vs Last Month | vs Last Year |
|--------|---------|---------------|--------------|
| Page Views | X | +X% | +X% |
| Page Reach | X | +X% | +X% |
| Engagement | X | +X% | +X% |

### Facebook Rating
Average: X.X / 5.0 (X reviews)

[Bar chart: Facebook metrics comparison]
```

### Page 9: Apple Maps Performance (1 page)

```
## Apple Maps Performance

### Discovery Metrics

| Metric | [Month] | vs Last Month |
|--------|---------|---------------|
| Total Impressions | X | +X% |
| Direction Requests | X | +X% |
| Website Clicks | X | +X% |
| Calls | X | +X% |

Note: Apple Maps data may have limited historical comparison.
```

### Pages 10-11: Location Breakdown (1-2 pages, if multi-location)

```
## Location Performance Summary

### Top 5 Performing Locations

| Location | Views | Actions | Rating |
|----------|-------|---------|--------|
| [Location 1] | X | X | X.X |
| ... | ... | ... | ... |

### Locations Needing Attention

| Location | Issue | Recommendation |
|----------|-------|----------------|
| [Location A] | Low rating (X.X) | Respond to recent negative reviews |
| [Location B] | Declining views (-X%) | Update business information |
```

### Page 12: Recommendations (1 page)

```
## Strategic Recommendations

### Immediate Actions (This Month)

1. **[Action 1]**: [Specific recommendation based on data]
   - Impact: [Expected outcome]

2. **[Action 2]**: [Specific recommendation]
   - Impact: [Expected outcome]

### Focus Areas for Next Month

- [Area 1]: [Why and what to do]
- [Area 2]: [Why and what to do]

### Success Metrics to Track

- [ ] [Metric 1] target: [value]
- [ ] [Metric 2] target: [value]
```

## Chart Specifications

### Line Charts (Trends)
- Width: 100% of content area
- Height: 200px
- Colors: Blue (#3399FF) for current, Light Blue (#bbd9fa) for comparison
- X-axis: Days of month
- Y-axis: Metric value

### Bar Charts (Comparisons)
- Horizontal or vertical as appropriate
- Primary bars: Blue (#3399FF)
- Secondary bars: Orange (#FF8854)
- Labels: Mid Grey (#333333), Montserrat

### Pie Charts (Distribution)
- Colors cycle: Blue (#3399FF), Orange (#FF8854), Light Blue (#bbd9fa)
- Labels outside with leader lines
- Legend below chart

### Tables
- Header row: Blue (#3399FF) background, white text
- Alternating rows: White / Grey (#F2F3F4)
- Border: 1px Light Blue (#bbd9fa)
- Font: Montserrat for headers, Recursive for data
