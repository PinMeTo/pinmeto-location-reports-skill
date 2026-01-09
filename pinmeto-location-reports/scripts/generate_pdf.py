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
import io
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for PDF generation
import matplotlib.pyplot as plt

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
# Helper Functions
# =============================================================================
def get_previous_quarter(period):
    """Derive previous quarter from current period string like 'Q4 2025' -> 'Q3 2025'."""
    import re
    match = re.match(r'Q(\d)\s+(\d{4})', period)
    if not match:
        return "Prior Period"
    quarter = int(match.group(1))
    year = int(match.group(2))
    if quarter == 1:
        return f"Q4 {year - 1}"
    else:
        return f"Q{quarter - 1} {year}"


# =============================================================================
# PinMeTo Brand Colors
# =============================================================================
PINMETO_BLUE = colors.HexColor('#3399FF')
PINMETO_ORANGE = colors.HexColor('#FF8854')
PINMETO_BLUE_MARINE = colors.HexColor('#001334')
PINMETO_LIGHT_BLUE = colors.HexColor('#bbd9fa')
PINMETO_GREY = colors.HexColor('#F2F3F4')
PINMETO_MID_GREY = colors.HexColor('#333333')
PINMETO_GREEN = colors.HexColor('#28a745')  # For positive changes

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

    # Narrative/summary text
    styles.add(ParagraphStyle(
        name='PinMeToNarrative',
        fontName='Helvetica',
        fontSize=11,
        textColor=PINMETO_BLUE_MARINE,
        spaceBefore=10,
        spaceAfter=15,
        leading=16,
    ))

    # Insight bullet point
    styles.add(ParagraphStyle(
        name='PinMeToInsight',
        fontName='Helvetica',
        fontSize=9,
        textColor=PINMETO_MID_GREY,
        spaceBefore=3,
        spaceAfter=3,
        leading=12,
    ))

    # Appendix section header
    styles.add(ParagraphStyle(
        name='PinMeToAppendixH2',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=PINMETO_BLUE,
        spaceBefore=12,
        spaceAfter=6,
    ))

    # Appendix body text (smaller)
    styles.add(ParagraphStyle(
        name='PinMeToAppendixBody',
        fontName='Helvetica',
        fontSize=9,
        textColor=PINMETO_MID_GREY,
        spaceBefore=2,
        spaceAfter=2,
        leading=11,
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


def create_bar_chart(data: list[dict], width=400, height=200, current_label=None, prior_label=None) -> Drawing:
    """Create a branded bar chart with optional comparison period. Returns empty Drawing if data is invalid."""
    drawing = Drawing(width, height)

    # Guard against empty or invalid data
    if not data or not isinstance(data, list):
        return drawing

    # Use actual period names if provided
    current_legend = current_label or 'Current'
    prior_legend = prior_label or 'Prior'

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
            (PINMETO_BLUE, current_legend),
            (PINMETO_LIGHT_BLUE, prior_legend)
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

    # Scale pie size based on available width
    if width < 220:
        # Compact layout for narrow containers (e.g., keywords section)
        pie_size = 70
        pie_x = 10
        legend_x = pie_x + pie_size + 15  # 15pt gap after pie
    else:
        # Standard layout
        pie_size = 120
        pie_x = 50
        legend_x = 200

    pie = Pie()
    pie.x = pie_x
    pie.y = (height - pie_size) // 2  # Center vertically
    pie.width = pie_size
    pie.height = pie_size

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
    legend.x = legend_x
    legend.y = height - 50  # Position near top
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


def generate_bar_chart_image(data: list[dict], width=450, height=220, current_label=None, prior_label=None, value_name=None) -> io.BytesIO:
    """
    Generate bar chart using matplotlib (matches PPTX approach).
    Returns BytesIO buffer with PNG image, or None if data is invalid.

    Args:
        value_name: Label describing what the values represent (e.g., "Profile Views")
    """
    if not data or not isinstance(data, list):
        return None

    labels = [d.get('label', '') for d in data]
    values = [d.get('value', 0) for d in data]
    prior_values = [d.get('priorValue', 0) for d in data]
    has_prior = any(v > 0 for v in prior_values)

    # Create figure with extra height for legend below
    fig, ax = plt.subplots(figsize=(width / 72, height / 72), dpi=150)

    x = list(range(len(labels)))
    bar_width = 0.35 if has_prior else 0.5

    # Draw current period bars
    if has_prior:
        bars1 = ax.bar([i - bar_width / 2 for i in x], values, bar_width,
                       label=current_label or 'Current', color='#3399FF')
        bars2 = ax.bar([i + bar_width / 2 for i in x], prior_values, bar_width,
                       label=prior_label or 'Prior', color='#bbd9fa')
    else:
        bars1 = ax.bar(x, values, bar_width, label=current_label or 'Current', color='#3399FF')
        bars2 = None

    # Add value labels above current period bars
    for bar in bars1:
        height_val = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height_val,
                f'{int(height_val):,}', ha='center', va='bottom', fontsize=7,
                color='#001334')

    # Add value labels above prior period bars if present
    if bars2:
        for bar in bars2:
            height_val = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height_val,
                    f'{int(height_val):,}', ha='center', va='bottom', fontsize=7,
                    color='#666666')

    # Style the chart
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.tick_params(axis='y', labelsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add title showing what value is displayed
    if value_name:
        ax.set_title(value_name, fontsize=10, color='#001334', fontweight='bold', pad=10)

    # Legend below the chart
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=8, frameon=False)

    plt.tight_layout(rect=[0, 0.08, 1, 1])  # Leave room for legend below

    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buf.seek(0)
    plt.close(fig)

    return buf


