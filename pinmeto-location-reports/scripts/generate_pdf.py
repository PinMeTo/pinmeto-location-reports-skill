#!/usr/bin/env python3
# © 2025 PinMeTo AB. All rights reserved.
# See LICENSE file for full terms.
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
import math
import os
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for PDF generation
import matplotlib.pyplot as plt

# Auto-detect paths relative to script location
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
DEFAULT_LOGO = ASSETS_DIR / "logos" / "PinMeTo_Logo_Landscape.jpg"

def find_logo_path(provided_path=None):
    """Find logo path with fallback for different environments (e.g., Claude Desktop)."""
    candidates = [
        provided_path,  # User-provided path
        str(DEFAULT_LOGO) if DEFAULT_LOGO.exists() else None,  # Default relative to script
        "assets/logos/PinMeTo_Logo_Landscape.jpg",  # CWD relative
        "pinmeto-location-reports/assets/logos/PinMeTo_Logo_Landscape.jpg",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    print(f"Warning: Logo not found. Tried: {[c for c in candidates if c]}")
    return None

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# =============================================================================
# Brand Typeface
# =============================================================================
# Montserrat is the only PinMeTo brand typeface (Graphic Manual, May 2026). The
# TTFs ship in assets/fonts/ under the SIL Open Font License so reports render
# on-brand on a machine that has never installed the font.
#
# Registration is best-effort: a missing or unreadable TTF falls back to
# Helvetica rather than aborting the report. Helvetica is metrically close enough
# that layout holds, but it is NOT brand-compliant, so the fallback announces
# itself on stderr instead of failing silently.
FONTS_DIR = SCRIPT_DIR.parent / "assets" / "fonts"

_MONTSERRAT_FACES = {
    "regular": ("Montserrat", "Montserrat-Regular.ttf"),
    "semibold": ("Montserrat-SemiBold", "Montserrat-SemiBold.ttf"),
    "bold": ("Montserrat-Bold", "Montserrat-Bold.ttf"),
}

_HELVETICA_FALLBACK = {
    "regular": "Helvetica",
    "semibold": "Helvetica-Bold",
    "bold": "Helvetica-Bold",
}


def register_brand_fonts():
    """Register the bundled Montserrat faces, returning the usable font names.

    Returns a dict keyed 'regular'/'semibold'/'bold'. Every face must register
    for the family to be used: a partial registration would mix Montserrat body
    text with Helvetica headings, which looks worse than consistent Helvetica.
    """
    registered = {}
    for weight, (font_name, filename) in _MONTSERRAT_FACES.items():
        path = FONTS_DIR / filename
        if not path.exists():
            print(f"Warning: brand font missing ({path}); falling back to Helvetica.")
            return dict(_HELVETICA_FALLBACK)
        try:
            pdfmetrics.registerFont(TTFont(font_name, str(path)))
        except Exception as exc:  # unreadable/corrupt TTF
            print(f"Warning: could not register {filename} ({exc}); falling back to Helvetica.")
            return dict(_HELVETICA_FALLBACK)
        registered[weight] = font_name

    # Map the bold/italic slots so <b> in Paragraph markup resolves to the bold
    # face instead of reportlab synthesising a smeared fake bold.
    pdfmetrics.registerFontFamily(
        "Montserrat",
        normal="Montserrat",
        bold="Montserrat-Bold",
        italic="Montserrat",
        boldItalic="Montserrat-Bold",
    )
    return registered


BRAND_FONTS = register_brand_fonts()
FONT_REGULAR = BRAND_FONTS["regular"]
FONT_SEMIBOLD = BRAND_FONTS["semibold"]
FONT_BOLD = BRAND_FONTS["bold"]

# matplotlib keeps its own font cache, so the same TTFs are registered again for
# the chart renderer. Without this, charts silently render in DejaVu Sans while
# the surrounding page is Montserrat.
if FONT_REGULAR != "Helvetica":
    from matplotlib import font_manager

    for _face in _MONTSERRAT_FACES.values():
        _face_path = FONTS_DIR / _face[1]
        if _face_path.exists():
            font_manager.fontManager.addfont(str(_face_path))
    plt.rcParams["font.family"] = "Montserrat"


# =============================================================================
# Helper Functions
# =============================================================================
def format_metric_value(value):
    """Format a metric value for display in a table.

    Applies thousands separators so metric tables match the keyword table, the
    chart value labels, and the KPI cards. Without this, a table reads
    '2400000' on the same page as a chart labelled '780,000'.

    Strings pass through untouched: they are already formatted upstream (for
    example the '2.4M' style used on KPI cards, or 'N/A').
    """
    if isinstance(value, bool) or value is None:
        return str(value) if value is not None else ''
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return f'{value:,}'
    if isinstance(value, float):
        # Keep a decimal only when it carries information, so ratings stay 4.3
        # while whole counts do not gain a spurious '.0'.
        if value.is_integer():
            return f'{int(value):,}'
        return f'{value:,.1f}'
    return str(value)


def get_previous_period(period, report_type=None):
    """Derive previous period from current period string.

    Handles multiple formats:
    - Yearly: '2025' -> '2024'
    - Quarterly: 'Q4 2025' -> 'Q3 2025'
    - Monthly: 'October 2025' -> 'September 2025'

    Args:
        period: Period string in various formats
        report_type: Optional hint ('yearly', 'quarterly', 'monthly')

    Returns:
        Previous period string, or None if not applicable
    """
    import re
    if not period:
        return None

    # Try yearly format first (just a year like "2025")
    if re.match(r'^\d{4}$', str(period).strip()):
        year = int(str(period).strip())
        return str(year - 1)

    # Try quarterly format ('Q4 2025')
    match = re.match(r'Q(\d)\s+(\d{4})', str(period))
    if match:
        quarter = int(match.group(1))
        year = int(match.group(2))
        if quarter == 1:
            return f"Q4 {year - 1}"
        else:
            return f"Q{quarter - 1} {year}"

    # Try monthly format ('October 2025' or 'Oct 2025')
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    months_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for i, (month_full, month_short) in enumerate(zip(months, months_short)):
        match = re.match(rf'({month_full}|{month_short})\s+(\d{{4}})', str(period), re.IGNORECASE)
        if match:
            year = int(match.group(2))
            if i == 0:  # January
                return f"{months[11]} {year - 1}"
            else:
                return f"{months[i - 1]} {year}"

    return None


# Accepted spellings for an explicit report type, mapped to the canonical value.
REPORT_TYPE_ALIASES = {
    'monthly': 'monthly',
    'quarterly': 'quarterly',
    'half-yearly': 'half-yearly',
    'half_yearly': 'half-yearly',
    'halfyearly': 'half-yearly',
    'yearly': 'yearly',
    'annual': 'yearly',
}


def get_period_type(data: dict):
    """Read the caller's explicit report type from the data dict.

    Accepts both spellings because the two generators historically wrote
    different keys ('periodType' and 'period_type') and neither read them back.
    """
    if not isinstance(data, dict):
        return None
    return data.get('periodType') or data.get('period_type')


def detect_report_type(period, period_type=None):
    """Resolve the report type, preferring an explicit period type over inference.

    An explicit `--period` is authoritative: it is what the caller asked for.
    Inference from the free-text period label is only a fallback, and it cannot
    recognise half-yearly on its own ('H1 2025' matched no pattern), which
    silently downgraded every half-yearly report to the quarterly layout.

    Returns:
        'yearly', 'quarterly', 'half-yearly', 'monthly', or None
    """
    import re

    if period_type:
        resolved = REPORT_TYPE_ALIASES.get(str(period_type).strip().lower())
        if resolved:
            return resolved

    if not period:
        return None

    # Yearly: just a year
    if re.match(r'^\d{4}$', str(period).strip()):
        return 'yearly'

    # Quarterly: Q1-Q4 YYYY
    if re.match(r'Q\d\s+\d{4}', str(period)):
        return 'quarterly'

    # Half-yearly: H1/H2 YYYY
    if re.match(r'^H[12]\s+\d{4}', str(period).strip(), re.IGNORECASE):
        return 'half-yearly'

    # Monthly: Month name + year
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    for month in months:
        if str(period).lower().startswith(month.lower()[:3]):
            return 'monthly'

    return None


# =============================================================================
# PinMeTo Brand Colors
# =============================================================================
PINMETO_BLUE = colors.HexColor('#3399FF')
PINMETO_ORANGE = colors.HexColor('#FF8854')
PINMETO_NAVY = colors.HexColor('#000050')
PINMETO_LIGHT_BLUE = colors.HexColor('#bbd9fa')
PINMETO_GREY = colors.HexColor('#F2F3F4')
PINMETO_MID_GREY = colors.HexColor('#333333')
PINMETO_GREEN = colors.HexColor('#28a745')  # Deprecated: see STATUS_GOOD

# =============================================================================
# Chart & status tokens
# =============================================================================
# Validated with the dataviz skill's validate_palette.js (light surface).
#
# Categorical trio '#1F7AE0,#E8690B,#5B4B8A' passes all six checks: lightness
# band, chroma floor, CVD separation (worst adjacent dE 25.3 protan), the
# normal-vision floor, and 3:1 contrast against the surface. The brand's own
# #3399FF/#FF8854/#bbd9fa trio FAILED: #bbd9fa sits outside the lightness band
# and under the chroma floor (it reads gray), and both brand hues fall below 3:1.
# These are slightly deepened steps of the brand hues, reserved for data marks;
# PINMETO_BLUE remains the brand accent for headings and rules.
CHART_BLUE = colors.HexColor('#1F7AE0')     # categorical slot 1
CHART_ORANGE = colors.HexColor('#E8690B')   # categorical slot 2
CHART_VIOLET = colors.HexColor('#5B4B8A')   # categorical slot 3

# Prior-period wash. Deliberately recessive: a prior period is the same metric
# earlier, not a separate identity, so it is a de-emphasis step rather than a
# categorical slot (it would fail the categorical chroma floor, correctly).
# Relief comes from the legend plus direct labels on the current series.
CHART_PRIOR = colors.HexColor('#C9DCF3')

# Status tokens, reserved for direction of change and never reused as a series
# color. The previous pair (#28a745 green / #FF8854 orange) measured dE 1.8 under
# protanopia, i.e. indistinguishable to red-green colorblind readers. This pair
# measures dE 9.6 (deutan) and both clear 3:1. Direction is ALSO encoded with a
# triangle glyph, so colour is never the only channel.
STATUS_GOOD = colors.HexColor('#0E7C4A')
STATUS_BAD = colors.HexColor('#CC3311')

# Star rating fill. Conventionally gold, but it has to clear 3:1 against the tile
# surface: brand orange measures 2.3:1 and a lighter gold is worse. This amber
# passes and still reads as a star colour rather than a data hue.
STAR_AMBER = colors.HexColor('#C77700')

# Ink and chrome
INK = PINMETO_NAVY
INK_MUTED = colors.HexColor('#5A6472')
HAIRLINE = colors.HexColor('#DCE3EC')
TILE_SURFACE = colors.HexColor('#F5F8FC')
TABLE_HEADER_BG = colors.HexColor('#EAF2FD')
TABLE_ZEBRA = colors.HexColor('#FAFBFD')

# Platform chart footprint. The text frame is 495pt wide (A4 less 50pt margins),
# so the chart spans it fully rather than leaving a 45pt gutter that made pages
# read as unfinished. Height is set from the space actually free on the shortest
# platform page (the Google section, whose insight list and table run longest):
# 320pt fills it while leaving ~44pt of clearance, so no chart is pushed onto a
# page of its own. Raising this further risks exactly that, which is why it is a
# named constant and not an inline literal.
PLATFORM_CHART_WIDTH = 495
PLATFORM_CHART_HEIGHT = 320

# Categorical order is fixed: slot N always gets the same hue regardless of how
# many slices are present, so a filtered chart never repaints its survivors.
CHART_COLORS = [CHART_BLUE, CHART_ORANGE, CHART_VIOLET, INK_MUTED]

# Diverging/status ramp for sentiment: good -> neutral gray midpoint -> bad.
SENTIMENT_COLORS = [STATUS_GOOD, colors.HexColor('#9AA4B2'), STATUS_BAD]


# Direction glyphs for text contexts (table cells), as opposed to the drawn
# polygon used on the stat tiles. Montserrat carries all three; the base-14
# fallback carries none, hence DIRECTION_GLYPHS_AVAILABLE below.
DELTA_GLYPHS = {1: '▲', -1: '▼', 0: '–'}  # ▲ ▼ –
DIRECTION_GLYPHS_AVAILABLE = FONT_REGULAR != 'Helvetica'
_GLYPH_PREFIX_CHARS = ''.join(DELTA_GLYPHS.values()) + ' \t'


def change_direction(change) -> int:
    """Classify a change string as positive (1), negative (-1), or neutral (0).

    Neutral covers 'N/A', 'No change', empty, and an explicit zero, none of which
    should be painted as a win or a loss.

    Tolerates an already-applied direction glyph so callers may classify a
    decorated cell without having to keep the raw string around.
    """
    if not change:
        return 0
    text = str(change).strip().lstrip(_GLYPH_PREFIX_CHARS).strip()
    if not text or text.upper() in {'N/A', 'NA', '-', '--'}:
        return 0
    if 'no change' in text.lower():
        return 0
    stripped = text.lstrip('+-')
    if stripped and stripped[0].isdigit():
        try:
            if float(stripped.rstrip('% YoYQoQMoMpts').strip() or 0) == 0:
                return 0
        except ValueError:
            pass
    if text.startswith('-'):
        return -1
    if text.startswith('+'):
        return 1
    return 0


def status_color(change):
    """Status colour for a change string, or muted ink when there is no direction."""
    direction = change_direction(change)
    if direction > 0:
        return STATUS_GOOD
    if direction < 0:
        return STATUS_BAD
    return INK_MUTED


def decorate_delta(value):
    """Prefix a change string with its direction glyph.

    Table cells previously carried direction in colour and the +/- sign only,
    while the stat tiles also drew a triangle. That left the tables one channel
    short of the tiles for exactly the readers the triangle exists for.

    Returns the value untouched when the brand font is unavailable: the base-14
    fallback has no triangle glyph and would render a black box, which is worse
    than the sign alone. Also untouched for 'N/A'-style cells, which have no
    direction to report.
    """
    if not DIRECTION_GLYPHS_AVAILABLE or value is None:
        return value
    text = str(value)
    if not text.strip():
        return text
    if text.strip().upper() in {'N/A', 'NA', '-', '--'}:
        return text
    if text.strip()[0] in DELTA_GLYPHS.values():
        return text  # already decorated
    return f"{DELTA_GLYPHS[change_direction(text)]} {text}"


# =============================================================================
# Custom Styles
# =============================================================================
def get_pinmeto_styles():
    """Create PinMeTo branded paragraph styles."""
    styles = getSampleStyleSheet()

    # Title style (left-aligned for cover page consistency)
    styles.add(ParagraphStyle(
        name='PinMeToTitle',
        fontName=FONT_BOLD,
        fontSize=28,
        leading=34,        textColor=PINMETO_NAVY,
        alignment=TA_LEFT,
        spaceAfter=20,
    ))

    # Heading 1
    styles.add(ParagraphStyle(
        name='PinMeToH1',
        fontName=FONT_BOLD,
        fontSize=18,
        leading=22,        textColor=PINMETO_BLUE,
        spaceBefore=20,
        spaceAfter=12,
    ))

    # Heading 2
    styles.add(ParagraphStyle(
        name='PinMeToH2',
        fontName=FONT_BOLD,
        fontSize=14,
        leading=18,        textColor=PINMETO_NAVY,
        spaceBefore=16,
        spaceAfter=8,
    ))

    # Body text
    styles.add(ParagraphStyle(
        name='PinMeToBody',
        fontName=FONT_REGULAR,
        fontSize=10,
        textColor=PINMETO_MID_GREY,
        spaceBefore=6,
        spaceAfter=6,
        leading=14,
    ))

    # KPI highlight
    styles.add(ParagraphStyle(
        name='PinMeToKPI',
        fontName=FONT_BOLD,
        fontSize=24,
        leading=28,        textColor=PINMETO_BLUE,
        alignment=TA_CENTER,
    ))

    # KPI label
    styles.add(ParagraphStyle(
        name='PinMeToKPILabel',
        fontName=FONT_REGULAR,
        fontSize=9,
        leading=11,        textColor=PINMETO_MID_GREY,
        alignment=TA_CENTER,
    ))

    # Narrative/summary text
    styles.add(ParagraphStyle(
        name='PinMeToNarrative',
        fontName=FONT_REGULAR,
        fontSize=11,
        textColor=PINMETO_NAVY,
        spaceBefore=10,
        spaceAfter=15,
        leading=16,
    ))

    # Insight bullet point
    styles.add(ParagraphStyle(
        name='PinMeToInsight',
        fontName=FONT_REGULAR,
        fontSize=9,
        textColor=PINMETO_MID_GREY,
        spaceBefore=3,
        spaceAfter=3,
        leading=12,
    ))

    # Appendix section header
    styles.add(ParagraphStyle(
        name='PinMeToAppendixH2',
        fontName=FONT_BOLD,
        fontSize=11,
        leading=14,        textColor=PINMETO_BLUE,
        spaceBefore=12,
        spaceAfter=6,
    ))

    # Appendix body text (smaller)
    styles.add(ParagraphStyle(
        name='PinMeToAppendixBody',
        fontName=FONT_REGULAR,
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
def get_data_table_style(text_columns=()):
    """Standard data table styling.

    Args:
        text_columns: indices of columns holding text rather than numbers. These
            align left in BOTH the header and the body; numeric columns align
            right in both. A header aligned opposite its own column reads as a
            layout bug.

    Chrome is recessive: a tinted header with ink text rather than a saturated
    blue block, hairline row rules instead of a full cell grid, and a barely-there
    zebra. A boxed grid puts a line around every number, which is a lot of ink
    that carries no information.
    """
    commands = [
        # Header row: tint + ink, with a single rule carrying the brand colour.
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), INK),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
        # (text_columns overrides are appended below)
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, CHART_BLUE),

        # Data rows. Header and body share alignment so columns read as columns.
        ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), INK),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_ZEBRA]),

        # Hairline rules only, one shade off the surface.
        ('LINEBELOW', (0, 1), (-1, -2), 0.4, HAIRLINE),
        ('LINEBELOW', (0, -1), (-1, -1), 0.8, HAIRLINE),
    ]
    for column in text_columns:
        commands.append(('ALIGN', (column, 0), (column, -1), 'LEFT'))
    return TableStyle(commands)


