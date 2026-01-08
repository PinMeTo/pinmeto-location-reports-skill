# Keyword Classification Rules

Classify search keywords into three categories to analyze search intent and optimize local presence strategy.

## Categories

### Branded Keywords

**Definition:** Keywords containing the brand name or known brand variants.

**Indicators:**
- Exact brand name match
- Brand name + location
- Brand name + product/service
- Common brand misspellings
- Brand abbreviations or nicknames

**Examples:**
```
"starbucks" → Branded
"starbucks stockholm" → Branded
"sbux coffee" → Branded (abbreviation)
"starbacks" → Branded (misspelling)
"starbucks drive through" → Branded
```

**Business Insight:** High branded search volume indicates strong brand awareness. Growth suggests successful marketing; decline may indicate brand perception issues.

### Discovery Keywords

**Definition:** Generic category, product, or service searches without brand reference.

**Indicators:**
- Industry/category terms
- Product or service descriptions
- Generic needs or solutions
- Competitor category terms

**Examples:**
```
"coffee shop" → Discovery
"best latte" → Discovery
"breakfast restaurant" → Discovery
"pharmacy open late" → Discovery
"car repair" → Discovery
```

**Business Insight:** Discovery keywords represent new customer acquisition opportunities. High discovery traffic indicates strong category presence and SEO performance.

### Navigational Keywords

**Definition:** Keywords with clear location-finding intent.

**Indicators:**
- "near me" suffix
- Geographic modifiers (city, neighborhood, address)
- "directions to"
- "closest" or "nearest"
- "open now" or "24 hour"

**Examples:**
```
"coffee near me" → Navigational
"restaurants södermalm" → Navigational
"closest gas station" → Navigational
"pizza delivery 10115" → Navigational (postal code)
"pharmacy open now" → Navigational
```

**Business Insight:** Navigational keywords indicate immediate purchase intent. Optimize for these to capture customers ready to visit.

## Classification Algorithm

```python
def classify_keyword(keyword: str, brand_terms: list[str]) -> str:
    """
    Classify a keyword into branded, discovery, or navigational.

    Args:
        keyword: The search keyword to classify
        brand_terms: List of brand names and variants to check

    Returns:
        'branded', 'discovery', or 'navigational'
    """
    keyword_lower = keyword.lower().strip()

    # Check for branded keywords first
    for brand in brand_terms:
        if brand.lower() in keyword_lower:
            return 'branded'

    # Check for navigational patterns
    navigational_patterns = [
        'near me',
        'nearby',
        'closest',
        'nearest',
        'directions to',
        'directions',
        'open now',
        'open late',
        '24 hour',
        '24h',
        'drive to',
        'how to get to',
    ]

    # Common city/location suffixes (extend with relevant markets)
    location_indicators = [
        'stockholm',
        'göteborg',
        'malmö',
        # Add more cities as needed
    ]

    for pattern in navigational_patterns:
        if pattern in keyword_lower:
            return 'navigational'

    # Check for location-based searches (city names, postal codes)
    for location in location_indicators:
        if location in keyword_lower:
            return 'navigational'

    # Check for postal code patterns (adjust regex for locale)
    import re
    if re.search(r'\b\d{3}\s?\d{2}\b', keyword_lower):  # Swedish postal codes
        return 'navigational'
    if re.search(r'\b\d{5}\b', keyword_lower):  # US ZIP codes
        return 'navigational'

    # Default to discovery for generic searches
    return 'discovery'


def classify_keywords(keywords: list[dict], brand_terms: list[str]) -> list[dict]:
    """
    Classify a list of keywords with impressions.

    Args:
        keywords: List of {'keyword': str, 'impressions': int}
        brand_terms: List of brand names

    Returns:
        List with added 'category' field
    """
    for kw in keywords:
        kw['category'] = classify_keyword(kw['keyword'], brand_terms)
    return keywords


def get_category_summary(classified_keywords: list[dict]) -> dict:
    """
    Summarize keyword distribution by category.

    Returns:
        {
            'branded': {'count': X, 'impressions': Y, 'percentage': Z},
            'discovery': {...},
            'navigational': {...}
        }
    """
    summary = {
        'branded': {'count': 0, 'impressions': 0},
        'discovery': {'count': 0, 'impressions': 0},
        'navigational': {'count': 0, 'impressions': 0},
    }

    total_impressions = 0

    for kw in classified_keywords:
        cat = kw['category']
        summary[cat]['count'] += 1
        summary[cat]['impressions'] += kw.get('impressions', 0)
        total_impressions += kw.get('impressions', 0)

    # Calculate percentages
    for cat in summary:
        if total_impressions > 0:
            summary[cat]['percentage'] = round(
                (summary[cat]['impressions'] / total_impressions) * 100, 1
            )
        else:
            summary[cat]['percentage'] = 0

    return summary
```

## Usage Example

```python
# Brand terms for classification
brand_terms = [
    "PinMeTo",
    "Pin Me To",
    "Pinmeto",
    # Add brand variants
]

# Keywords from MCP tool
keywords = [
    {"keyword": "pinmeto login", "impressions": 500},
    {"keyword": "local seo tools", "impressions": 300},
    {"keyword": "business listing management near me", "impressions": 150},
]

# Classify
classified = classify_keywords(keywords, brand_terms)

# Result:
# [
#     {"keyword": "pinmeto login", "impressions": 500, "category": "branded"},
#     {"keyword": "local seo tools", "impressions": 300, "category": "discovery"},
#     {"keyword": "business listing management near me", "impressions": 150, "category": "navigational"},
# ]

# Get summary
summary = get_category_summary(classified)
# {
#     'branded': {'count': 1, 'impressions': 500, 'percentage': 52.6},
#     'discovery': {'count': 1, 'impressions': 300, 'percentage': 31.6},
#     'navigational': {'count': 1, 'impressions': 150, 'percentage': 15.8}
# }
```

## Strategic Interpretation

### Ideal Distribution (varies by industry)

| Category | Established Brand | Growing Brand |
|----------|-------------------|---------------|
| Branded | 40-60% | 20-40% |
| Discovery | 25-40% | 40-60% |
| Navigational | 15-25% | 15-25% |

### Analysis Questions

**High Branded (>60%):**
- Strong brand awareness
- Consider: Is discovery traffic being missed?

**High Discovery (>50%):**
- Strong category presence
- Consider: Are we converting to brand loyalty?

**High Navigational (>30%):**
- High purchase intent traffic
- Consider: Is location information optimized?

**Low Discovery (<20%):**
- May be missing new customer opportunities
- Consider: Category keyword optimization

### Recommendations by Category

| If... | Then... |
|-------|---------|
| Branded declining | Review brand messaging, check for reputation issues |
| Discovery low | Optimize category keywords in profile, add services/products |
| Navigational low | Verify address accuracy, add location-specific content |
| Navigational high but conversions low | Check operating hours accuracy, verify directions work |