def create_kpi_cards(kpis: list, width=400) -> Drawing:
    """
    Create a 2x2 grid of KPI cards matching PPTX style.

    Each card shows:
    - Large value in blue
    - Metric name in grey
    - Change indicator in green/orange
    """
    if not kpis:
        return Drawing(width, 10)

    # Card dimensions
    card_width = 180
    card_height = 75
    gap = 15

    # Calculate total drawing dimensions
    total_width = card_width * 2 + gap
    total_height = card_height * 2 + gap

    drawing = Drawing(total_width, total_height)

    for i, kpi in enumerate(kpis[:4]):
        col = i % 2
        row = i // 2

        # Position: ReportLab y is bottom-up, so row 0 is at top
        x = col * (card_width + gap)
        y = total_height - (row + 1) * (card_height + gap) + gap

        # Card background with rounded corners effect (using Rect)
        rect = Rect(x, y, card_width, card_height)
        rect.fillColor = PINMETO_GREY
        rect.strokeColor = PINMETO_LIGHT_BLUE
        rect.strokeWidth = 1
        rect.rx = 5  # Rounded corners
        rect.ry = 5
        drawing.add(rect)

        # KPI value (centered, large blue text)
        value = kpi.get('value', 'N/A')
        value_text = String(
            x + card_width / 2,
            y + card_height - 28,
            str(value),
            fontSize=22,
            fontName='Helvetica-Bold',
            fillColor=PINMETO_BLUE,
            textAnchor='middle'
        )
        drawing.add(value_text)

        # KPI name (centered, grey text)
        name = kpi.get('name', '')
        name_text = String(
            x + card_width / 2,
            y + card_height / 2 - 8,
            name,
            fontSize=9,
            fontName='Helvetica',
            fillColor=PINMETO_MID_GREY,
            textAnchor='middle'
        )
        drawing.add(name_text)

        # KPI change (centered, colored based on positive/negative)
        change = kpi.get('change', '')
        if change:
            # Determine color based on change direction
            if change.startswith('-'):
                change_color = PINMETO_ORANGE
            else:
                change_color = PINMETO_GREEN

            change_text = String(
                x + card_width / 2,
                y + 12,
                change,
                fontSize=10,
                fontName='Helvetica',
                fillColor=change_color,
                textAnchor='middle'
            )
            drawing.add(change_text)

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
# Draft Watermark
# =============================================================================
def draw_draft_watermark(canvas, doc):
    """Draw a diagonal 'DRAFT - PENDING REVIEW' watermark across the page."""
    canvas.saveState()

    # Semi-transparent gray text
    canvas.setFillColor(colors.Color(0.7, 0.7, 0.7, alpha=0.4))
    canvas.setFont('Helvetica-Bold', 60)

    # Center of the page
    page_width, page_height = doc.pagesize
    center_x = page_width / 2
    center_y = page_height / 2

    # Rotate and draw text at center
    canvas.translate(center_x, center_y)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "DRAFT - PENDING REVIEW")

    canvas.restoreState()


