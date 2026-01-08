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

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String
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

    # Title style
    styles.add(ParagraphStyle(
        name='PinMeToTitle',
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=PINMETO_BLUE_MARINE,
        alignment=TA_CENTER,
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
    """Create a branded line chart."""
    drawing = Drawing(width, height)

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
    """Create a branded bar chart."""
    drawing = Drawing(width, height)

    chart = VerticalBarChart()
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

    # Bar styling
    chart.bars[0].fillColor = PINMETO_BLUE

    drawing.add(chart)
    return drawing


def create_pie_chart(data: list[dict], width=300, height=200) -> Drawing:
    """Create a branded pie chart."""
    drawing = Drawing(width, height)

    pie = Pie()
    pie.x = 100
    pie.y = 30
    pie.width = 120
    pie.height = 120

    # Extract data
    pie.data = [d.get('value', 0) for d in data]
    pie.labels = [d.get('label', '') for d in data]

    # Apply colors
    for i, _ in enumerate(data):
        pie.slices[i].fillColor = CHART_COLORS[i % len(CHART_COLORS)]

    pie.slices.fontName = 'Helvetica'
    pie.slices.fontSize = 8

    drawing.add(pie)
    return drawing


# =============================================================================
# Page Templates
# =============================================================================
def header_footer(canvas, doc, report_title: str, logo_path: str = None):
    """Add header and footer to each page."""
    canvas.saveState()

    # Header line
    canvas.setStrokeColor(PINMETO_BLUE)
    canvas.setLineWidth(2)
    canvas.line(50, doc.height + 60, doc.width + 50, doc.height + 60)

    # Header text
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(PINMETO_MID_GREY)
    canvas.drawString(50, doc.height + 70, report_title)

    # Logo (if available)
    if logo_path and os.path.exists(logo_path):
        canvas.drawImage(logo_path, doc.width - 50, doc.height + 65, width=80, height=25, preserveAspectRatio=True)

    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(PINMETO_MID_GREY)
    canvas.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    canvas.drawRightString(doc.width + 50, 30, f"Page {doc.page}")

    # Footer line
    canvas.setStrokeColor(PINMETO_LIGHT_BLUE)
    canvas.setLineWidth(1)
    canvas.line(50, 45, doc.width + 50, 45)

    canvas.restoreState()


# =============================================================================
# Report Sections
# =============================================================================
def create_cover_page(data: dict, styles) -> list:
    """Create the cover page elements."""
    elements = []

    # Spacer for vertical centering
    elements.append(Spacer(1, 2*inch))

    # Report title
    title = data.get('title', 'Location Analytics Report')
    elements.append(Paragraph(title, styles['PinMeToTitle']))

    # Period
    period = data.get('period', '')
    if period:
        elements.append(Paragraph(period, styles['PinMeToH2']))

    # Date range
    date_range = data.get('date_range', '')
    if date_range:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(date_range, styles['PinMeToBody']))

    elements.append(Spacer(1, 2*inch))

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

    elements.append(Paragraph(f"{platform} Performance", styles['PinMeToH1']))

    # Metrics table
    metrics = platform_data.get('metrics', [])
    if metrics:
        table_data = [['Metric', 'Value', 'vs Prior Period', 'vs Prior Year']]
        for metric in metrics:
            table_data.append([
                metric.get('name', ''),
                str(metric.get('value', '')),
                metric.get('period_change', 'N/A'),
                metric.get('year_change', 'N/A')
            ])

        table = Table(table_data, colWidths=[150, 80, 100, 100])
        table.setStyle(get_data_table_style())
        elements.append(table)

    # Chart if data available
    chart_data = platform_data.get('chart_data', [])
    if chart_data:
        elements.append(Spacer(1, 20))
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

    # Top keywords table
    top_keywords = keywords_data.get('top_keywords', [])
    if top_keywords:
        elements.append(Paragraph("Top Keywords", styles['PinMeToH2']))

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

    # Category distribution
    categories = keywords_data.get('category_distribution', [])
    if categories:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Category Distribution", styles['PinMeToH2']))
        chart = create_pie_chart(categories)
        elements.append(chart)

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
        elements.append(Paragraph(
            f"<b>{i}. {rec.get('title', '')}</b>",
            styles['PinMeToH2']
        ))
        elements.append(Paragraph(rec.get('description', ''), styles['PinMeToBody']))

        impact = rec.get('impact', '')
        if impact:
            elements.append(Paragraph(f"<i>Expected Impact: {impact}</i>", styles['PinMeToBody']))

        elements.append(Spacer(1, 10))

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
        logo_path: Optional path to logo image
    """
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
    elements.extend(create_cover_page(data, styles))

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

    # Recommendations
    elements.extend(create_recommendations_section(data, styles))

    # Build PDF with header/footer
    report_title = data.get('title', 'Location Analytics Report')
    doc.build(
        elements,
        onFirstPage=lambda c, d: None,  # No header on cover
        onLaterPages=lambda c, d: header_footer(c, d, report_title, logo_path)
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

    # Load data
    with open(args.data, 'r') as f:
        data = json.load(f)

    # Add period if not in data
    if 'period_type' not in data:
        data['period_type'] = args.period

    # Generate report
    generate_report(data, args.output, args.logo)


if __name__ == '__main__':
    main()
