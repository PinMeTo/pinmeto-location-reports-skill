#!/usr/bin/env python3
"""
Validates report data JSON before generating PDF/PPTX reports.

Usage:
    python scripts/validate_report_data.py report_data.json

Exit codes:
    0 - Validation passed
    1 - Validation failed (errors found)
"""

import json
import sys
import re
from typing import Any


def validate_required_fields(data: dict) -> list[str]:
    """Check that all required top-level fields exist."""
    errors = []
    required = ['companyName', 'title', 'period', 'dateRange']

    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not data[field]:
            errors.append(f"Empty required field: {field}")

    return errors


def validate_kpis(data: dict) -> list[str]:
    """Validate KPI structure and values."""
    errors = []
    kpis = data.get('kpis', [])

    if not isinstance(kpis, list):
        errors.append("kpis must be a list")
        return errors

    for i, kpi in enumerate(kpis):
        if not isinstance(kpi, dict):
            errors.append(f"kpis[{i}] must be an object")
            continue

        if 'name' not in kpi:
            errors.append(f"kpis[{i}] missing 'name'")
        if 'value' not in kpi:
            errors.append(f"kpis[{i}] missing 'value'")

    return errors


def validate_rating(data: dict) -> list[str]:
    """Check rating values are within valid bounds (1.0-5.0)."""
    errors = []
    reviews = data.get('reviews', {})

    if not reviews:
        return errors

    avg_rating = reviews.get('averageRating')
    if avg_rating is not None:
        try:
            rating = float(avg_rating)
            if not (1.0 <= rating <= 5.0):
                errors.append(f"Invalid averageRating: {rating} (must be 1.0-5.0)")
        except (ValueError, TypeError):
            errors.append(f"averageRating must be a number: {avg_rating}")

    return errors


def validate_sentiment(data: dict) -> list[str]:
    """Check sentiment percentages sum to ~100%."""
    errors = []
    reviews = data.get('reviews', {})
    sentiment = reviews.get('sentiment', {})

    if not sentiment:
        return errors

    positive = sentiment.get('positive', 0)
    neutral = sentiment.get('neutral', 0)
    negative = sentiment.get('negative', 0)

    total = positive + neutral + negative

    # Allow small rounding errors (95-105%)
    if total > 0 and not (95 <= total <= 105):
        errors.append(f"Sentiment percentages sum to {total}% (expected ~100%)")

    # Check for negative values
    for key, val in [('positive', positive), ('neutral', neutral), ('negative', negative)]:
        if val < 0:
            errors.append(f"Negative sentiment value: {key}={val}")

    return errors


def validate_metrics(data: dict) -> list[str]:
    """Check metrics have valid structure."""
    errors = []

    for platform in ['google', 'facebook', 'apple']:
        platform_data = data.get(platform, {})
        if not platform_data:
            continue

        metrics = platform_data.get('metrics', [])
        if not isinstance(metrics, list):
            errors.append(f"{platform}.metrics must be a list")
            continue

        for i, metric in enumerate(metrics):
            if not isinstance(metric, dict):
                errors.append(f"{platform}.metrics[{i}] must be an object")
                continue

            if 'name' not in metric:
                errors.append(f"{platform}.metrics[{i}] missing 'name'")
            if 'value' not in metric:
                errors.append(f"{platform}.metrics[{i}] missing 'value'")

            # Check for invalid negative values
            value = metric.get('value')
            if isinstance(value, (int, float)) and value < 0:
                errors.append(f"{platform}.metrics[{i}] has negative value: {value}")

    return errors


def validate_keywords(data: dict) -> list[str]:
    """Validate keyword structure."""
    errors = []
    keywords = data.get('keywords', {})

    if not keywords:
        return errors

    top_keywords = keywords.get('topKeywords', [])
    if not isinstance(top_keywords, list):
        errors.append("keywords.topKeywords must be a list")
    else:
        for i, kw in enumerate(top_keywords):
            if not isinstance(kw, dict):
                errors.append(f"keywords.topKeywords[{i}] must be an object")
                continue
            if 'keyword' not in kw:
                errors.append(f"keywords.topKeywords[{i}] missing 'keyword'")
            if 'impressions' in kw:
                imp = kw['impressions']
                if isinstance(imp, (int, float)) and imp < 0:
                    errors.append(f"keywords.topKeywords[{i}] has negative impressions")

    cat_dist = keywords.get('categoryDistribution', [])
    if cat_dist and not isinstance(cat_dist, list):
        errors.append("keywords.categoryDistribution must be a list")

    return errors


def validate_recommendations(data: dict) -> list[str]:
    """Validate recommendations structure."""
    errors = []
    recommendations = data.get('recommendations', [])

    if not isinstance(recommendations, list):
        errors.append("recommendations must be a list")
        return errors

    for i, rec in enumerate(recommendations):
        if not isinstance(rec, dict):
            errors.append(f"recommendations[{i}] must be an object")
            continue
        if 'title' not in rec:
            errors.append(f"recommendations[{i}] missing 'title'")
        if 'description' not in rec:
            errors.append(f"recommendations[{i}] missing 'description'")

    return errors


def validate_date_format(data: dict) -> list[str]:
    """Check date fields have valid format."""
    errors = []
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}|[A-Z][a-z]+ \d{1,2}.*\d{4}')

    date_range = data.get('dateRange', '')
    if date_range and not date_pattern.search(date_range):
        errors.append(f"dateRange format may be invalid: {date_range}")

    return errors


def validate_report_data(data: dict) -> list[str]:
    """Run all validations and return list of errors."""
    errors = []

    errors.extend(validate_required_fields(data))
    errors.extend(validate_kpis(data))
    errors.extend(validate_rating(data))
    errors.extend(validate_sentiment(data))
    errors.extend(validate_metrics(data))
    errors.extend(validate_keywords(data))
    errors.extend(validate_recommendations(data))
    errors.extend(validate_date_format(data))

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_report_data.py <data.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)

    errors = validate_report_data(data)

    if errors:
        print(f"Validation FAILED ({len(errors)} error(s)):\n")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Validation PASSED: All checks passed")
        sys.exit(0)


if __name__ == '__main__':
    main()