def change_column_styles(table_data, first_change_col=2):
    """Status colours for the change columns of a metrics table.

    Returns TableStyle commands so a reader sees direction in the table the same
    way they see it on the stat tiles, instead of the tables being the one place
    where +22% and -27% look identical.
    """
    commands = []
    for row_index, row in enumerate(table_data[1:], start=1):
        for col_index in range(first_change_col, len(row)):
            value = row[col_index]
            if change_direction(value) != 0:
                commands.append(
                    ('TEXTCOLOR', (col_index, row_index), (col_index, row_index),
                     status_color(value))
                )
    return commands


# =============================================================================
# Chart Creation
# =============================================================================
def create_category_bars(data: list[dict], width=495, palette=None,
                         show_share=True) -> Drawing:
    """Horizontal labelled bars for a part-to-whole breakdown.

    Replaces the pie this section used to draw. A pie is only legible for
    part-to-whole at a glance with clearly unequal segments; these breakdowns
    routinely have close values (52% vs 40%), where arc length stops being
    comparable and the reader is left matching legend swatches. Bars share a
    common baseline, so close values are directly comparable, and every value is
    labelled rather than encoded in colour.

    Args:
        palette: per-bar colours. Default is a single hue for every bar, which is
            correct for nominal categories: they have no order, so a value-ramp
            would double-encode length as darkness and burn the colour channel on
            information the bar already shows. Pass SENTIMENT_COLORS only where the
            colour genuinely means state (good / neutral / bad).
        show_share: append each value as a percentage of the total.
    """
    if not data or not isinstance(data, list):
        return Drawing(width, 10)

    rows = [d for d in data if isinstance(d, dict)]
    if not rows:
        return Drawing(width, 10)

    label_width = 96
    value_width = 44
    bar_height = 13
    row_gap = 9
    track_width = max(60, width - label_width - value_width - 16)

    total = sum(d.get('value', 0) or 0 for d in rows)
    largest = max((d.get('value', 0) or 0) for d in rows) or 1

    height = len(rows) * (bar_height + row_gap)
    drawing = Drawing(width, height)

    for i, item in enumerate(rows):
        value = item.get('value', 0) or 0
        # Bars are drawn top-down; ReportLab's origin is bottom-left.
        y = height - (i + 1) * (bar_height + row_gap) + row_gap

        drawing.add(String(0, y + 3, str(item.get('label', '')),
                           fontSize=9, fontName=FONT_REGULAR,
                           fillColor=INK, textAnchor='start'))

        # Recessive track shows the full scale, so a short bar still reads as a
        # share of something rather than floating in space.
        drawing.add(Rect(label_width, y, track_width, bar_height,
                         fillColor=colors.HexColor('#F0F3F7'), strokeColor=None))

        colour = palette[i % len(palette)] if palette else CHART_BLUE
        bar_length = track_width * (value / largest) if largest else 0
        if bar_length > 0:
            drawing.add(Rect(label_width, y, bar_length, bar_height,
                             fillColor=colour, strokeColor=None))

        if show_share and total > 0:
            text = f'{round(value / total * 100)}%'
        else:
            text = format_metric_value(value)
        drawing.add(String(width, y + 3, text,
                           fontSize=9, fontName=FONT_BOLD,
                           fillColor=INK, textAnchor='end'))

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
    # Bars are capped rather than filling the slot: the leftover band is air, and
    # the pair sits with a small gap so adjacent fills read as separate marks
    # without a stroke drawn around them.
    bar_width = 0.30 if has_prior else 0.42
    pair_gap = 0.02

    if has_prior:
        bars1 = ax.bar([i - bar_width / 2 - pair_gap for i in x], values, bar_width,
                       label=current_label or 'Current', color='#1F7AE0', zorder=3)
        bars2 = ax.bar([i + bar_width / 2 + pair_gap for i in x], prior_values, bar_width,
                       label=prior_label or 'Prior', color='#C9DCF3', zorder=3)
    else:
        bars1 = ax.bar(x, values, bar_width, label=current_label or 'Current',
                       color='#1F7AE0', zorder=3)
        bars2 = None

    # Label the current series only. A number above every bar is chaos and goes
    # unread; the prior series is context, and the y-axis plus the table carry it.
    for bar in bars1:
        height_val = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height_val,
                f'{int(height_val):,}', ha='center', va='bottom', fontsize=7,
                color='#000050', zorder=4)

    # Style the chart
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9, color='#000050')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.tick_params(axis='y', labelsize=8, colors='#5A6472', length=0)
    ax.tick_params(axis='x', length=0)

    # Recessive grid: solid hairlines one shade off the surface, behind the bars.
    # It carries the values that are no longer directly labelled.
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='#DCE3EC', linewidth=0.6, linestyle='-')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DCE3EC')
    ax.spines['bottom'].set_linewidth(0.8)

    # Add title showing what value is displayed
    if value_name:
        ax.set_title(value_name, fontsize=10, color='#000050', fontweight='bold', pad=10)

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


