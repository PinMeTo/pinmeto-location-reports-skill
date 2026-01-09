# Half-Yearly Location Analytics Report Structure

## Report Parameters

| Parameter | Value |
|-----------|-------|
| Page Count | 12-20 pages |
| Top Keywords | 20 |
| Comparisons | HoH (prior_period) + YoY (prior_year) |
| Aggregation | half_yearly (summary), quarterly/monthly (trends) |

## MCP Data Fetching Sequence

**IMPORTANT:** All MCP tools require `from` and `to` date parameters.

**DEFAULT:** Use `compare_with="prior_year"` (YoY) unless user specifically requests HoH comparison.

For H2 2025: `from: "2025-07-01"`, `to: "2025-12-31"`

```
1. pinmeto_get_locations(fields=["store_id", "name", "city", "country", "region"])

2. pinmeto_get_google_insights(from="2025-07-01", to="2025-12-31", aggregation="half_yearly", compare_with="prior_year")

3. pinmeto_get_google_insights(from="2025-07-01", to="2025-12-31", aggregation="quarterly")

4. pinmeto_get_google_insights(from="2025-07-01", to="2025-12-31", aggregation="monthly")

5. pinmeto_get_google_ratings(from="2025-07-01", to="2025-12-31", aggregation="half_yearly")

6. pinmeto_get_google_ratings(from="2025-07-01", to="2025-12-31", aggregation="monthly")

7. pinmeto_get_google_keywords(from="2025-07-01", to="2025-12-31", limit=20)

8. pinmeto_get_google_reviews(from="2025-07-01", to="2025-12-31", limit=100)

9. pinmeto_get_facebook_insights(from="2025-07-01", to="2025-12-31", aggregation="half_yearly", compare_with="prior_year")

10. pinmeto_get_facebook_brandpage_insights(from="2025-07-01", to="2025-12-31")

11. pinmeto_get_facebook_ratings(from="2025-07-01", to="2025-12-31", aggregation="half_yearly")

12. pinmeto_get_apple_insights(from="2025-07-01", to="2025-12-31", aggregation="half_yearly")
```

**Note:** Only add a second call with `compare_with="prior_period"` if user explicitly requests HoH comparison.

## Report Structure

### Page 1: Cover Page

**Content:**
- Report Title: "[Brand Name] Location Analytics"
- Subtitle: "[H1/H2] [Year] Performance Report"
- Period: "[Start Date] - [End Date]"
- PinMeTo logo (vertical version)

