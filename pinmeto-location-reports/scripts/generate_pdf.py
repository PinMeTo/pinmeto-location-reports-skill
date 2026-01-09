#!/usr/bin/env python3
"""
PinMeTo Location Analytics PDF Report Generator

Generates professional PDF reports from PinMeTo analytics data with brand styling.

Usage:
    python generate_pdf.py --data report_data.json --output report.pdf --period monthly

Dependencies:
    pip install reportlab pillow

Author: PinMeTo
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# Auto-detect paths relative to script location
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
DEFAULT_LOGO = ASSETS_DIR / "logos" / "PinMeTo_Logo_Landscape.jpg"

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie


# =============================================================================
# PinMeTo Brand Colors
# =============================================================================
PINMETO_BLUE = colors.HexColor('#3399FF')
PINMETO_ORANGE = colors.HexColor('#FF8854')
PINMETO_BLUE_MARINE = colors.HexColor('#001334')
PINMETO_LIGHT_BLUE = colors.HexColor('#bbd9fa')
PINMETO_GREY = colors.HexColor('#F2F3F4')
PINMETO_MID_GREY = colors.HexColor('#333333')

# Chart colors cycle
CHART_COLORS = [PINMETO_BLUE, PINMETO_ORANGE, PINMETO_LIGHT_BLUE, PINMETO_MID_GREY]


# =============================================================================
# Custom Styles
# =============================================================================
def get_pinmeto_styles():
    """Create PinMeTo branded paragraph styles."""
    styles = getSampleStyleSheet()

    # Title style (left-aligned for cover page consistency)
    styles.add(ParagraphStyle(
        name='PinMeToTitle',
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=PINMETO_BLUE_MARINE,
        alignment=TA_LEFT,
        spaceAfter=20,
    ))

    # Heading 1
    styles.add(ParagraphStyle(
        name='PinMeToH1',
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=PINMETO_BLUE,
        spaceBefore=20,
        spaceAfter=12,
    ))

    # Heading 2
    styles.add(ParagraphStyle(
        name='PinMeToH2',
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=PINMETO_BLUE_MARINE,
        spaceBefore=16,
        spaceAfter=8,
    ))

    # Body text
    styles.add(ParagraphStyle(
        name='PinMeToBody',
        fontName='Helvetica',
        fontSize=10,
        textColor=PINMETO_MID_GREY,
        spaceBefore=6,
        spaceAfter=6,
        leading=14,
    ))

    # KPI highlight
    styles.add(ParagraphStyle(
        name='PinMeToKPI',
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=PINMETO_BLUE,
        alignment=TA_CENTER,
    ))

    # KPI label
    styles.add(ParagraphStyle(
        name='PinMeToKPILabel',
        fontName='Helvetica',
        fontSize=9,
        textColor=PINMETO_MID_GREY,
        alignment=TA_CENTER,
    ))

    return styles


# =============================================================================
# Table Styling
# =============================================================================
def get_data_table_style():
    """Standard data table styling."""
    return TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), PINMETO_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),

        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, PINMETO_GREY]),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, PINMETO_LIGHT_BLUE),
    ])


def get_kpi_table_style():
    """KPI summary table styling."""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PINMETO_GREY),
        ('BOX', (0, 0), (-1, -1), 1, PINMETO_LIGHT_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ])


# =============================================================================
# Chart Creation
# =============================================================================
def create_line_chart(data: list[dict], width=400, height=200) -> Drawing:
    """Create a branded line chart. Returns empty Drawing if data is invalid."""
    drawing = Drawing(width, height)

    # Guard against empty or invalid data
    if not data or not isinstance(data, list):
        return drawing

    chart = HorizontalLineChart()
    chart.x = 50
    chart.y = 30
    chart.width = width - 80
    chart.height = height - 60

    # Extract data
    labels = [d.get('label', '') for d in data]
    values = [d.get('value', 0) for d in data]

    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontName = 'Helvetica'
    chart.categoryAxis.labels.fontSize = 8
    chart.valueAxis.labels.fontName = 'Helvetica'
    chart.valueAxis.labels.fontSize = 8

    # Styling
    chart.lines[0].strokeColor = PINMETO_BLUE
    chart.lines[0].strokeWidth = 2

    drawing.add(chart)
    return drawing


def create_bar_chart(data: list[dict], width=400, height=200) -> Drawing:
    """Create a branded bar chart with optional comparison period. Returns empty Drawing if data is invalid."""
    drawing = Drawing(width, height)

    # Guard against empty or invalid data
    if not data or not isinstance(data, list):
        return drawing

    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 30
    chart.width = width - 80
    chart.height = height - 60

    # Extract data
    labels = [d.get('label', '') for d in data]
    values = [d.get('value', 0) for d in data]
    prior_values = [d.get('priorValue', 0) for d in data]
    has_prior = any(v > 0 for v in prior_values)

    if has_prior:
        chart.data = [values, prior_values]
        chart.bars[0].fillColor = PINMETO_BLUE
        chart.bars[1].fillColor = PINMETO_LIGHT_BLUE
    else:
        chart.data = [values]
        chart.bars[0].fillColor = PINMETO_BLUE

    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontName = 'Helvetica'
    chart.categoryAxis.labels.fontSize = 8
    chart.valueAxis.labels.fontName = 'Helvetica'
    chart.valueAxis.labels.fontSize = 8

    # Add legend if comparison data exists
    if has_prior:
        from reportlab.graphics.charts.legends import Legend
        legend = Legend()
        legend.x = width - 80
        legend.y = height - 5
        legend.fontName = 'Helvetica'
        legend.fontSize = 7
        legend.alignment = 'right'
        legend.columnMaximum = 1
        legend.colorNamePairs = [
            (PINMETO_BLUE, 'Current'),
            (PINMETO_LIGHT_BLUE, 'Prior')
        ]
        drawing.add(legend)

    drawing.add(chart)
    return drawing


def create_pie_chart(data: list[dict], width=300, height=200) -> Drawing:
    """Create a branded pie chart with legend. Returns empty Drawing if data is invalid."""
    drawing = Drawing(width, height)

    # Guard against empty or invalid data
    if not data or not isinstance(data, list):
        return drawing

    pie = Pie()
    pie.x = 50  # Move pie left to make room for legend
    pie.y = 30
    pie.width = 120
    pie.height = 120

    # Extract data
    pie.data = [d.get('value', 0) for d in data]
    pie.labels = None  # Hide slice labels, use legend instead

    # Apply colors
    for i, _ in enumerate(data):
        pie.slices[i].fillColor = CHART_COLORS[i % len(CHART_COLORS)]

    pie.slices.fontName = 'Helvetica'
    pie.slices.fontSize = 8

    drawing.add(pie)

    # Add legend on the right side with proper spacing
    from reportlab.graphics.charts.legends import Legend
    legend = Legend()
    legend.x = 200  # Position to the right of pie chart
    legend.y = height - 60  # Position near top
    legend.fontName = 'Helvetica'
    legend.fontSize = 8
    legend.alignment = 'left'
    legend.columnMaximum = len(data)
    legend.colorNamePairs = [
        (CHART_COLORS[i % len(CHART_COLORS)], d.get('label', ''))
        for i, d in enumerate(data)
    ]
    drawing.add(legend)

    return drawing


# =============================================================================
# Runtime Validation
# =============================================================================
def validate_report_data(data: dict) -> list[str]:
    """
    Validate report data structure and return warnings for missing required fields.
    Prints warnings but allows generation to continue with partial data.
    """
    warnings = []

    # Check top-level required fields
    required_top_level = ['companyName', 'title', 'period']
    for field in required_top_level:
        if not data.get(field):
            warnings.append(f"Missing required field: {field}")

    # Validate KPIs
    kpis = data.get('kpis', [])
    for i, kpi in enumerate(kpis):
        if not kpi.get('name'):
            warnings.append(f"KPI #{i+1}: missing 'name' field (value: {kpi.get('value', 'N/A')})")

    # Validate platform metrics
    for platform in ['google', 'facebook', 'apple']:
        platform_data = data.get(platform, {})
        metrics = platform_data.get('metrics', [])
        for i, metric in enumerate(metrics):
            if not metric.get('name'):
                warnings.append(f"{platform.title()} metric #{i+1}: missing 'name' field (value: {metric.get('value', 'N/A')})")

    # Validate keywords
    keywords_data = data.get('keywords', {})
    top_keywords = keywords_data.get('topKeywords', []) or keywords_data.get('top_keywords', [])
    for i, kw in enumerate(top_keywords):
        if not kw.get('keyword'):
            warnings.append(f"Keyword #{i+1}: missing 'keyword' field")

    # Validate review themes
    reviews_data = data.get('reviews', {})
    themes = reviews_data.get('topThemes', [])
    for i, theme in enumerate(themes):
        if not theme.get('theme'):
            warnings.append(f"Review theme #{i+1}: missing 'theme' field")

    # Print warnings
    if warnings:
        print("\n⚠️  Data Validation Warnings:")
        print("   The following fields are missing or empty. Report will generate with blanks.")
        for warning in warnings:
            print(f"   • {warning}")
        print()

    return warnings


# =============================================================================
# Page Templates
# =============================================================================
def header_footer(canvas, doc, report_title: str, logo_path: str = None, company_name: str = None, period_info: dict = None):
    """Add header and footer to each page."""
    canvas.saveState()

    # Header line
    canvas.setStrokeColor(PINMETO_BLUE)
    canvas.setLineWidth(2)
    canvas.line(50, doc.height + 60, doc.width + 50, doc.height + 60)

    # Header text (company name + report title)
    header_text = f"{company_name} - {report_title}" if company_name else report_title
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(PINMETO_MID_GREY)
    canvas.drawString(50, doc.height + 70, header_text)

    # Logo (if available)
    if logo_path and os.path.exists(logo_path):
        canvas.drawImage(logo_path, doc.width - 50, doc.height + 65, width=80, height=25, preserveAspectRatio=True)

    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(PINMETO_MID_GREY)
    canvas.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")

    # Period info (center of footer)
    if period_info and period_info.get('period'):
        period = period_info.get('period', '')
        prior_period = period_info.get('priorPeriod', '') or period_info.get('prior_period', '')
        period_text = f"{period} vs {prior_period}" if prior_period else period
        canvas.drawCentredString((doc.width + 100) / 2, 30, period_text)

    canvas.drawRightString(doc.width + 50, 30, f"Page {doc.page}")

    # Footer line
    canvas.setStrokeColor(PINMETO_LIGHT_BLUE)
    canvas.setLineWidth(1)
    canvas.line(50, 45, doc.width + 50, 45)

    canvas.restoreState()


# =============================================================================
# Report Sections
# =============================================================================
def create_cover_page(data: dict, styles, logo_path: str = None) -> list:
    """Create the cover page elements with PinMeTo branding."""
    elements = []

    # Logo at top (if available)
    if logo_path and os.path.exists(logo_path):
        # Logo aspect ratio is 2.21:1, use width=120 for ~54pt height
        logo = Image(logo_path, width=120, height=54)
        elements.append(logo)
        elements.append(Spacer(1, 15))

    # Blue accent line
    line_drawing = Drawing(500, 10)
    line_drawing.add(Line(0, 5, 500, 5, strokeColor=PINMETO_BLUE, strokeWidth=2))
    elements.append(line_drawing)

    # Spacer for vertical positioning
    elements.append(Spacer(1, 1.5*inch))

    # Company/Brand name
    company_name = data.get('companyName') or data.get('company_name')
    if company_name:
        elements.append(Paragraph(company_name, styles['PinMeToH2']))
        elements.append(Spacer(1, 15))

    # Report title
    title = data.get('title', 'Location Analytics Report')
    elements.append(Paragraph(title, styles['PinMeToTitle']))
    elements.append(Spacer(1, 10))

    # Period
    period = data.get('period', '')
    if period:
        elements.append(Paragraph(period, styles['PinMeToH2']))

    # Current period date range
    date_range = data.get('dateRange', '') or data.get('date_range', '')
    if date_range:
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Current Period: {date_range}", styles['PinMeToBody']))

    # Prior period date range (for YoY comparison)
    prior_period = data.get('priorPeriod', '') or data.get('prior_period', '')
    prior_date_range = data.get('priorDateRange', '') or data.get('prior_date_range', '')
    if prior_period and prior_date_range:
        elements.append(Paragraph(f"Prior Period ({prior_period}): {prior_date_range}", styles['PinMeToBody']))

    elements.append(Spacer(1, 1.5*inch))

    # Generation date
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
        styles['PinMeToBody']
    ))

    elements.append(Spacer(1, 0.5*inch))

    # Confidentiality notice
    elements.append(Paragraph(
        "Confidential - For Internal Use Only",
        styles['PinMeToBody']
    ))

    elements.append(PageBreak())
    return elements


def create_executive_summary(data: dict, styles) -> list:
    """Create executive summary section."""
    elements = []

    elements.append(Paragraph("Executive Summary", styles['PinMeToH1']))

    # Key highlights
    highlights = data.get('highlights', [])
    if highlights:
        elements.append(Paragraph("Key Highlights", styles['PinMeToH2']))
        for highlight in highlights:
            elements.append(Paragraph(f"• {highlight}", styles['PinMeToBody']))

    # KPI summary table
    kpis = data.get('kpis', [])
    if kpis:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Performance Summary", styles['PinMeToH2']))

        # Create KPI cards as table
        kpi_data = [['Metric', 'Value', 'Change']]
        for kpi in kpis:
            kpi_data.append([
                kpi.get('name', ''),
                kpi.get('value', ''),
                kpi.get('change', '')
            ])

        table = Table(kpi_data, colWidths=[200, 100, 100])
        table.setStyle(get_data_table_style())
        elements.append(table)

    elements.append(PageBreak())
    return elements


def create_metrics_section(data: dict, platform: str, styles) -> list:
    """Create platform-specific metrics section."""
    elements = []

    platform_data = data.get(platform, {})
    if not platform_data:
        return elements

    # Proper platform display names
    platform_names = {
        'google': 'Google Business Profile',
        'facebook': 'Facebook',
        'apple': 'Apple Maps'
    }
    display_name = platform_names.get(platform, platform.title())

    elements.append(Paragraph(f"{display_name} Performance", styles['PinMeToH1']))
    elements.append(Spacer(1, 15))

    # Metrics table
    metrics = platform_data.get('metrics', [])
    if metrics:
        table_data = [['Metric', 'Value', 'vs Prior Period', 'vs Prior Year']]
        for metric in metrics:
            table_data.append([
                metric.get('name', ''),
                str(metric.get('value', '')),
                metric.get('periodChange', '') or metric.get('period_change', 'N/A'),
                metric.get('yearChange', '') or metric.get('year_change', 'N/A')
            ])

        table = Table(table_data, colWidths=[150, 80, 100, 100])
        table.setStyle(get_data_table_style())
        elements.append(table)

    # Chart if data available
    chart_data = platform_data.get('chartData', []) or platform_data.get('chart_data', [])
    if chart_data:
        elements.append(Spacer(1, 40))
        chart = create_bar_chart(chart_data)
        elements.append(chart)

    elements.append(PageBreak())
    return elements


def create_keywords_section(data: dict, styles) -> list:
    """Create keywords analysis section."""
    elements = []

    keywords_data = data.get('keywords', {})
    if not keywords_data:
        return elements

    elements.append(Paragraph("Search Keywords Analysis", styles['PinMeToH1']))
    elements.append(Spacer(1, 15))

    # Top keywords table
    top_keywords = keywords_data.get('topKeywords', []) or keywords_data.get('top_keywords', [])
    if top_keywords:
        elements.append(Paragraph("Top Keywords", styles['PinMeToH2']))
        elements.append(Spacer(1, 10))

        table_data = [['Rank', 'Keyword', 'Impressions', 'Category']]
        for i, kw in enumerate(top_keywords, 1):
            table_data.append([
                str(i),
                kw.get('keyword', ''),
                str(kw.get('impressions', '')),
                kw.get('category', '')
            ])

        table = Table(table_data, colWidths=[50, 200, 80, 100])
        table.setStyle(get_data_table_style())
        elements.append(table)

    # Category distribution - wrap header and chart together to prevent orphaning
    categories = keywords_data.get('categoryDistribution', []) or keywords_data.get('category_distribution', [])
    if categories:
        elements.append(Spacer(1, 40))
        category_section = [
            Paragraph("Category Distribution", styles['PinMeToH2']),
            Spacer(1, 10),
            create_pie_chart(categories)
        ]
        elements.append(KeepTogether(category_section))

    elements.append(PageBreak())
    return elements


def create_reviews_section(data: dict, styles) -> list:
    """Create reviews and sentiment analysis section."""
    elements = []

    reviews_data = data.get('reviews', {})
    if not reviews_data:
        return elements

    elements.append(Paragraph("Review Sentiment Analysis", styles['PinMeToH1']))
    elements.append(Spacer(1, 15))

    # Summary stats
    total = reviews_data.get('totalReviews', 0)
    avg_rating = reviews_data.get('averageRating', 0)
    rating_change = reviews_data.get('ratingChange', '')

    elements.append(Paragraph(
        f"<b>Total Reviews:</b> {total:,} | <b>Average Rating:</b> {avg_rating} ({rating_change})",
        styles['PinMeToBody']
    ))
    elements.append(Spacer(1, 25))

    # Sentiment distribution pie chart
    sentiment = reviews_data.get('sentiment', {})
    if sentiment:
        elements.append(Paragraph("Sentiment Distribution", styles['PinMeToH2']))
        elements.append(Spacer(1, 10))
        sentiment_data = [
            {'label': 'Positive', 'value': sentiment.get('positive', 0)},
            {'label': 'Neutral', 'value': sentiment.get('neutral', 0)},
            {'label': 'Negative', 'value': sentiment.get('negative', 0)},
        ]
        chart = create_pie_chart(sentiment_data)
        elements.append(chart)
        elements.append(Spacer(1, 30))

    # Top themes table - wrap header and table together to prevent orphaning
    themes = reviews_data.get('topThemes', [])
    if themes:
        table_data = [['Theme', 'Mentions', 'Sentiment']]
        for theme in themes:
            table_data.append([
                theme.get('theme', ''),
                str(theme.get('mentions', '')),
                theme.get('sentiment', '').title()
            ])
        table = Table(table_data, colWidths=[150, 80, 100])
        table.setStyle(get_data_table_style())
        themes_section = [
            Paragraph("Top Review Themes", styles['PinMeToH2']),
            Spacer(1, 10),
            table
        ]
        elements.append(KeepTogether(themes_section))

    elements.append(PageBreak())
    return elements


def create_recommendations_section(data: dict, styles) -> list:
    """Create recommendations section."""
    elements = []

    recommendations = data.get('recommendations', [])
    if not recommendations:
        return elements

    elements.append(Paragraph("Strategic Recommendations", styles['PinMeToH1']))

    for i, rec in enumerate(recommendations, 1):
        # Wrap each recommendation to keep title, description, and impact together
        rec_elements = [
            Paragraph(
                f"<b>{i}. {rec.get('title', '')}</b>",
                styles['PinMeToH2']
            ),
            Paragraph(rec.get('description', ''), styles['PinMeToBody'])
        ]

        impact = rec.get('impact', '')
        if impact:
            rec_elements.append(Paragraph(f"<i>Expected Impact: {impact}</i>", styles['PinMeToBody']))

        rec_elements.append(Spacer(1, 10))
        elements.append(KeepTogether(rec_elements))

    return elements


# =============================================================================
# Main Generation Function
# =============================================================================
def generate_report(data: dict, output_path: str, logo_path: str = None):
    """
    Generate a complete PDF report.

    Args:
        data: Report data dictionary with sections
        output_path: Path to save the PDF
        logo_path: Optional path to logo image (uses default if not provided)
    """
    # Validate data and print warnings for missing fields
    validate_report_data(data)

    # Use default logo if not provided
    if logo_path is None and DEFAULT_LOGO.exists():
        logo_path = str(DEFAULT_LOGO)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=80,
        bottomMargin=60
    )

    styles = get_pinmeto_styles()
    elements = []

    # Cover page
    elements.extend(create_cover_page(data, styles, logo_path))

    # Executive summary
    elements.extend(create_executive_summary(data, styles))

    # Google metrics
    elements.extend(create_metrics_section(data, 'google', styles))

    # Facebook metrics
    elements.extend(create_metrics_section(data, 'facebook', styles))

    # Apple metrics
    elements.extend(create_metrics_section(data, 'apple', styles))

    # Keywords
    elements.extend(create_keywords_section(data, styles))

    # Reviews and Sentiment
    elements.extend(create_reviews_section(data, styles))

    # Recommendations
    elements.extend(create_recommendations_section(data, styles))

    # Build PDF with header/footer
    report_title = data.get('title', 'Location Analytics Report')
    company_name = data.get('companyName') or data.get('company_name')
    period_info = {
        'period': data.get('period', ''),
        'priorPeriod': data.get('priorPeriod', '') or data.get('prior_period', '')
    }
    doc.build(
        elements,
        onFirstPage=lambda c, d: None,  # No header on cover
        onLaterPages=lambda c, d: header_footer(c, d, report_title, logo_path, company_name, period_info)
    )

    print(f"Report generated: {output_path}")


# =============================================================================
# CLI Interface
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description='Generate PinMeTo PDF Report')
    parser.add_argument('--data', required=True, help='Path to report data JSON')
    parser.add_argument('--output', required=True, help='Output PDF path')
    parser.add_argument('--logo', help='Path to logo image')
    parser.add_argument('--period', choices=['monthly', 'quarterly', 'half-yearly', 'yearly'],
                        default='monthly', help='Report period type')

    args = parser.parse_args()

    # Load data with error handling
    try:
        with open(args.data, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found: {args.data}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.data}: {e}")
        return 1

    # Add period if not in data
    if 'period_type' not in data:
        data['period_type'] = args.period

    # Generate report with error handling
    try:
        generate_report(data, args.output, args.logo)
        return 0
    except PermissionError:
        print(f"Error: Cannot write to {args.output} - permission denied")
        return 1
    except Exception as e:
        print(f"Error generating report: {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
