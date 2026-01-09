# Quarterly Location Analytics Report Structure

## Report Parameters

| Parameter | Value |
|-----------|-------|
| Page Count | 10-18 pages |
| Top Keywords | 15 |
| Comparisons | QoQ (prior_period) + YoY (prior_year) |
| Aggregation | quarterly (summary), monthly (trends) |

## MCP Data Fetching Sequence

**IMPORTANT:** All MCP tools require `from` and `to` date parameters.

**DEFAULT:** Use `compare_with="prior_year"` (YoY) unless user specifically requests QoQ comparison.

For Q4 2025: `from: "2025-10-01"`, `to: "2025-12-31"`

```
1. pinmeto_get_locations(fields=["store_id", "name", "city", "country", "region"])

2. pinmeto_get_google_insights(from="2025-10-01", to="2025-12-31", aggregation="quarterly", compare_with="prior_year")

3. pinmeto_get_google_insights(from="2025-10-01", to="2025-12-31", aggregation="monthly")  // Monthly trends

4. pinmeto_get_google_ratings(from="2025-10-01", to="2025-12-31", aggregation="quarterly")

5. pinmeto_get_google_keywords(from="2025-10-01", to="2025-12-31", limit=15)

6. pinmeto_get_google_reviews(from="2025-10-01", to="2025-12-31", limit=50)

7. pinmeto_get_facebook_insights(from="2025-10-01", to="2025-12-31", aggregation="quarterly", compare_with="prior_year")

8. pinmeto_get_facebook_brandpage_insights(from="2025-10-01", to="2025-12-31")

9. pinmeto_get_facebook_ratings(from="2025-10-01", to="2025-12-31", aggregation="quarterly")

10. pinmeto_get_apple_insights(from="2025-10-01", to="2025-12-31", aggregation="quarterly")
```

**Note:** Only add a second call with `compare_with="prior_period"` if user explicitly requests QoQ comparison.

## Report Structure

### Page 1: Cover Page

**Content:**
- Report Title: "[Brand Name] Location Analytics"
- Subtitle: "[Quarter] [Year] Quarterly Performance Report"
- Quarter dates: "[Start Date] - [End Date]"
- PinMeTo logo (vertical version)
- Confidentiality notice