# =============================================================================
# Page Templates
# =============================================================================
def header_footer(canvas, doc, report_title: str, logo_path: str = None, company_name: str = None, period_info: dict = None, is_draft: bool = False):
    """Add header and footer to each page."""
    canvas.saveState()

    # Draw draft watermark if in draft mode
    if is_draft:
        draw_draft_watermark(canvas, doc)

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
    """Create executive summary section with narrative, highlights, and KPIs."""
    elements = []

    elements.append(Paragraph("Executive Summary", styles['PinMeToH1']))

    # Executive summary narrative (new format)
    exec_summary = data.get('executiveSummary', {})
    narrative = exec_summary.get('narrative', '')
    if narrative:
        elements.append(Paragraph(narrative, styles['PinMeToNarrative']))

    # Structured highlights with title + description (new format)
    structured_highlights = exec_summary.get('highlights', [])
    if structured_highlights:
        elements.append(Paragraph("Quarter Highlights", styles['PinMeToH2']))
        for highlight in structured_highlights:
            title = highlight.get('title', '')
            description = highlight.get('description', '')
            if title and description:
                elements.append(Paragraph(
                    f"• <b>{title}:</b> {description}",
                    styles['PinMeToBody']
                ))
            elif title:
                elements.append(Paragraph(f"• <b>{title}</b>", styles['PinMeToBody']))
    else:
        # Fallback to legacy highlights format
        highlights = data.get('highlights', [])
        if highlights:
            elements.append(Paragraph("Key Highlights", styles['PinMeToH2']))
            for highlight in highlights:
                elements.append(Paragraph(f"• {highlight}", styles['PinMeToBody']))

    # KPI summary cards (2x2 grid matching PPTX style)
    kpis = data.get('kpis', [])
    if kpis:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Performance Metrics", styles['PinMeToH2']))
        elements.append(Spacer(1, 10))
        elements.append(create_kpi_cards(kpis))

    elements.append(PageBreak())
    return elements


def create_section_insights(insights: list, styles) -> list:
    """Create a key insights box for a section."""
    elements = []
    if not insights:
        return elements

    elements.append(Paragraph("Key Insights", styles['PinMeToH2']))

    # Create insights as styled bullet points
    for insight in insights:
        elements.append(Paragraph(f"• {insight}", styles['PinMeToInsight']))

    elements.append(Spacer(1, 15))
    return elements


def create_metrics_section(data: dict, platform: str, styles, period_info: dict = None) -> list:
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

    # Key insights for this platform
    insights = platform_data.get('insights', [])
    elements.extend(create_section_insights(insights, styles))

    elements.append(Spacer(1, 10))

    # Get period names for table headers
    period_info = period_info or {}
    current_period = period_info.get('period', 'Current')
    prior_year_period = period_info.get('priorPeriod', 'Prior Year')
    previous_quarter = get_previous_quarter(current_period)

    # Metrics table with actual period names
    metrics = platform_data.get('metrics', [])
    if metrics:
        table_data = [['Metric', current_period, f'vs {previous_quarter}', f'vs {prior_year_period}']]
        for metric in metrics:
            table_data.append([
                metric.get('name', ''),
                str(metric.get('value', '')),
                metric.get('periodChange', '') or metric.get('period_change', 'N/A'),
                metric.get('yearChange', '') or metric.get('year_change', 'N/A')
            ])

        table = Table(table_data, colWidths=[160, 100, 115, 115])
        table.setStyle(get_data_table_style())
        elements.append(table)

    # Chart if data available (compares to prior year same period)
    # Uses matplotlib for better rendering with value labels above bars
    chart_data = platform_data.get('chartData', []) or platform_data.get('chart_data', [])
    if chart_data:
        elements.append(Spacer(1, 30))
        # Determine chart title based on platform's primary metric
        chart_titles = {
            'google': 'Profile Views',
            'facebook': 'Page Engagement',
            'apple': 'Discovery Views'
        }
        chart_title = chart_titles.get(platform, 'Monthly Activity')
        chart_image = generate_bar_chart_image(
            chart_data,
            width=450,
            height=220,
            current_label=current_period,
            prior_label=prior_year_period,
            value_name=chart_title
        )
        if chart_image:
            elements.append(Image(chart_image, width=450, height=220))

    elements.append(PageBreak())
    return elements