**Design:**
- Background: Gradient Blue Marine to Blue
- Title: White, Montserrat Bold 52pt
- Half badge: Orange (#FF8854)

### Pages 2-3: Executive Summary (2 pages)

```
## Executive Summary - [H#] [Year]

### Half-Year Performance Overview

[3-4 paragraph executive narrative covering:
- Overall performance against goals
- Key achievements
- Notable challenges
- Strategic implications]

### Key Performance Indicators

| KPI | [H#] Total | vs [H#-1] | vs [H#] LY | Trend |
|-----|------------|-----------|------------|-------|
| Profile Views | X | +X% | +X% | [arrow] |
| Customer Actions | X | +X% | +X% | [arrow] |
| Average Rating | X.X | +X.X | +X.X | [arrow] |
| Total Reviews | X | +X | +X | [arrow] |
| Conversion Rate | X.X% | +X.X% | +X.X% | [arrow] |

### Quarter-by-Quarter Summary

| Metric | Q[#] | Q[#+1] | Half Total |
|--------|------|--------|------------|
| Views | X | X | X |
| Actions | X | X | X |
| Reviews | X | X | X |

### Strategic Highlights

**Wins:**
1. [Major achievement with business impact]
2. [Second major achievement]

**Challenges:**
1. [Key challenge encountered]
2. [Second challenge]

**Opportunities Identified:**
1. [Growth opportunity for H2/next year]
2. [Second opportunity]
```

### Page 4: Half-Year Dashboard (1 page)

**Content:**
- 8-10 KPI cards
- 6-month sparklines
- Performance vs. target indicators

**KPI Layout (2x4 grid):**
| Row | KPIs |
|-----|------|
| 1 | Total Views, Total Actions |
| 2 | Conversion Rate, Avg Rating |
| 3 | New Reviews, Discovery Searches |
| 4 | Top Keyword Impressions, Apple Maps Share |

### Pages 5-6: Quarterly Analysis (2 pages)

```
## Quarterly Performance Comparison

### Quarter-over-Quarter Analysis

| Metric | Q[#] | Q[#+1] | Change | Trend Analysis |
|--------|------|--------|--------|----------------|
| Views | X | X | +X% | [Analysis] |
| Actions | X | X | +X% | [Analysis] |
| Rating | X.X | X.X | +X.X | [Analysis] |

[Grouped bar chart: Q1 vs Q2 for all key metrics]

### Monthly Progression

[Line chart: 6-month trend for views, actions, rating]

| Month | Views | Actions | Rating | Notes |
|-------|-------|---------|--------|-------|
| Month 1 | X | X | X.X | |
| Month 2 | X | X | X.X | |
| Month 3 | X | X | X.X | End Q[#] |
| Month 4 | X | X | X.X | |
| Month 5 | X | X | X.X | |
| Month 6 | X | X | X.X | End Q[#+1] |

### Seasonal Patterns Identified

[Analysis of any seasonal trends observed in the 6-month period]
```

### Pages 7-8: Google Business Profile Analysis (2 pages)

**Page 7 - Visibility & Discovery:**

```
## Google Business Profile - Half-Year Analysis

### Visibility Metrics

| Metric | [H#] Total | HoH Change | YoY Change |
|--------|------------|------------|------------|
| Search Views | X | +X% | +X% |
| Maps Views | X | +X% | +X% |
| Total Views | X | +X% | +X% |

### Search Intent Distribution

| Search Type | [H#] Total | % Share | Trend |
|-------------|------------|---------|-------|
| Direct | X | X% | [arrow] |
| Discovery | X | X% | [arrow] |
| Branded | X | X% | [arrow] |

[Stacked area chart: Monthly search type distribution]

### Discovery Performance

- Discovery Searches: X (+X% YoY)
- Discovery/Total Ratio: X%
- Top Discovery Categories: [list]
```

**Page 8 - Actions & Conversion:**

```
### Customer Actions Analysis

| Action Type | [H#] Total | HoH Change | YoY Change |
|-------------|------------|------------|------------|
| Website Clicks | X | +X% | +X% |
| Direction Requests | X | +X% | +X% |
| Phone Calls | X | +X% | +X% |
| Total Actions | X | +X% | +X% |

### Conversion Funnel

Views → Searches → Actions

| Stage | Volume | Conversion |
|-------|--------|------------|
| Total Views | X | - |
| Active Searches | X | X% |
| Actions Taken | X | X% |

### Action Mix Analysis

[Pie chart: Action type distribution]

- Primary Action: [Type] (X%)
- Trend: [Growing/Declining action types]
```

### Page 9: Ratings & Reviews Deep Dive (1 page)

```
## Ratings & Reviews - Half-Year Analysis

### Rating Trajectory

| Period | Avg Rating | Total Reviews | New Reviews |
|--------|------------|---------------|-------------|
| [H#-1] | X.X | X | X |
| [H#] | X.X | X | X |
| Change | +X.X | +X | +X% |

[Line chart: Monthly average rating trend]

### Review Volume Analysis

| Month | 5-Star | 4-Star | 3-Star | 2-Star | 1-Star | Total |
|-------|--------|--------|--------|--------|--------|-------|
| M1 | X | X | X | X | X | X |
| M2 | X | X | X | X | X | X |
| ... | ... | ... | ... | ... | ... | ... |

### Sentiment Analysis Summary

**Top Positive Themes (from X positive reviews):**
1. [Theme]: X mentions
2. [Theme]: X mentions
3. [Theme]: X mentions

**Top Improvement Areas (from X critical reviews):**
1. [Theme]: X mentions
2. [Theme]: X mentions
3. [Theme]: X mentions

### Response Rate & Time

| Metric | Q[#] | Q[#+1] | Target |
|--------|------|--------|--------|
| Response Rate | X% | X% | >80% |
| Avg Response Time | Xh | Xh | <24h |
```

### Pages 10-11: Keyword Strategy Analysis (2 pages)

```
## Search Keywords - Top 20 Analysis

### Keyword Performance

| Rank | Keyword | Impressions | HoH Change | YoY Change | Category |
|------|---------|-------------|------------|------------|----------|
| 1 | [kw] | X | +X% | +X% | Branded |
| ... | ... | ... | ... | ... | ... |
| 20 | [kw] | X | +X% | +X% | Discovery |

### Category Strategic Analysis

| Category | Keywords | Impressions | % Total | HoH Trend |
|----------|----------|-------------|---------|-----------|
| Branded | X | X | X% | +X% |
| Discovery | X | X | X% | +X% |
| Navigational | X | X | X% | +X% |

### Keyword Insights

**Growing Keywords (Top 5 by growth):**
| Keyword | Growth | Category | Opportunity |
|---------|--------|----------|-------------|
| [kw] | +X% | [cat] | [insight] |

**Declining Keywords (Investigate):**
| Keyword | Decline | Category | Action |
|---------|---------|----------|--------|
| [kw] | -X% | [cat] | [action] |

### Competitive Keyword Landscape

[Analysis of discovery keywords indicating competitive positioning]
```

### Pages 12-13: Multi-Platform Performance (2 pages)

**Page 12 - Facebook:**

```
## Facebook Performance - Half-Year

### Engagement Metrics

| Metric | [H#] Total | HoH Change | YoY Change |
|--------|------------|------------|------------|
| Page Views | X | +X% | +X% |
| Reach | X | +X% | +X% |
| Engagement | X | +X% | +X% |
| Check-ins | X | +X% | +X% |

### Facebook vs Google Comparison

| Metric | Google | Facebook | Gap |
|--------|--------|----------|-----|
| Views | X | X | X |
| Actions | X | X | X |
| Rating | X.X | X.X | +X.X |

### Brandpage Insights

[Summary across all brandpages]
```

**Page 13 - Apple Maps:**

```
## Apple Maps - Half-Year

### Performance Summary

| Metric | [H#] Total | HoH Change |
|--------|------------|------------|
| Impressions | X | +X% |
| Directions | X | +X% |
| Website | X | +X% |
| Calls | X | +X% |

### Platform Share Analysis

| Platform | Actions Share | Trend |
|----------|---------------|-------|
| Google | X% | [arrow] |
| Apple | X% | [arrow] |
| Facebook | X% | [arrow] |

[Pie chart: Platform action distribution]
```

### Pages 14-15: Location Portfolio Analysis (2 pages)

```
## Location Performance Analysis

### Portfolio Overview

| Metric | Value |
|--------|-------|
| Total Locations | X |
| Avg Views/Location | X |
| Avg Rating | X.X |
| Top Performer Views | X |
| Bottom Performer Views | X |

### Top 10 Locations

| Rank | Location | Views | Actions | Rating | Trend |
|------|----------|-------|---------|--------|-------|
| 1 | [loc] | X | X | X.X | [arrow] |
| ... | ... | ... | ... | ... | ... |

### Locations Requiring Intervention

| Location | Issue | Severity | Recommended Action |
|----------|-------|----------|-------------------|
| [loc] | [issue] | High/Med | [action] |

### Regional Performance

| Region | Locations | Total Views | Avg Rating | Trend |
|--------|-----------|-------------|------------|-------|
| [reg] | X | X | X.X | [arrow] |

[Map visualization: Regional heat map]
```

### Pages 16-17: Financial Impact Analysis (2 pages)

```
## Business Value Analysis

### Customer Engagement Value

| Metric | Volume | Est. Value | Total Value |
|--------|--------|------------|-------------|
| Website Clicks | X | $X/click | $X |
| Direction Requests | X | $X/request | $X |
| Phone Calls | X | $X/call | $X |
| **Total** | X | - | **$X** |

*Note: Values are estimated based on industry benchmarks*

### Year-over-Year Comparison

| Metric | [H#] LY | [H#] TY | Growth | Value Impact |
|--------|---------|---------|--------|--------------|
| Actions | X | X | +X% | +$X |

### Reputation Impact

- Rating Improvement: +X.X stars
- Review Volume Growth: +X%
- Estimated Revenue Impact: [analysis]

### ROI Indicators

[Analysis of PinMeTo platform value based on improvements]
```

### Pages 18-19: Strategic Recommendations (2 pages)

```
## Strategic Recommendations

### H2 / Next Half Priorities

#### Priority 1: [Strategic Initiative]
- **Objective**: [Goal]
- **Rationale**: [Why based on data]
- **Actions**:
  1. [Specific action]
  2. [Specific action]
  3. [Specific action]
- **Success Metrics**: [How to measure]
- **Resources Required**: [Estimate]

#### Priority 2: [Strategic Initiative]
[Same structure]

#### Priority 3: [Strategic Initiative]
[Same structure]

### Tactical Quick Wins (Next 30 Days)

| Action | Owner | Expected Impact | Effort |
|--------|-------|-----------------|--------|
| [action] | [team] | +X% [metric] | Low |
| [action] | [team] | +X% [metric] | Medium |

### Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [risk] | High/Med/Low | [impact] | [action] |

### Goals for [H#+1]

| Metric | [H#] Actual | [H#+1] Target | Growth |
|--------|-------------|---------------|--------|
| Views | X | X | +X% |
| Actions | X | X | +X% |
| Rating | X.X | X.X | +X.X |
| Reviews | X | X | +X |
```

### Page 20: Appendix

```
## Appendix

### Data Sources & Methodology

[Same as quarterly]

### Glossary

See metrics-glossary.md

### Report Distribution

- Executive Team
- Regional Managers
- Marketing Team

### Next Report

[H#+1] Report expected: [Date]
```
