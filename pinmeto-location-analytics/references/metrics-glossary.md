# Platform Metrics Glossary

Complete definitions for all metrics available through PinMeTo Location MCP.

## Google Business Profile Metrics

### Views

| Metric | API Field | Definition |
|--------|-----------|------------|
| Search Views | `search_views` | Number of times profile appeared in Google Search results |
| Maps Views | `maps_views` | Number of times profile appeared in Google Maps |
| Total Views | `total_views` | Sum of Search Views + Maps Views |

### Searches

| Metric | API Field | Definition |
|--------|-----------|------------|
| Direct Searches | `direct_searches` | Searches using exact business name |
| Discovery Searches | `discovery_searches` | Searches using category, product, or service terms |
| Branded Searches | `branded_searches` | Searches combining brand + location/product |
| Total Searches | `total_searches` | Sum of all search types |

**Search Type Examples:**
- Direct: "Starbucks Stockholm"
- Discovery: "coffee shops near me"
- Branded: "Starbucks latte Stockholm"

### Customer Actions

| Metric | API Field | Definition |
|--------|-----------|------------|
| Website Clicks | `website_clicks` | Clicks on website link in profile |
| Direction Requests | `direction_requests` | Clicks on "Get Directions" |
| Phone Calls | `phone_calls` | Clicks on phone number |
| Total Actions | `total_actions` | Sum of all action types |

### Conversion Metrics (Calculated)

| Metric | Formula | Definition |
|--------|---------|------------|
| View-to-Action Rate | `(total_actions / total_views) * 100` | Percentage of views resulting in actions |
| Search-to-Action Rate | `(total_actions / total_searches) * 100` | Percentage of searches resulting in actions |

### Ratings

| Metric | API Field | Definition |
|--------|-----------|------------|
| Average Rating | `average_rating` | Mean rating (1.0-5.0 scale) |
| Total Reviews | `total_reviews` | Cumulative review count |
| New Reviews | Calculated | Reviews added in period |
| Rating Distribution | `rating_distribution` | Breakdown by star level (1-5) |

**Rating Distribution Format:**
```json
{
  "1_star": 5,
  "2_star": 10,
  "3_star": 25,
  "4_star": 100,
  "5_star": 360
}
```

### Keywords

| Metric | API Field | Definition |
|--------|-----------|------------|
| Keyword | `keyword` | Search term used to find business |
| Impressions | `impressions` | Times keyword led to profile view |
| Category | Classified | Branded, Discovery, or Navigational |

## Facebook Metrics

### Page Metrics

| Metric | API Field | Definition |
|--------|-----------|------------|
| Page Views | `page_views` | Total page views |
| Page Reach | `page_reach` | Unique users who saw content |
| Page Impressions | `page_impressions` | Total content impressions |
| Page Engagement | `page_engagement` | Reactions, comments, shares |
| Check-ins | `checkins` | User check-ins at location |

### Engagement Breakdown

| Metric | API Field | Definition |
|--------|-----------|------------|
| Reactions | `reactions` | Likes, loves, etc. on posts |
| Comments | `comments` | Comments on posts |
| Shares | `shares` | Content shares |
| Clicks | `clicks` | Clicks on posts/links |

### Facebook Ratings

| Metric | API Field | Definition |
|--------|-----------|------------|
| Facebook Rating | `facebook_rating` | Average recommendation score |
| Recommendation Count | `recommendation_count` | Number of recommendations |

**Note:** Facebook uses recommendations (Yes/No) rather than star ratings.

## Apple Maps Metrics

### Visibility

| Metric | API Field | Definition |
|--------|-----------|------------|
| Total Impressions | `total_impressions` | Times location appeared in Maps |
| Search Impressions | `search_impressions` | Impressions from search |
| Browse Impressions | `browse_impressions` | Impressions from browsing |

### Actions

| Metric | API Field | Definition |
|--------|-----------|------------|
| Direction Requests | `direction_requests` | "Get Directions" taps |
| Website Taps | `website_taps` | Website link taps |
| Call Taps | `call_taps` | Phone number taps |
| Share Actions | `share_actions` | Location shares |

## Comparison Metrics

When using `comparison_type` parameter, these fields are added:

| Field | Definition |
|-------|------------|
| `value` | Current period metric value |
| `priorValue` | Comparison period metric value |
| `delta` | Absolute change (value - priorValue) |
| `deltaPercent` | Percentage change ((delta / priorValue) * 100) |
| `priorPeriodRange` | Date range of comparison period |

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
| `half_yearly` | 6-month periods | Strategic reviews |
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

Always validate date ranges against these lags when generating reports.