def create_keywords_section(data: dict, styles) -> list:
    """Create keywords analysis section with table above pie chart."""
    elements = []

    keywords_data = data.get('keywords', {})
    if not keywords_data:
        return elements

    elements.append(Paragraph("Search Keywords Analysis", styles['PinMeToH1']))

    # Key insights for keywords
    insights = keywords_data.get('insights', [])
    elements.extend(create_section_insights(insights, styles))

    elements.append(Spacer(1, 10))

    # Get data for both sections
    top_keywords = keywords_data.get('topKeywords', []) or keywords_data.get('top_keywords', [])
    categories = keywords_data.get('categoryDistribution', []) or keywords_data.get('category_distribution', [])

    # Keywords table
    if top_keywords:
        elements.append(Paragraph("Top Keywords", styles['PinMeToH2']))
        elements.append(Spacer(1, 8))

        # Create a style for wrapped table cells
        cell_style = ParagraphStyle(
            'TableCell',
            fontName='Helvetica',
            fontSize=9,
            leading=11,
            textColor=PINMETO_MID_GREY,
        )

        table_data = [['Rank', 'Keyword', 'Impressions', 'Category']]
        for i, kw in enumerate(top_keywords, 1):
            # Use Paragraph for keyword to enable text wrapping
            keyword_text = kw.get('keyword', '')
            keyword_para = Paragraph(keyword_text, cell_style)
            table_data.append([
                str(i),
                keyword_para,
                f"{kw.get('impressions', 0):,}",
                kw.get('category', '')
            ])

        keywords_table = Table(table_data, colWidths=[40, 220, 100, 130])
        keywords_table.setStyle(get_data_table_style())
        elements.append(keywords_table)

    # Category distribution pie chart below the table
    if categories:
        elements.append(Spacer(1, 25))
        elements.append(Paragraph("Category Distribution", styles['PinMeToH2']))
        elements.append(Spacer(1, 10))
        # Full-width pie chart now that it's not side-by-side
        pie_chart = create_pie_chart(categories, width=350, height=180)
        elements.append(pie_chart)

    elements.append(PageBreak())
    return elements


def create_reviews_section(data: dict, styles) -> list:
    """Create reviews and sentiment analysis section."""
    elements = []

    reviews_data = data.get('reviews', {})
    if not reviews_data:
        return elements

    elements.append(Paragraph("Review Sentiment Analysis", styles['PinMeToH1']))

    # Key insights for reviews
    insights = reviews_data.get('insights', [])
    elements.extend(create_section_insights(insights, styles))

    elements.append(Spacer(1, 10))

    # Summary stats
    total = reviews_data.get('totalReviews', 0)
    avg_rating = reviews_data.get('averageRating', 0)
    rating_change = reviews_data.get('ratingChange', '')

    elements.append(Paragraph(
        f"<b>Total Reviews:</b> {total:,} | <b>Average Rating:</b> {avg_rating} ({rating_change})",
        styles['PinMeToBody']
    ))
    elements.append(Spacer(1, 25))

    # Top themes table first (to match order of other pages: table then chart)
    themes = reviews_data.get('topThemes', [])
    if themes:
        elements.append(Paragraph("Top Review Themes", styles['PinMeToH2']))
        elements.append(Spacer(1, 10))
        table_data = [['Theme', 'Mentions', 'Sentiment']]
        for theme in themes:
            table_data.append([
                theme.get('theme', ''),
                str(theme.get('mentions', '')),
                theme.get('sentiment', '').title()
            ])
        table = Table(table_data, colWidths=[200, 100, 120])
        table.setStyle(get_data_table_style())
        elements.append(table)
        elements.append(Spacer(1, 30))

    # Sentiment distribution pie chart below the table
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