def _direction_triangle(drawing, x, y, direction, color, size=4.0):
    """Draw a small up/down triangle as the delta's non-colour channel.

    Colour alone must never carry direction (a protan reader sees green and red as
    the same hue), so every delta ships with this glyph. Drawn as a polygon rather
    than a text character because the base-14 PDF fonts have no triangle glyph.
    """
    if direction == 0:
        # Neutral: a short dash, so 'no change' does not imply a direction.
        drawing.add(Rect(x, y + size / 2, size * 1.6, 1.1,
                         fillColor=color, strokeColor=None))
        return

    half = size * 0.62
    if direction > 0:
        points = [x, y, x + half * 2, y, x + half, y + size]
    else:
        points = [x, y + size, x + half * 2, y + size, x + half, y]

    from reportlab.graphics.shapes import Polygon
    drawing.add(Polygon(points, fillColor=color, strokeColor=None))


def _star_points(cx, cy, outer_radius):
    """Vertices of a five-pointed star centred on (cx, cy), point upwards."""
    import math
    # 0.382 is the classic geometric star, but its points read as thin spikes at
    # 11pt. A larger inner radius gives a solider shape that survives small sizes
    # and print.
    inner_radius = outer_radius * 0.47
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer_radius if i % 2 == 0 else inner_radius
        points.extend([cx + radius * math.cos(angle), cy + radius * math.sin(angle)])
    return points