**Design:**
- Background: Blue Marine (#001334)
- Title: White, Montserrat Bold 48pt
- Quarter badge: Orange (#FF8854) accent

### Page 2: Executive Summary (1 page)

```
## Executive Summary - [Q#] [Year]

### Quarter at a Glance

[2-3 sentence overview of quarterly performance]

### Key Performance Indicators

| KPI | [Q#] Value | vs [Q#-1] | vs [Q#] Last Year |
|-----|------------|-----------|-------------------|
| Total Profile Views | X | +X% | +X% |
| Customer Actions | X | +X% | +X% |
| Average Rating | X.X | +X.X | +X.X |
| New Reviews | X | +X% | +X% |

### Quarter Highlights

1. **[Achievement]**: [Context and impact]
2. **[Trend]**: [What changed and why it matters]
3. **[Opportunity]**: [Identified growth area]

### Areas of Focus

- [Challenge 1]: [Brief description and status]
- [Challenge 2]: [Brief description and status]
```

### Page 3: Quarterly Performance Dashboard (1 page)

**Content:**
- 6-8 KPI cards with QoQ and YoY indicators
- Quarterly trend mini-charts
- Performance scorecard

**KPI Cards:**
1. Total Views (Search + Maps)
2. Customer Actions (all types)
3. Conversion Rate (Actions/Views)
4. Average Rating
5. Total Reviews
6. Net New Reviews
7. Discovery Search Share
8. Top Keyword Impressions

### Pages 4-5: Monthly Trends Within Quarter (2 pages)

```
## Monthly Performance Trends

### Month-over-Month Progression

| Metric | Month 1 | Month 2 | Month 3 | Trend |
|--------|---------|---------|---------|-------|
| Views | X | X | X | [arrow] |
| Actions | X | X | X | [arrow] |
| Rating | X.X | X.X | X.X | [arrow] |

[Line chart: 3-month trend for key metrics]

### Performance Momentum

- **Accelerating**: [Metrics showing increasing growth]
- **Decelerating**: [Metrics showing slowing growth]
- **Stable**: [Metrics with consistent performance]

### Monthly Breakdown

[Stacked bar chart: Monthly contribution to quarterly totals]
```

### Pages 6-7: Google Business Profile Deep Dive (2 pages)

**Page 6 - Visibility Analysis:**

```
## Google Business Profile - Quarterly Visibility

### Views Summary

| View Type | [Q#] Total | QoQ Change | YoY Change |
|-----------|------------|------------|------------|
| Search Views | X | +X% | +X% |
| Maps Views | X | +X% | +X% |
| **Total Views** | X | +X% | +X% |

### Search Intent Analysis

| Search Type | [Q#] Total | Share | Trend |
|-------------|------------|-------|-------|
| Direct (Brand) | X | X% | [arrow] |
| Discovery | X | X% | [arrow] |
| Branded | X | X% | [arrow] |

[Stacked area chart: Weekly search distribution over quarter]
```

**Page 7 - Actions Analysis:**

```
## Google Business Profile - Customer Actions

### Quarterly Actions Summary

| Action Type | [Q#] Total | QoQ Change | YoY Change |
|-------------|------------|------------|------------|
| Website Clicks | X | +X% | +X% |
| Direction Requests | X | +X% | +X% |
| Phone Calls | X | +X% | +X% |
| **Total Actions** | X | +X% | +X% |

### Conversion Metrics

| Metric | [Q#] | [Q#-1] | Change |
|--------|------|--------|--------|
| Views to Actions | X.X% | X.X% | +X.X% |
| Search to Actions | X.X% | X.X% | +X.X% |

[Funnel chart: Views -> Searches -> Actions]
```

### Page 8: Ratings & Reviews Analysis (1 page)

```
## Ratings & Reviews - Quarterly Analysis

### Rating Performance

| Metric | [Q#] | vs [Q#-1] | vs [Q#] LY |
|--------|------|-----------|------------|
| Average Rating | X.X | +X.X | +X.X |
| Total Reviews | X | +X | +X |
| New Reviews | X | +X% | +X% |

### Rating Distribution Trend

[Grouped bar chart: Rating distribution comparison Q vs Q-1]

### Review Volume by Month

| Month | Reviews | Avg Rating |
|-------|---------|------------|
| Month 1 | X | X.X |
| Month 2 | X | X.X |
| Month 3 | X | X.X |

### Review Theme Summary

**Positive Themes:**
- [Theme 1]: Mentioned X times
- [Theme 2]: Mentioned X times

**Improvement Areas:**
- [Theme 1]: Mentioned X times
- [Theme 2]: Mentioned X times
```

### Pages 9-10: Keyword Performance (2 pages)

**Page 9 - Top 15 Keywords:**

```
## Search Keywords - Top 15

| Rank | Keyword | Impressions | QoQ Change | Category |
|------|---------|-------------|------------|----------|
| 1 | [keyword] | X | +X% | Branded |
| 2 | [keyword] | X | +X% | Discovery |
| ... | ... | ... | ... | ... |
| 15 | [keyword] | X | +X% | Navigational |
```

**Page 10 - Keyword Strategy:**

```
## Keyword Analysis & Strategy

### Category Performance

| Category | Keywords | Impressions | % of Total | QoQ Change |
|----------|----------|-------------|------------|------------|
| Branded | X | X | X% | +X% |
| Discovery | X | X | X% | +X% |
| Navigational | X | X | X% | +X% |

[Pie chart: Category distribution]

### Emerging Keywords (New in Top 50)

| Keyword | Impressions | Category | Opportunity |
|---------|-------------|----------|-------------|
| [new keyword 1] | X | Discovery | [action] |
| [new keyword 2] | X | Discovery | [action] |

### Declining Keywords (Lost from Top 50)

| Keyword | Previous Impressions | Category |
|---------|---------------------|----------|
| [lost keyword 1] | X | [category] |
```

### Pages 11-12: Facebook & Apple Performance (2 pages)

**Page 11 - Facebook:**

```
## Facebook Performance - Quarterly

### Page Metrics

| Metric | [Q#] | QoQ Change | YoY Change |
|--------|------|------------|------------|
| Page Views | X | +X% | +X% |
| Page Reach | X | +X% | +X% |
| Page Engagement | X | +X% | +X% |
| Check-ins | X | +X% | +X% |

### Brandpage Performance

[Summary of brandpage insights across all pages]

### Facebook Rating Trend

| Month | Rating | Reviews |
|-------|--------|---------|
| Month 1 | X.X | X |
| Month 2 | X.X | X |
| Month 3 | X.X | X |
```

**Page 12 - Apple Maps:**

```
## Apple Maps Performance - Quarterly

### Discovery Metrics

| Metric | [Q#] | QoQ Change |
|--------|------|------------|
| Total Impressions | X | +X% |
| Direction Requests | X | +X% |
| Website Taps | X | +X% |
| Call Taps | X | +X% |

### Apple Maps Share of Actions

[Compare Apple Maps actions vs Google actions]
```

### Pages 13-14: Location Performance (2 pages)

```
## Location Performance Rankings

### Top 5 Locations by Views

| Rank | Location | Views | Actions | Rating | Trend |
|------|----------|-------|---------|--------|-------|
| 1 | [Location] | X | X | X.X | [arrow] |
| ... | ... | ... | ... | ... | ... |

### Top 5 Locations by Rating

| Rank | Location | Rating | Reviews | Views |
|------|----------|--------|---------|-------|
| 1 | [Location] | X.X | X | X |
| ... | ... | ... | ... | ... |

### Bottom 5 Locations Needing Attention

| Location | Primary Issue | Recommendation |
|----------|---------------|----------------|
| [Location] | Low rating (X.X) | [Action] |
| [Location] | Declining views (-X%) | [Action] |
| ... | ... | ... |

### Regional Performance Summary

| Region | Locations | Avg Views | Avg Rating | QoQ Trend |
|--------|-----------|-----------|------------|-----------|
| [Region 1] | X | X | X.X | [arrow] |
| [Region 2] | X | X | X.X | [arrow] |
```

### Pages 15-16: Strategic Recommendations (2 pages)

```
## Strategic Recommendations

### Immediate Actions (Next 30 Days)

1. **[Priority 1]**
   - Situation: [What the data shows]
   - Action: [Specific recommendation]
   - Expected Impact: [Metric improvement]
   - Owner: [Suggested responsibility]

2. **[Priority 2]**
   - Situation: [What the data shows]
   - Action: [Specific recommendation]
   - Expected Impact: [Metric improvement]

3. **[Priority 3]**
   - Situation: [What the data shows]
   - Action: [Specific recommendation]
   - Expected Impact: [Metric improvement]

### Next Quarter Focus Areas

| Focus Area | Current State | Target | Strategy |
|------------|---------------|--------|----------|
| [Area 1] | X | Y | [Approach] |
| [Area 2] | X | Y | [Approach] |
| [Area 3] | X | Y | [Approach] |

### Success Metrics for [Q#+1]

| Metric | [Q#] Actual | [Q#+1] Target | % Improvement |
|--------|-------------|---------------|---------------|
| Views | X | Y | +X% |
| Actions | X | Y | +X% |
| Rating | X.X | X.X | +X.X |
```

### Page 17: Appendix - Methodology (1 page)

```
## Appendix: Data & Methodology

### Data Sources
- Google Business Profile via PinMeTo API
- Facebook Pages via PinMeTo API
- Apple Maps Connect via PinMeTo API

### Reporting Period
- Quarter: [Q#] [Year]
- Date Range: [Start] to [End]
- Data Freshness: As of [Date] (Note: Google data has ~10-day lag)

### Metrics Definitions
See metrics-glossary.md for complete definitions.

### Calculation Notes
- YoY comparisons use same quarter from previous year
- QoQ comparisons use immediately preceding quarter
- Percentages calculated as ((current - previous) / previous) * 100

### Location Coverage
- Total Locations: X
- Active Locations: X
- Locations with Complete Data: X
```

## Additional Chart Types for Quarterly

### Quarterly Trend Charts
- 4-quarter rolling trend line
- Year-over-year overlay comparison

### Heat Maps
- Performance by region/city
- Day-of-week patterns

### Waterfall Charts
- QoQ change breakdown by component
