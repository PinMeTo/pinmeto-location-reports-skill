# Yearly Location Analytics Report Structure

## Report Parameters

| Parameter | Value |
|-----------|-------|
| Page Count | 15-25 pages |
| Top Keywords | 25 |
| Comparisons | YoY (prior_year) |
| Aggregation | yearly (summary), quarterly/monthly (trends) |
| Audience | Board of Directors, C-Level Executives |

## MCP Data Fetching Sequence

**IMPORTANT:** All MCP tools require `from` and `to` date parameters.

For 2025: `from: "2025-01-01"`, `to: "2025-12-31"`

```
1. pinmeto_get_locations(fields=["store_id", "name", "city", "country", "region"])

2. pinmeto_get_google_insights(from="2025-01-01", to="2025-12-31", aggregation="yearly", compare_with="prior_year")

3. pinmeto_get_google_insights(from="2025-01-01", to="2025-12-31", aggregation="quarterly")

4. pinmeto_get_google_insights(from="2025-01-01", to="2025-12-31", aggregation="monthly")

5. pinmeto_get_google_ratings(from="2025-01-01", to="2025-12-31", aggregation="yearly", compare_with="prior_year")

6. pinmeto_get_google_ratings(from="2025-01-01", to="2025-12-31", aggregation="monthly")

7. pinmeto_get_google_keywords(from="2025-01-01", to="2025-12-31", limit=25)

8. pinmeto_get_google_reviews(from="2025-01-01", to="2025-12-31", limit=200)

9. pinmeto_get_facebook_insights(from="2025-01-01", to="2025-12-31", aggregation="yearly", compare_with="prior_year")

10. pinmeto_get_facebook_brandpage_insights(from="2025-01-01", to="2025-12-31")

11. pinmeto_get_facebook_ratings(from="2025-01-01", to="2025-12-31", aggregation="yearly")

12. pinmeto_get_apple_insights(from="2025-01-01", to="2025-12-31", aggregation="yearly")
```

## Report Structure

### Page 1: Cover Page

**Content:**
- Report Title: "[Brand Name]"
- Subtitle: "Annual Location Performance Report"
- Year: "[Year]"
- Tagline: "Powered by PinMeTo"
- Logo and confidentiality