def draw_star_rating(drawing, x, y, value, max_value, size=11, gap=2.5,
                     fill_color=None, track_color=None):
    """Draw a star rating with an exact partial final star.

    The stars are filled to the true value rather than rounded to the nearest
    half: a mark must not overstate its number, and 4.3 rounded up to 4.5 stars
    would. The fractional star is clipped horizontally to the exact remainder.

    Returns the width consumed, so callers can lay out beside it.
    """
    from reportlab.graphics.shapes import Group, Polygon, definePath

    fill_color = fill_color or STAR_AMBER
    track_color = track_color or colors.HexColor('#DCE3EC')

    try:
        value = float(value)
        star_count = int(float(max_value))
    except (TypeError, ValueError):
        return 0

    if star_count <= 0:
        return 0

    radius = size / 2.0
    step = size + gap

    for index in range(star_count):
        cx = x + radius + index * step
        cy = y + radius
        points = _star_points(cx, cy, radius)

        # Track star underneath, so the remainder still reads as "out of five".
        drawing.add(Polygon(points, fillColor=track_color, strokeColor=None))

        remainder = value - index
        if remainder <= 0:
            continue

        if remainder >= 1:
            drawing.add(Polygon(points, fillColor=fill_color, strokeColor=None))
            continue

        # Partial star: clip the filled star to the exact fraction.
        left = cx - radius
        clip_width = size * remainder
        group = Group()
        group.add(definePath(
            [('moveTo', left, y),
             ('lineTo', left + clip_width, y),
             ('lineTo', left + clip_width, y + size),
             ('lineTo', left, y + size),
             ('closePath',)],
            isClipPath=1, fillColor=None, strokeColor=None))
        group.add(Polygon(points, fillColor=fill_color, strokeColor=None))
        drawing.add(group)

    return star_count * step - gap