def create_appendix(data: dict, styles) -> list:
    """Create appendix section with data sources, methodology, and location coverage."""
    elements = []

    appendix_data = data.get('appendix', {})
    if not appendix_data:
        return elements

    elements.append(PageBreak())
    elements.append(Paragraph("Appendix: Data & Methodology", styles['PinMeToH1']))
    elements.append(Spacer(1, 15))

    # Data Sources
    data_sources = appendix_data.get('dataSources', [])
    if data_sources:
        elements.append(Paragraph("Data Sources", styles['PinMeToAppendixH2']))
        for source in data_sources:
            elements.append(Paragraph(f"• {source}", styles['PinMeToAppendixBody']))
        elements.append(Spacer(1, 10))

    # Reporting Period
    reporting_period = appendix_data.get('reportingPeriod', {})
    if reporting_period:
        elements.append(Paragraph("Reporting Period", styles['PinMeToAppendixH2']))
        quarter = reporting_period.get('quarter', '')
        date_range = reporting_period.get('dateRange', '')
        data_freshness = reporting_period.get('dataFreshness', '')
        lag_note = reporting_period.get('lagNote', '')

        if quarter:
            elements.append(Paragraph(f"<b>Quarter:</b> {quarter}", styles['PinMeToAppendixBody']))
        if date_range:
            elements.append(Paragraph(f"<b>Date Range:</b> {date_range}", styles['PinMeToAppendixBody']))
        if data_freshness:
            elements.append(Paragraph(f"<b>Data Freshness:</b> As of {data_freshness}", styles['PinMeToAppendixBody']))
        if lag_note:
            elements.append(Paragraph(f"<i>Note: {lag_note}</i>", styles['PinMeToAppendixBody']))
        elements.append(Spacer(1, 10))

    # Calculation Notes
    calc_notes = appendix_data.get('calculationNotes', [])
    if calc_notes:
        elements.append(Paragraph("Calculation Notes", styles['PinMeToAppendixH2']))
        for note in calc_notes:
            elements.append(Paragraph(f"• {note}", styles['PinMeToAppendixBody']))
        elements.append(Spacer(1, 10))

    # Location Coverage
    location_coverage = appendix_data.get('locationCoverage', {})
    if location_coverage:
        elements.append(Paragraph("Location Coverage", styles['PinMeToAppendixH2']))
        total = location_coverage.get('totalLocations', 0)
        geo = location_coverage.get('geographicCoverage', '')
        google_data = location_coverage.get('locationsWithGoogleData', 0)
        reviews = location_coverage.get('locationsWithReviews', 0)

        if total:
            elements.append(Paragraph(f"<b>Total Locations:</b> {total} active locations", styles['PinMeToAppendixBody']))
        if geo:
            elements.append(Paragraph(f"<b>Geographic Coverage:</b> {geo}", styles['PinMeToAppendixBody']))
        if google_data:
            elements.append(Paragraph(f"<b>Locations with Google Data:</b> {google_data} locations", styles['PinMeToAppendixBody']))
        if reviews:
            elements.append(Paragraph(f"<b>Locations with Reviews:</b> {reviews} locations", styles['PinMeToAppendixBody']))

    return elements


# =============================================================================
# Main Generation Function
# =============================================================================
def generate_report(data: dict, output_path: str, logo_path: str = None, is_draft: bool = False):
    """
    Generate a complete PDF report.

    Args:
        data: Report data dictionary with sections
        output_path: Path to save the PDF
        logo_path: Optional path to logo image (uses default if not provided)
        is_draft: If True, adds "DRAFT - PENDING REVIEW" watermark on every page
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

    # Period info for headers and tables
    period_info = {
        'period': data.get('period', ''),
        'priorPeriod': data.get('priorPeriod', '') or data.get('prior_period', '')
    }

    # Cover page
    elements.extend(create_cover_page(data, styles, logo_path))

    # Executive summary
    elements.extend(create_executive_summary(data, styles))

    # Google metrics
    elements.extend(create_metrics_section(data, 'google', styles, period_info))

    # Facebook metrics
    elements.extend(create_metrics_section(data, 'facebook', styles, period_info))

    # Apple metrics
    elements.extend(create_metrics_section(data, 'apple', styles, period_info))

    # Keywords
    elements.extend(create_keywords_section(data, styles))

    # Reviews and Sentiment
    elements.extend(create_reviews_section(data, styles))

    # Recommendations
    elements.extend(create_recommendations_section(data, styles))

    # Appendix (Data & Methodology)
    elements.extend(create_appendix(data, styles))

    # Build PDF with header/footer
    report_title = data.get('title', 'Location Analytics Report')
    company_name = data.get('companyName') or data.get('company_name')

    # Define page handlers - cover page gets watermark but no header, other pages get both
    def on_first_page(c, d):
        if is_draft:
            draw_draft_watermark(c, d)

    def on_later_pages(c, d):
        header_footer(c, d, report_title, logo_path, company_name, period_info, is_draft)

    doc.build(
        elements,
        onFirstPage=on_first_page,
        onLaterPages=on_later_pages
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
    parser.add_argument('--draft', action='store_true',
                        help='Add "DRAFT - PENDING REVIEW" watermark on every page')

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
        generate_report(data, args.output, args.logo, is_draft=args.draft)
        if args.draft:
            print("Note: This is a DRAFT report. Run without --draft flag to generate final version.")
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