**Design:**
- Premium feel for board presentation
- Background: Gradient Blue Marine (#001334) to Blue (#3399FF)
- Title: White, Montserrat Bold 56pt
- Year badge: Orange (#FF8854) accent circle
- Full-bleed design

### Pages 2-3: Executive Summary (2 pages - Board Ready)

```
## Executive Summary - [Year] Annual Review

### Year in Review

[Executive narrative - 4-5 paragraphs covering:
- Overall business performance context
- Location analytics performance highlights
- Digital presence achievements
- Customer engagement summary
- Strategic outcomes]

### Annual Performance Scorecard

| KPI | [Year] | [Year-1] | YoY Change | Status |
|-----|--------|----------|------------|--------|
| Profile Views | X | X | +X% | [status] |
| Customer Actions | X | X | +X% | [status] |
| Conversion Rate | X.X% | X.X% | +X.X% | [status] |
| Average Rating | X.X | X.X | +X.X | [status] |
| Total Reviews | X | X | +X | [status] |
| Net Promoter Score* | X | X | +X | [status] |

*Estimated from rating distribution

### Key Achievements

1. **[Achievement 1]**: [Impact statement with numbers]
2. **[Achievement 2]**: [Impact statement with numbers]
3. **[Achievement 3]**: [Impact statement with numbers]

### Areas Requiring Board Attention

1. **[Item 1]**: [Brief description and recommendation]
2. **[Item 2]**: [Brief description and recommendation]

### Strategic Outlook

[2-3 sentences on next year positioning]
```

### Page 4: Annual Performance Dashboard (1 page)

**Content:**
- Large KPI tiles (6)
- Year-over-year indicators
- Status colors (green/yellow/red)
- Mini 12-month sparklines

**Layout:**
```
┌─────────────────┬─────────────────┬─────────────────┐
│   TOTAL VIEWS   │  TOTAL ACTIONS  │ CONVERSION RATE │
│   [large num]   │   [large num]   │   [large num]   │
│   +X% YoY       │    +X% YoY      │   +X.X% YoY     │
│   [sparkline]   │   [sparkline]   │   [sparkline]   │
├─────────────────┼─────────────────┼─────────────────┤
│  AVG RATING     │  TOTAL REVIEWS  │  DISCOVERY %    │
│   [large num]   │   [large num]   │   [large num]   │
│   +X.X YoY      │    +X YoY       │   +X% YoY       │
│   [sparkline]   │   [sparkline]   │   [sparkline]   │
└─────────────────┴─────────────────┴─────────────────┘
```

### Pages 5-6: Year in Review - Quarterly Breakdown (2 pages)

```
## Quarterly Performance Analysis

### Quarter-by-Quarter Summary

| Metric | Q1 | Q2 | Q3 | Q4 | Full Year |
|--------|-----|-----|-----|-----|-----------|
| Views | X | X | X | X | X |
| Actions | X | X | X | X | X |
| Rating | X.X | X.X | X.X | X.X | X.X |
| Reviews | X | X | X | X | X |

[Line chart: Quarterly trends for all key metrics]

### Quarterly Growth Rates

| Quarter | Views Growth | Actions Growth | Rating Change |
|---------|--------------|----------------|---------------|
| Q1 vs Q4 [Y-1] | +X% | +X% | +X.X |
| Q2 vs Q1 | +X% | +X% | +X.X |
| Q3 vs Q2 | +X% | +X% | +X.X |
| Q4 vs Q3 | +X% | +X% | +X.X |

### Seasonality Analysis

[Analysis of seasonal patterns with recommendations for next year planning]

### Key Events Impact

| Event/Period | Dates | Impact on Metrics | Learning |
|--------------|-------|-------------------|----------|
| [Event 1] | [dates] | +X% views | [insight] |
| [Event 2] | [dates] | +X% actions | [insight] |
```

### Pages 7-8: Google Business Profile Annual Analysis (2 pages)

**Page 7 - Visibility & Discovery:**

```
## Google Business Profile - Annual Performance

### Visibility Metrics - [Year]

| Metric | [Year] | [Year-1] | YoY Change |
|--------|--------|----------|------------|
| Search Views | X | X | +X% |
| Maps Views | X | X | +X% |
| **Total Views** | X | X | +X% |

### Search Performance Evolution

| Search Type | [Year] | [Year-1] | YoY Change | % Share |
|-------------|--------|----------|------------|---------|
| Direct | X | X | +X% | X% |
| Discovery | X | X | +X% | X% |
| Branded | X | X | +X% | X% |

[Stacked area chart: Monthly search type evolution over 12 months]

### Discovery Growth Analysis

- Discovery searches increased X% YoY
- Discovery now represents X% of all searches
- [Strategic implication]
```

**Page 8 - Customer Actions:**

```
### Customer Actions - Annual Summary

| Action | [Year] | [Year-1] | YoY Change | % of Total |
|--------|--------|----------|------------|------------|
| Website Clicks | X | X | +X% | X% |
| Direction Requests | X | X | +X% | X% |
| Phone Calls | X | X | +X% | X% |
| **Total Actions** | X | X | +X% | 100% |

### Conversion Performance

| Metric | [Year] | [Year-1] | Improvement |
|--------|--------|----------|-------------|
| Views to Actions | X.X% | X.X% | +X.X% |
| Search to Actions | X.X% | X.X% | +X.X% |

### Action Mix Evolution

[Show how action distribution changed year over year]

[Grouped bar chart: Action types [Year] vs [Year-1]]
```

### Pages 9-10: Customer Sentiment & Reputation (2 pages)

```
## Reputation Excellence - Annual Review

### Rating Performance

| Metric | [Year] | [Year-1] | YoY Change | Industry Avg |
|--------|--------|----------|------------|--------------|
| Average Rating | X.X | X.X | +X.X | X.X |
| Total Reviews | X | X | +X | - |
| New Reviews | X | X | +X% | - |

### Rating Trajectory

[Line chart: Monthly average rating for 24 months (current + prior year)]

### Rating Distribution Evolution

| Stars | [Year] | [Year-1] | Change |
|-------|--------|----------|--------|
| 5-Star | X% | X% | +X% |
| 4-Star | X% | X% | +X% |
| 3-Star | X% | X% | -X% |
| 2-Star | X% | X% | -X% |
| 1-Star | X% | X% | -X% |

### Annual Sentiment Analysis

**What Customers Love (Top Themes):**
| Theme | Mentions | Sentiment Score |
|-------|----------|-----------------|
| [Theme 1] | X | +X.X |
| [Theme 2] | X | +X.X |
| [Theme 3] | X | +X.X |

**Improvement Opportunities:**
| Theme | Mentions | Sentiment Score | Priority |
|-------|----------|-----------------|----------|
| [Theme 1] | X | -X.X | High |
| [Theme 2] | X | -X.X | Medium |

### Review Response Performance

| Metric | [Year] | [Year-1] | Target | Status |
|--------|--------|----------|--------|--------|
| Response Rate | X% | X% | 90% | [status] |
| Avg Response Time | Xh | Xh | <24h | [status] |
| Response Quality Score* | X/10 | X/10 | 8/10 | [status] |
```

### Pages 11-12: Keyword & Search Strategy (2 pages)

```
## Search Keyword Analysis - Top 25

### Annual Keyword Performance

| Rank | Keyword | Impressions | YoY Change | Category |
|------|---------|-------------|------------|----------|
| 1 | [keyword] | X | +X% | Branded |
| 2 | [keyword] | X | +X% | Discovery |
| ... | ... | ... | ... | ... |
| 25 | [keyword] | X | +X% | Navigational |

### Category Performance Summary

| Category | Keywords | Impressions | YoY Growth | Strategy |
|----------|----------|-------------|------------|----------|
| Branded | X | X | +X% | Maintain |
| Discovery | X | X | +X% | Grow |
| Navigational | X | X | +X% | Optimize |

### Keyword Strategy Insights

**High-Value Discovery Keywords:**
[Analysis of discovery keywords driving new customer acquisition]

**Competitive Position:**
[Analysis of branded vs discovery ratio compared to industry]

**Emerging Search Trends:**
| Trend | Keywords | Growth | [Year+1] Opportunity |
|-------|----------|--------|----------------------|
| [Trend 1] | X | +X% | [recommendation] |
| [Trend 2] | X | +X% | [recommendation] |

### Search Strategy Recommendations for [Year+1]

1. [Strategy recommendation]
2. [Strategy recommendation]
3. [Strategy recommendation]
```

### Pages 13-14: Multi-Platform Performance (2 pages)

```
## Multi-Platform Digital Presence

### Platform Performance Comparison

| Platform | Metric | [Year] | [Year-1] | YoY |
|----------|--------|--------|----------|-----|
| Google | Views | X | X | +X% |
| Google | Actions | X | X | +X% |
| Google | Rating | X.X | X.X | +X.X |
| Facebook | Reach | X | X | +X% |
| Facebook | Engagement | X | X | +X% |
| Facebook | Rating | X.X | X.X | +X.X |
| Apple | Impressions | X | X | +X% |
| Apple | Actions | X | X | +X% |

### Platform Share of Voice

| Platform | [Year] Share | [Year-1] Share | Trend |
|----------|--------------|----------------|-------|
| Google | X% | X% | [arrow] |
| Facebook | X% | X% | [arrow] |
| Apple | X% | X% | [arrow] |

[Pie chart: Platform distribution]

### Cross-Platform Strategy Analysis

- **Google**: [Performance summary and strategy]
- **Facebook**: [Performance summary and strategy]
- **Apple**: [Performance summary and strategy]

### Platform Investment Priorities for [Year+1]

| Platform | Priority | Investment Focus | Expected ROI |
|----------|----------|------------------|--------------|
| [Platform] | High/Med/Low | [Focus area] | [estimate] |
```

### Pages 15-16: Location Portfolio Analysis (2 pages)

```
## Location Portfolio Performance

### Portfolio Health Overview

| Metric | Value |
|--------|-------|
| Total Locations | X |
| Active Locations | X |
| Average Views/Location | X |
| Average Rating | X.X |
| Locations Above 4.5 Rating | X (X%) |
| Locations Below 4.0 Rating | X (X%) |

### Top 10 Performing Locations

| Rank | Location | Views | Actions | Rating | YoY Growth |
|------|----------|-------|---------|--------|------------|
| 1 | [Location] | X | X | X.X | +X% |
| ... | ... | ... | ... | ... | ... |

### Locations Requiring Strategic Review

| Location | Issue | Impact | Recommendation |
|----------|-------|--------|----------------|
| [Location] | [issue] | High | [action] |
| [Location] | [issue] | Medium | [action] |

### Regional Performance Matrix

| Region | Locations | Total Views | Avg Rating | YoY Trend | Status |
|--------|-----------|-------------|------------|-----------|--------|
| [Region] | X | X | X.X | +X% | [status] |

[Heat map: Regional performance visualization]

### New Location Performance

[Analysis of any locations opened during the year]

### Location Optimization Opportunities

| Tier | Locations | Opportunity | Estimated Uplift |
|------|-----------|-------------|------------------|
| High Potential | X | [opportunity] | +X% views |
| Medium Potential | X | [opportunity] | +X% views |
```

### Pages 17-18: Financial Impact & Business Value (2 pages)

```
## Business Value Analysis

### Customer Engagement Value - [Year]

| Action Type | Volume | Value/Action | Total Value |
|-------------|--------|--------------|-------------|
| Website Clicks | X | $X | $X |
| Direction Requests | X | $X | $X |
| Phone Calls | X | $X | $X |
| **Total Engagement Value** | X | - | **$X** |

### Year-over-Year Value Growth

| Metric | [Year-1] Value | [Year] Value | Growth |
|--------|----------------|--------------|--------|
| Total Engagement Value | $X | $X | +$X (+X%) |

### Reputation Value

- Rating improved by X.X stars
- Estimated revenue impact per 0.1 star: $X
- Total reputation value improvement: $X

### Digital Presence ROI

| Investment | Return | ROI |
|------------|--------|-----|
| PinMeTo Platform | $X | X% |
| Content Investment | $X | X% |
| Review Management | $X | X% |

### Competitive Advantage Metrics

[Analysis of digital presence vs competitors if available]
```

### Pages 19-21: Strategic Roadmap [Year+1] (3 pages)

```
## [Year+1] Strategic Roadmap

### Vision

[1-2 sentence vision for next year's location analytics performance]

### Strategic Pillars

#### Pillar 1: [Strategic Theme]
- **Goal**: [Specific measurable goal]
- **Key Initiatives**:
  1. [Initiative with timeline]
  2. [Initiative with timeline]
  3. [Initiative with timeline]
- **Success Metrics**: [How we'll measure]
- **Investment Required**: [Estimate]

#### Pillar 2: [Strategic Theme]
[Same structure]

#### Pillar 3: [Strategic Theme]
[Same structure]

### Quarterly Milestones

| Quarter | Key Milestones | Target Metrics |
|---------|----------------|----------------|
| Q1 | [Milestone 1], [Milestone 2] | Views: X, Rating: X.X |
| Q2 | [Milestone 1], [Milestone 2] | Views: X, Rating: X.X |
| Q3 | [Milestone 1], [Milestone 2] | Views: X, Rating: X.X |
| Q4 | [Milestone 1], [Milestone 2] | Views: X, Rating: X.X |

### [Year+1] Goals & Targets

| Metric | [Year] Actual | [Year+1] Target | Growth |
|--------|---------------|-----------------|--------|
| Total Views | X | X | +X% |
| Total Actions | X | X | +X% |
| Conversion Rate | X.X% | X.X% | +X.X% |
| Average Rating | X.X | X.X | +X.X |
| Total Reviews | X | X | +X |

### Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Strategy] |
| [Risk 2] | High/Med/Low | High/Med/Low | [Strategy] |

### Resource Requirements

| Resource | [Year+1] Need | Current State | Gap |
|----------|---------------|---------------|-----|
| [Resource 1] | X | X | X |
| [Resource 2] | X | X | X |
```

### Pages 22-23: Appendix (2 pages)

```
## Appendix

### A. Data Sources & Methodology

**Data Sources:**
- Google Business Profile via PinMeTo API
- Facebook Pages via PinMeTo API
- Apple Maps Connect via PinMeTo API

**Reporting Period:**
- Year: [Year]
- Date Range: January 1 - December 31
- Data Extracted: [Date]
- Data Lag: Google data has ~10-day reporting delay

**Calculation Methodology:**
- YoY comparisons: Same period from [Year-1]
- Percentage changes: ((Current - Previous) / Previous) * 100
- Rating averages: Weighted by review count

### B. Complete Metrics Reference

See metrics-glossary.md for complete definitions.

### C. Location List

| Store ID | Location Name | City | Region | Status |
|----------|---------------|------|--------|--------|
| [ID] | [Name] | [City] | [Region] | Active |
| ... | ... | ... | ... | ... |

### D. Report Distribution

- Board of Directors
- Executive Leadership Team
- Regional Vice Presidents
- Marketing Leadership
- Operations Leadership

### E. Report Cadence

| Report Type | Frequency | Audience |
|-------------|-----------|----------|
| Monthly | Monthly | Management |
| Quarterly | Quarterly | Leadership |
| Half-Yearly | Semi-Annual | Executive |
| Annual | Annual | Board |

### F. Contact Information

For questions about this report:
[Contact details]
```

## Board Presentation Best Practices

### Design Guidelines
- Clean, uncluttered layouts
- Large fonts for projected presentations
- High-contrast colors
- Minimal text, maximum visualization
- Executive summary that stands alone

### Narrative Flow
1. Performance headline
2. Key achievements
3. Challenges addressed
4. Opportunities identified
5. Forward-looking strategy
6. Board-level recommendations

### Speaking Points Template
For each major section, include:
- Key insight (30 seconds)
- Business impact (30 seconds)
- Recommendation (30 seconds)