def create_kpi_cards(kpis: list, width=500) -> Drawing:
    """Create a row of KPI stat tiles.

    Follows the stat-tile contract: label, value, delta, and an optional meter.

    - Label sits above the value; the value is the loudest thing in the tile.
    - The value wears ink, not the brand blue. Text never wears a data colour;
      identity comes from the accent rule beside it.
    - The delta carries a status colour AND a triangle, so direction survives
      colourblindness and greyscale printing.
    - A KPI carrying a 'max' renders a meter (e.g. a 4.3 rating out of 5), which
      gives an otherwise context-free number its scale.
    - Chrome is a fill plus one accent rule. No outline: a border around a tile is
      ink that is not data.
    """
    if not kpis:
        return Drawing(width, 10)

    tiles = kpis[:4]
    count = len(tiles)
    gap = 12
    tile_height = 76
    tile_width = (width - gap * (count - 1)) / count

    drawing = Drawing(width, tile_height)

    for i, kpi in enumerate(tiles):
        x = i * (tile_width + gap)
        y = 0

        # Tile surface, no stroke.
        drawing.add(Rect(x, y, tile_width, tile_height,
                         fillColor=TILE_SURFACE, strokeColor=None,
                         rx=3, ry=3))

        # Accent rule: the tile's only chrome, and where the brand colour lives.
        drawing.add(Rect(x, y, 3, tile_height,
                         fillColor=CHART_BLUE, strokeColor=None))

        pad_left = x + 12
        text_top = y + tile_height - 16

        # Label above the value.
        name = kpi.get('name', '')
        if name:
            drawing.add(String(pad_left, text_top, str(name),
                               fontSize=8, fontName=FONT_REGULAR,
                               fillColor=INK_MUTED, textAnchor='start'))

        # Value: the loudest element, in ink.
        value = kpi.get('value', 'N/A')
        max_value = kpi.get('max')
        value_size = 22 if len(str(value)) <= 7 else 18
        value_baseline = text_top - value_size - 4
        drawing.add(String(pad_left, value_baseline, str(value),
                           fontSize=value_size, fontName=FONT_BOLD,
                           fillColor=INK, textAnchor='start'))

        # Scale rides beside the value, not on the meter track, so the two never
        # collide however wide the tile is.
        if max_value:
            from reportlab.pdfbase.pdfmetrics import stringWidth
            offset = stringWidth(str(value), FONT_BOLD, value_size)
            drawing.add(String(pad_left + offset + 3, value_baseline,
                               f'/ {max_value}', fontSize=9,
                               fontName=FONT_REGULAR, fillColor=INK_MUTED,
                               textAnchor='start'))

        baseline = y + 12

        # A rating is read as stars, so draw stars. The final star is filled to the
        # exact remainder rather than rounded, so the mark never overstates the
        # number printed above it.
        if max_value:
            try:
                numeric_value = float(str(value).replace(',', ''))
            except (ValueError, TypeError):
                numeric_value = None
            if numeric_value is not None:
                draw_star_rating(drawing, pad_left, baseline - 1,
                                 numeric_value, max_value, size=11, gap=2.5)
                continue

        # Delta: triangle plus text, both in the status colour.
        change = kpi.get('change', '')
        if change:
            direction = change_direction(change)
            colour = status_color(change)
            _direction_triangle(drawing, pad_left, baseline, direction, colour)
            drawing.add(String(pad_left + 12, baseline, str(change),
                               fontSize=9, fontName=FONT_REGULAR,
                               fillColor=colour, textAnchor='start'))

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
DRAFT_WATERMARK_TEXT = "DRAFT - PENDING REVIEW"
DRAFT_WATERMARK_MAX_SIZE = 60
DRAFT_WATERMARK_MARGIN = 24


def draft_watermark_font_size(page_width, page_height, font_name,
                              text=DRAFT_WATERMARK_TEXT,
                              max_size=DRAFT_WATERMARK_MAX_SIZE,
                              margin=DRAFT_WATERMARK_MARGIN):
    """Largest size at which the 45-degree watermark still fits on the page.

    Derived from the page rather than hardcoded, because the string's width is a
    property of the font: at 60pt this text is 783pt wide in Helvetica but 845pt
    in Montserrat, and the wider one overran the left edge.

    A rotated text block is a rectangle, not a line: width w and line height h
    both project onto each axis, giving an axis-aligned span of (w + h)*cos(45).
    Ignoring h leaves the glyph ascenders and descenders hanging off the edge.
    The shorter page side is the binding constraint.
    """
    cos45 = math.cos(math.radians(45))
    allowed_span = min(page_width, page_height) - 2 * margin
    # Width and line height per point of font size, so size factors out.
    width_per_pt = pdfmetrics.stringWidth(text, font_name, 1.0)
    height_per_pt = 1.2  # conventional line height, covers ascender + descender
    span_per_pt = (width_per_pt + height_per_pt) * cos45
    return min(max_size, allowed_span / span_per_pt)


def draw_draft_watermark(canvas, doc):
    """Draw a diagonal 'DRAFT - PENDING REVIEW' watermark across the page."""
    canvas.saveState()

    page_width, page_height = doc.pagesize
    size = draft_watermark_font_size(page_width, page_height, FONT_BOLD)

    # Semi-transparent gray text
    canvas.setFillColor(colors.Color(0.7, 0.7, 0.7, alpha=0.4))
    canvas.setFont(FONT_BOLD, size)

    # Rotate about the page centre and draw the string centred on it
    canvas.translate(page_width / 2, page_height / 2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, DRAFT_WATERMARK_TEXT)

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
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(PINMETO_MID_GREY)
    canvas.drawString(50, doc.height + 70, header_text)

    # Logo (if available)
    if logo_path and os.path.exists(logo_path):
        canvas.drawImage(logo_path, doc.width - 50, doc.height + 65, width=80, height=25, preserveAspectRatio=True)

    # Footer
    canvas.setFont(FONT_REGULAR, 8)
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
        # Dynamic label based on report type
        period = data.get('period', '')
        report_type = detect_report_type(period, get_period_type(data))
        highlights_label = {
            'yearly': 'Year Highlights',
            'half-yearly': 'Half-Year Highlights',
            'quarterly': 'Quarter Highlights',
            'monthly': 'Month Highlights'
        }.get(report_type, 'Key Highlights')
        elements.append(Paragraph(highlights_label, styles['PinMeToH2']))
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
        elements.append(create_kpi_cards(kpis, width=495))

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
    report_type = detect_report_type(current_period, get_period_type(data))

    # For yearly reports, only show YoY comparison (no quarterly column)
    is_yearly = report_type == 'yearly'

    # Metrics table with actual period names
    metrics = platform_data.get('metrics', [])
    if metrics:
        if is_yearly:
            # Yearly: 3 columns - Metric | Value | YoY Change
            table_data = [['Metric', current_period, f'vs {prior_year_period}']]
            for metric in metrics:
                table_data.append([
                    metric.get('name', ''),
                    format_metric_value(metric.get('value', '')),
                    decorate_delta(metric.get('yearChange', '') or metric.get('periodChange', '') or metric.get('year_change', 'N/A'))
                ])
            table = Table(table_data, colWidths=[180, 120, 190])
        else:
            # Quarterly/Monthly: 4 columns
            previous_period = get_previous_period(current_period)
            if previous_period:
                table_data = [['Metric', current_period, f'vs {previous_period}', f'vs {prior_year_period}']]
            else:
                table_data = [['Metric', current_period, 'Period Change', 'Year Change']]

            for metric in metrics:
                table_data.append([
                    metric.get('name', ''),
                    format_metric_value(metric.get('value', '')),
                    decorate_delta(metric.get('periodChange', '') or metric.get('period_change', 'N/A')),
                    decorate_delta(metric.get('yearChange', '') or metric.get('year_change', 'N/A'))
                ])
            table = Table(table_data, colWidths=[160, 100, 115, 115])

        style = get_data_table_style()
        for command in change_column_styles(table_data, first_change_col=2):
            style.add(*command)
        table.setStyle(style)
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
            width=PLATFORM_CHART_WIDTH,
            height=PLATFORM_CHART_HEIGHT,
            current_label=current_period,
            prior_label=prior_year_period,
            value_name=chart_title
        )
        if chart_image:
            elements.append(Image(chart_image,
                                  width=PLATFORM_CHART_WIDTH,
                                  height=PLATFORM_CHART_HEIGHT))

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
            fontName=FONT_REGULAR,
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
        keywords_table.setStyle(get_data_table_style(text_columns=(1, 3)))
        elements.append(keywords_table)

    # Category distribution pie chart below the table
    if categories:
        elements.append(Spacer(1, 25))
        elements.append(Paragraph("Category Distribution", styles['PinMeToH2']))
        elements.append(Spacer(1, 10))
        # Nominal categories: one hue for every bar, identity from the labels.
        elements.append(create_category_bars(categories, width=495))

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
        # Sentiment is polarity, so here the colour genuinely means state.
        elements.append(create_category_bars(sentiment_data, width=495,
                                             palette=SENTIMENT_COLORS))

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
        # 'period' is the current key; 'quarter' is the legacy alias and is wrong
        # for monthly, half-yearly, and yearly reports.
        period_label = reporting_period.get('period', '') or reporting_period.get('quarter', '')
        date_range = reporting_period.get('dateRange', '')
        data_freshness = reporting_period.get('dataFreshness', '')
        lag_note = reporting_period.get('lagNote', '')

        if period_label:
            elements.append(Paragraph(f"<b>Period:</b> {period_label}", styles['PinMeToAppendixBody']))
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

    # Use find_logo_path for robust logo resolution across environments
    logo_path = find_logo_path(logo_path)
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

    # The explicit --period wins unless the data file already states one.
    data['periodType'] = get_period_type(data) or args.period

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
