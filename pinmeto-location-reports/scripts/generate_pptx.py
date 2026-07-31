#!/usr/bin/env python3
# © 2025 PinMeTo AB. All rights reserved.
# See LICENSE file for full terms.
"""
PinMeTo Location Analytics PowerPoint Generator

Generates professional PPTX presentations from PinMeTo analytics data.
Uses python-pptx for slide creation with PinMeTo brand styling.

Usage:
    python generate_pptx.py --data report_data.json --output report.pptx --period quarterly

Dependencies:
    pip install python-pptx pillow

Author: PinMeTo
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import io

# Try to import matplotlib for chart generation
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-GUI backend for server environments
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will be text-based.")

# Script and asset paths
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
DEFAULT_LOGO = ASSETS_DIR / "logos" / "PinMeTo_Logo_Landscape.jpg"
DEFAULT_LOGO_VERTICAL = ASSETS_DIR / "logos" / "Pinmeto_Logo_Vertical.jpg"
FONTS_DIR = ASSETS_DIR / "fonts"

# Point matplotlib at the bundled Montserrat TTFs so chart labels match the slide
# typography. matplotlib maintains its own font registry, so without this the
# charts render in DejaVu Sans next to Montserrat slide text.
if MATPLOTLIB_AVAILABLE:
    from matplotlib import font_manager

    _faces = [
        FONTS_DIR / "Montserrat-Regular.ttf",
        FONTS_DIR / "Montserrat-SemiBold.ttf",
        FONTS_DIR / "Montserrat-Bold.ttf",
    ]
    if all(face.exists() for face in _faces):
        for _face in _faces:
            font_manager.fontManager.addfont(str(_face))
        plt.rcParams["font.family"] = "Montserrat"
    else:
        print(f"Warning: brand fonts missing from {FONTS_DIR}; charts use the matplotlib default.")

# =============================================================================
# PinMeTo Brand Constants
# =============================================================================
class Brand:
    # Colors (RGB tuples)
    BLUE = RGBColor(0x33, 0x99, 0xFF)
    ORANGE = RGBColor(0xFF, 0x88, 0x54)
    NAVY = RGBColor(0x00, 0x00, 0x50)
    LIGHT_BLUE = RGBColor(0xBB, 0xD9, 0xFA)
    GREY = RGBColor(0xF2, 0xF3, 0xF4)
    MID_GREY = RGBColor(0x33, 0x33, 0x33)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    GREEN = RGBColor(0x27, 0xAE, 0x60)  # Deprecated: see STATUS_GOOD

    # Chart & status tokens, validated with the dataviz skill's
    # validate_palette.js. The categorical trio passes all six checks; the
    # brand's own blue/orange/light-blue trio failed (light blue reads gray and
    # both brand hues fall under 3:1 against the surface). These are deepened
    # steps of the brand hues, reserved for data marks; BLUE stays the brand
    # accent for headings and rules.
    CHART_BLUE = RGBColor(0x1F, 0x7A, 0xE0)
    CHART_ORANGE = RGBColor(0xE8, 0x69, 0x0B)
    CHART_VIOLET = RGBColor(0x5B, 0x4B, 0x8A)
    CHART_PRIOR = RGBColor(0xC9, 0xDC, 0xF3)

    # Status pair. The previous green/orange measured dE 1.8 under protanopia,
    # i.e. identical to a red-green colourblind reader. This pair measures 9.6
    # and direction is also carried by a triangle glyph.
    STATUS_GOOD = RGBColor(0x0E, 0x7C, 0x4A)
    STATUS_BAD = RGBColor(0xCC, 0x33, 0x11)

    INK = RGBColor(0x00, 0x00, 0x50)
    INK_MUTED = RGBColor(0x5A, 0x64, 0x72)
    HAIRLINE = RGBColor(0xDC, 0xE3, 0xEC)
    TILE_SURFACE = RGBColor(0xF5, 0xF8, 0xFC)
    TABLE_HEADER_BG = RGBColor(0xEA, 0xF2, 0xFD)
    TABLE_ZEBRA = RGBColor(0xFA, 0xFB, 0xFD)

    # Font names. Montserrat is the only PinMeTo brand typeface (Graphic Manual,
    # May 2026), and it is what the official PinMeTo decks use in every text run.
    #
    # Caveat: a .pptx references fonts by name, so slide text renders in
    # Montserrat only on a machine that has it installed. python-pptx cannot
    # embed a typeface, and PowerPoint substitutes its own default otherwise.
    # Charts are unaffected: they are rasterised here with the bundled TTFs, so
    # chart labels are always Montserrat regardless of the viewer's fonts. Deliver
    # the PDF when typography has to be guaranteed.
    HEADING_FONT = "Montserrat"
    BODY_FONT = "Montserrat"

# Slide dimensions (16:9) - python-pptx default
SLIDE_WIDTH = Inches(10)
SLIDE_HEIGHT = Inches(5.625)

# Hex color strings for matplotlib (matching Brand colors)
CHART_COLORS = {
    'blue': '#1F7AE0',        # categorical slot 1 / data marks
    'orange': '#E8690B',      # categorical slot 2
    'violet': '#5B4B8A',      # categorical slot 3
    'prior': '#C9DCF3',       # prior-period wash (de-emphasis, not a slot)
    'light_blue': '#C9DCF3',  # retained alias
    'mid_grey': '#333333',
    'ink': '#000050',
    'ink_muted': '#5A6472',
    'hairline': '#DCE3EC',
    'track': '#F0F3F7',
    'good': '#0E7C4A',
    'neutral': '#9AA4B2',
    'bad': '#CC3311',
    # Star fill. Conventionally gold, but it must clear 3:1 on the tile surface:
    # brand orange measures 2.3:1 and a lighter gold is worse.
    'star': '#C77700',
    'green': '#0E7C4A',       # retained alias
}


# Direction glyphs for table cells, matching the drawn triangles on the stat
# tiles so both carry a non-colour channel.
DELTA_GLYPHS = {1: '▲', -1: '▼', 0: '–'}  # ▲ ▼ –
_GLYPH_PREFIX_CHARS = ''.join(DELTA_GLYPHS.values()) + ' \t'


def change_direction(change):
    """Classify a change string as positive (1), negative (-1) or neutral (0).

    Tolerates an already-applied direction glyph so a decorated cell can still
    be classified for its colour.
    """
    if not change:
        return 0
    text = str(change).strip().lstrip(_GLYPH_PREFIX_CHARS).strip()
    if not text or text.upper() in {'N/A', 'NA', '-', '--'}:
        return 0
    if 'no change' in text.lower():
        return 0
    if text.startswith('-'):
        return -1
    if text.startswith('+'):
        return 1
    return 0


def decorate_delta(value):
    """Prefix a change string with its direction glyph.

    Slide text references Montserrat by name rather than embedding it, so the
    glyph resolves through the viewer's font stack. ▲/▼ are near-universal, and
    a per-glyph substitution still reads as a triangle, so the non-colour
    channel survives even where Montserrat itself does not.
    """
    if value is None:
        return value
    text = str(value)
    if not text.strip():
        return text
    if text.strip().upper() in {'N/A', 'NA', '-', '--'}:
        return text
    if text.strip()[0] in DELTA_GLYPHS.values():
        return text  # already decorated
    return f"{DELTA_GLYPHS[change_direction(text)]} {text}"


def status_rgb(change):
    """Status colour for a change string, muted when there is no direction."""
    direction = change_direction(change)
    if direction > 0:
        return Brand.STATUS_GOOD
    if direction < 0:
        return Brand.STATUS_BAD
    return Brand.INK_MUTED


def direction_glyph(change):
    """Triangle prefix so direction never depends on colour alone."""
    direction = change_direction(change)
    return '\u25b2 ' if direction > 0 else ('\u25bc ' if direction < 0 else '\u2013 ')

# =============================================================================
# Text Layout Constants (prevents text overlap)
# =============================================================================
INSIGHT_BOX_HEIGHT = 0.45   # Height for each insight box in inches (fits 3 lines)
INSIGHT_SPACING = 0.50      # Vertical spacing between insights in inches
LINE_HEIGHT_8PT = 0.15      # Approximate line height at 8pt font
LINE_HEIGHT_10PT = 0.14     # Approximate line height at 10pt font

# =============================================================================
# Chart Generation Functions (matplotlib)
# =============================================================================
def generate_bar_chart_image(chart_data, title, has_prior_data=False, current_label=None, prior_label=None):
    """Generate a bar chart as PNG bytes using matplotlib."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    if not chart_data or len(chart_data) == 0:
        return None

    # Use actual period names if provided, otherwise fall back to generic labels
    current_legend = current_label or 'Current Period'
    prior_legend = prior_label or 'Prior Period'

    # Smaller figure size to fit better on slides
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='white')

    labels = [d.get('label', '') for d in chart_data]
    current_values = [d.get('value', 0) for d in chart_data]

    x = range(len(labels))
    # Bars are capped rather than filling the slot, and the pair carries a small
    # gap so touching fills read as separate marks without a stroke around them.
    width = 0.30 if has_prior_data else 0.42
    pair_gap = 0.02

    bars1 = ax.bar([i - width/2 - pair_gap if has_prior_data else i for i in x],
                   current_values, width, label=current_legend,
                   color=CHART_COLORS['blue'], zorder=3)

    if has_prior_data:
        prior_values = [d.get('priorValue', 0) for d in chart_data]
        bars2 = ax.bar([i + width/2 + pair_gap for i in x], prior_values, width,
                       label=prior_legend, color=CHART_COLORS['prior'], zorder=3)

    # Label the current series only. A number above every bar goes unread; the
    # prior series is context, carried by the grid and the table.
    for bar in bars1:
        height_val = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height_val,
                f'{int(height_val):,}', ha='center', va='bottom', fontsize=7,
                color=CHART_COLORS['ink'], zorder=4)

    ax.set_title(title, fontsize=11, fontweight='bold', color=CHART_COLORS['ink'])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, rotation=30, ha='right',
                       color=CHART_COLORS['ink'])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: format(int(v), ',')))
    ax.tick_params(axis='y', labelsize=8, colors=CHART_COLORS['ink_muted'], length=0)
    ax.tick_params(axis='x', length=0)

    if has_prior_data:
        ax.legend(loc='upper right', fontsize=8, frameon=False)

    # Recessive grid: solid hairlines one shade off the surface, behind the bars.
    ax.set_axisbelow(True)
    ax.grid(axis='y', color=CHART_COLORS['hairline'], linewidth=0.6, linestyle='-')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(CHART_COLORS['hairline'])
    ax.spines['bottom'].set_linewidth(0.8)

    # Adjust layout to fit everything within figure bounds
    plt.tight_layout()

    # Save to bytes - use fixed figure size, not bbox_inches='tight'
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor='white', pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_star_rating_image(value, max_value=5, star_size=64):
    """Render a star rating as a transparent PNG.

    Drawn as an image rather than as DrawingML star shapes so it matches the PDF
    exactly and avoids per-renderer gradient quirks in PowerPoint and Keynote.
    This is the same approach the charts already use for Keynote compatibility.

    The final star is clipped to the exact remainder rather than rounded to a half
    star, so the mark never overstates the number printed above it.
    """
    if not MATPLOTLIB_AVAILABLE:
        return None

    try:
        value = float(value)
        star_count = int(float(max_value))
    except (TypeError, ValueError):
        return None
    if star_count <= 0:
        return None

    import math
    from matplotlib.patches import Polygon, Rectangle

    def star_vertices(cx, cy, outer=1.0):
        # A larger inner radius than the classic 0.382 keeps the points from
        # reading as thin spikes at small sizes.
        inner = outer * 0.47
        pts = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            r = outer if i % 2 == 0 else inner
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        return pts

    step = 2.4  # centre-to-centre spacing in star radii
    fig_w = star_count * step
    fig, ax = plt.subplots(figsize=(fig_w * 0.16, 0.34), dpi=300)
    fig.patch.set_alpha(0)
    ax.set_axis_off()
    ax.set_xlim(-1.2, (star_count - 1) * step + 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')

    for index in range(star_count):
        cx = index * step
        # Track star, so the remainder still reads as "out of five".
        ax.add_patch(Polygon(star_vertices(cx, 0), closed=True,
                             facecolor=CHART_COLORS['hairline'], edgecolor='none'))
        remainder = value - index
        if remainder <= 0:
            continue
        filled = Polygon(star_vertices(cx, 0), closed=True,
                         facecolor=CHART_COLORS['star'], edgecolor='none')
        ax.add_patch(filled)
        if remainder < 1:
            clip = Rectangle((cx - 1.0, -1.2), 2.0 * remainder, 2.4,
                             transform=ax.transData)
            filled.set_clip_path(clip)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, transparent=True,
                bbox_inches='tight', pad_inches=0.01)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_breakdown_chart_image(data, title, palette=None):
    """Horizontal labelled bars for a part-to-whole breakdown, as PNG bytes.

    Replaces the pie these sections used to draw. A pie only works for
    part-to-whole at a glance with clearly unequal segments; these breakdowns
    routinely have close values (52% vs 38%), where arc length stops being
    comparable and the reader ends up matching legend swatches. Bars share a
    baseline, so close values compare directly, and each value is labelled.

    Args:
        palette: per-bar colours. Default is a single hue for every bar, correct
            for nominal categories: they have no order, so a value-ramp would
            double-encode length as darkness. Pass a status list only where the
            colour genuinely means state.
    """
    if not MATPLOTLIB_AVAILABLE:
        return None
    if not data or len(data) == 0:
        return None

    rows = [d for d in data if isinstance(d, dict)]
    if not rows:
        return None

    labels = [d.get('label') or d.get('name', '') for d in rows]
    values = [d.get('value', 0) or 0 for d in rows]
    total = sum(values)
    largest = max(values) if values else 0

    fig, ax = plt.subplots(figsize=(6, max(1.4, 0.52 * len(rows) + 0.9)),
                           facecolor='white')

    positions = list(range(len(rows)))[::-1]  # first row at the top
    colours = palette or [CHART_COLORS['blue']] * len(rows)

    # Recessive full-scale track, so a short bar still reads as a share.
    ax.barh(positions, [largest] * len(rows), height=0.5,
            color=CHART_COLORS['track'], zorder=2)
    ax.barh(positions, values, height=0.5,
            color=[colours[i % len(colours)] for i in range(len(rows))], zorder=3)

    for pos, value in zip(positions, values):
        share = f'{round(value / total * 100)}%' if total else f'{value:,}'
        ax.text(largest * 1.02, pos, share, va='center', ha='left',
                fontsize=9, fontweight='bold', color=CHART_COLORS['ink'], zorder=4)

    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=9, color=CHART_COLORS['ink'])
    ax.set_xticks([])
    ax.set_xlim(0, largest * 1.16 if largest else 1)
    ax.tick_params(axis='y', length=0)
    for side in ('top', 'right', 'bottom', 'left'):
        ax.spines[side].set_visible(False)
    ax.set_title(title, fontsize=11, fontweight='bold', color=CHART_COLORS['ink'],
                 loc='left')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_sentiment_breakdown_chart(sentiment_data):
    """Sentiment breakdown bars.

    Sentiment is polarity, not identity, so this is the one breakdown where the
    colour genuinely means state: good, neutral midpoint, bad. The labels are
    always present, so colour is never the only channel.
    """
    if not MATPLOTLIB_AVAILABLE:
        return None

    data = [
        {'label': 'Positive', 'value': sentiment_data.get('positive', 0)},
        {'label': 'Neutral', 'value': sentiment_data.get('neutral', 0)},
        {'label': 'Negative', 'value': sentiment_data.get('negative', 0)},
    ]
    palette = [CHART_COLORS['good'], CHART_COLORS['neutral'], CHART_COLORS['bad']]

    keep = [(d, c) for d, c in zip(data, palette) if d['value'] > 0]
    if not keep:
        return None

    return generate_breakdown_chart_image(
        [d for d, _ in keep], 'Sentiment Distribution',
        palette=[c for _, c in keep]
    )


# =============================================================================
# Draft Watermark
# =============================================================================
def add_draft_watermark(slide):
    """Add a diagonal 'DRAFT - PENDING REVIEW' watermark to a slide."""
    from pptx.oxml.ns import qn

    # Add a text box for the watermark (centered on slide)
    watermark = slide.shapes.add_textbox(
        Inches(0.5), Inches(2),
        Inches(9), Inches(1.5)
    )
    tf = watermark.text_frame
    # A watermark must stay on one line. At 48pt bold this string is slightly
    # wider than the 9in box, so leaving wrap enabled risks PowerPoint breaking
    # it across two lines; overflowing the box is the harmless outcome here.
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.text = "DRAFT - PENDING REVIEW"
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x99, 0x99, 0x99)  # Gray color
    p.alignment = PP_ALIGN.CENTER

    # Rotate the shape 45 degrees using OOXML
    # Access the shape's spPr element to add rotation
    sp = watermark._element
    xfrm = sp.find('.//' + qn('a:xfrm'))
    if xfrm is not None:
        xfrm.set('rot', str(int(-45 * 60000)))  # Rotation in EMUs (60000 per degree)

    # Move the watermark to the back
    # Lower z-order by moving shape to beginning of shape tree
    spTree = slide.shapes._spTree
    sp_idx = list(spTree).index(sp)
    if sp_idx > 2:  # Keep it behind content but above background
        spTree.remove(sp)
        spTree.insert(2, sp)


# =============================================================================
# Helper Functions
# =============================================================================
def add_text_box(slide, text, left, top, width, height, font_size=12,
                 font_name=Brand.BODY_FONT, color=Brand.MID_GREY, bold=False,
                 align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    """Add a text box with specified formatting."""
    textbox = slide.shapes.add_textbox(left, top, width, height)
    tf = textbox.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = str(text)
    p.font.size = Pt(font_size)
    p.font.name = font_name
    p.font.color.rgb = color
    p.font.bold = bold
    p.alignment = align

    tf.vertical_anchor = valign

    return textbox

def format_number(value):
    """Format large numbers with K/M suffixes."""
    if isinstance(value, str):
        return value
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return str(value)


def format_metric_value(value):
    """Format a metric value for display in a table.

    Applies thousands separators so metric tables match the keyword table, the
    chart value labels, and the KPI cards. Without this, a table reads
    '2400000' on the same slide as a chart labelled '780,000'.

    Strings pass through untouched: they are already formatted upstream (for
    example the '2.4M' style from format_number, or 'N/A').
    """
    if isinstance(value, bool) or value is None:
        return str(value) if value is not None else ""
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        # Keep a decimal only when it carries information, so ratings stay 4.3
        # while whole counts do not gain a spurious '.0'.
        if value.is_integer():
            return f"{int(value):,}"
        return f"{value:,.1f}"
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
    if re.match(r'^\d{4}$', period.strip()):
        year = int(period.strip())
        return str(year - 1)

    # Try quarterly format ('Q4 2025')
    match = re.match(r'Q(\d)\s+(\d{4})', period)
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
        match = re.match(rf'({month_full}|{month_short})\s+(\d{{4}})', period, re.IGNORECASE)
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


def get_period_type(data):
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
    if re.match(r'^\d{4}$', period.strip()):
        return 'yearly'

    # Quarterly: Q1-Q4 YYYY
    if re.match(r'Q\d\s+\d{4}', period):
        return 'quarterly'

    # Half-yearly: H1/H2 YYYY
    if re.match(r'^H[12]\s+\d{4}', period.strip(), re.IGNORECASE):
        return 'half-yearly'

    # Monthly: Month name + year
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    for month in months:
        if period.lower().startswith(month.lower()[:3]):
            return 'monthly'

    return None


def find_logo_path(data):
    """Find logo path with fallback for different environments (e.g., Claude Desktop)."""
    candidates = [
        data.get("logoPath"),  # User-provided path
        str(DEFAULT_LOGO),     # Default relative to script
        "assets/logos/PinMeTo_Logo_Landscape.jpg",  # CWD relative
        "pinmeto-location-reports/assets/logos/PinMeTo_Logo_Landscape.jpg",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    print(f"Warning: Logo not found. Tried: {[c for c in candidates if c]}")
    return None

def estimate_text_height(text, chars_per_line=90, line_height=0.14, min_height=0.3):
    """Estimate text box height based on content length.

    Args:
        text: The text content
        chars_per_line: Approximate characters per line (depends on font size and box width)
        line_height: Height per line in inches
        min_height: Minimum box height in inches

    Returns:
        Estimated height in inches
    """
    if not text:
        return min_height
    lines = max(1, (len(text) // chars_per_line) + 1)
    return max(min_height, lines * line_height)

# =============================================================================
# Slide Creation Functions
# =============================================================================
def create_title_slide(prs, data):
    """Create the title slide with logo and report info."""
    slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(slide_layout)

    # Logo - use landscape version with fallback path resolution
    logo_path = find_logo_path(data)
    if logo_path:
        slide.shapes.add_picture(logo_path, Inches(0.5), Inches(0.3), width=Inches(1.8))

    # Company name - tighter spacing below logo
    company_name = data.get("companyName") or data.get("company_name", "")
    if company_name:
        add_text_box(slide, company_name, Inches(0.5), Inches(1.3), Inches(9), Inches(0.4),
                     font_size=16, color=Brand.MID_GREY)

    # Main title
    title = data.get("title", "Location Analytics Report")
    add_text_box(slide, title, Inches(0.5), Inches(1.8), Inches(9), Inches(0.9),
                 font_size=32, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)

    # Period subtitle - tighter spacing
    period = data.get("period", "")
    add_text_box(slide, period, Inches(0.5), Inches(2.8), Inches(9), Inches(0.5),
                 font_size=20, font_name=Brand.HEADING_FONT, color=Brand.BLUE)

    # Current period date range
    date_range = data.get("dateRange", "")
    if date_range:
        add_text_box(slide, f"Current Period: {date_range}", Inches(0.5), Inches(3.5),
                     Inches(9), Inches(0.3), font_size=12, color=Brand.MID_GREY)

    # Prior period date range
    prior_period = data.get("priorPeriod", "")
    prior_date_range = data.get("priorDateRange", "")
    if prior_period and prior_date_range:
        add_text_box(slide, f"Prior Period ({prior_period}): {prior_date_range}",
                     Inches(0.5), Inches(3.85), Inches(9), Inches(0.3),
                     font_size=12, color=Brand.MID_GREY)

    # Generation date - positioned at bottom
    today = date.today().isoformat()
    add_text_box(slide, f"Generated: {today}", Inches(0.5), Inches(5.15),
                 Inches(4), Inches(0.3), font_size=10, color=Brand.MID_GREY)

    return slide

def add_header_line(slide):
    """Add the blue header line to a slide."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, Inches(0.05))
    shape.fill.solid()
    shape.fill.fore_color.rgb = Brand.BLUE
    shape.line.fill.background()

def add_footer(slide, page_num=None):
    """Add footer text to a slide."""
    add_text_box(slide, "PinMeTo Location Analytics", Inches(0.5), Inches(5.3),
                 Inches(3), Inches(0.25), font_size=8, color=Brand.MID_GREY)
    if page_num:
        add_text_box(slide, str(page_num), Inches(9.2), Inches(5.3),
                     Inches(0.5), Inches(0.25), font_size=8, color=Brand.MID_GREY)

def create_executive_summary(prs, data):
    """Create the executive summary slide."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    add_header_line(slide)
    add_footer(slide)

    # Title
    add_text_box(slide, "Executive Summary", Inches(0.5), Inches(0.2), Inches(9), Inches(0.4),
                 font_size=24, font_name=Brand.HEADING_FONT, color=Brand.BLUE, bold=True)

    # Narrative - with dynamic height based on content length
    exec_summary = data.get("executiveSummary", {})
    narrative = exec_summary.get("narrative", "")
    start_y = 0.65
    if narrative:
        # Calculate narrative height dynamically (90 chars/line at 10pt in 9" width)
        narrative_height = estimate_text_height(narrative, chars_per_line=90, line_height=LINE_HEIGHT_10PT, min_height=0.3)
        add_text_box(slide, narrative, Inches(0.5), Inches(start_y), Inches(9), Inches(narrative_height),
                     font_size=10, color=Brand.NAVY)
        start_y = start_y + narrative_height + 0.15  # Dynamic positioning below narrative

    # Highlights - with increased spacing to allow text wrapping
    highlights = exec_summary.get("highlights", []) or data.get("highlights", [])
    if highlights:
        # Dynamic label based on report type
        period = data.get("period", "")
        report_type = detect_report_type(period, get_period_type(data))
        highlights_label = {
            'yearly': 'Year Highlights',
            'half-yearly': 'Half-Year Highlights',
            'quarterly': 'Quarter Highlights',
            'monthly': 'Month Highlights'
        }.get(report_type, 'Key Highlights')

        add_text_box(slide, highlights_label, Inches(0.5), Inches(start_y),
                     Inches(4.5), Inches(0.25), font_size=12, font_name=Brand.HEADING_FONT,
                     color=Brand.NAVY, bold=True)

        for i, highlight in enumerate(highlights[:4]):
            y = start_y + 0.35 + i * INSIGHT_SPACING  # Use constant for consistent spacing
            if isinstance(highlight, dict):
                title = highlight.get("title", "")
                desc = highlight.get("description", "")
                text = f"• {title}: {desc}" if title and desc else f"• {title or desc}"
            else:
                text = f"• {highlight}"
            add_text_box(slide, text, Inches(0.5), Inches(y), Inches(4.5), Inches(INSIGHT_BOX_HEIGHT),
                         font_size=9, color=Brand.MID_GREY)

    # KPI boxes
    kpis = data.get("kpis", [])
    if kpis:
        add_text_box(slide, "Performance Metrics", Inches(5.5), Inches(start_y),
                     Inches(4), Inches(0.25), font_size=12, font_name=Brand.HEADING_FONT,
                     color=Brand.NAVY, bold=True)

        # Stat tiles: label above value, value in ink (text never wears a data
        # colour), delta carrying both a status colour and a triangle so direction
        # survives colourblindness. Chrome is a fill plus one accent rule; an
        # outline around a tile is ink that is not data.
        for i, kpi in enumerate(kpis[:4]):
            col = i % 2
            row = i // 2
            x = 5.5 + col * 2.2
            y = start_y + 0.35 + row * 1.4
            tile_w, tile_h = 2.0, 1.2

            box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                         Inches(x), Inches(y), Inches(tile_w), Inches(tile_h))
            box.fill.solid()
            box.fill.fore_color.rgb = Brand.TILE_SURFACE
            box.line.fill.background()
            box.shadow.inherit = False

            accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                            Inches(x), Inches(y), Inches(0.04), Inches(tile_h))
            accent.fill.solid()
            accent.fill.fore_color.rgb = Brand.CHART_BLUE
            accent.line.fill.background()
            accent.shadow.inherit = False

            text_x = Inches(x + 0.14)
            text_w = Inches(tile_w - 0.24)

            name = kpi.get("name", "")
            add_text_box(slide, name, text_x, Inches(y + 0.10), text_w, Inches(0.20),
                         font_size=8, color=Brand.INK_MUTED)

            value = kpi.get("value", "N/A")
            max_value = kpi.get("max")
            value_text = f"{value}  / {max_value}" if max_value else str(value)
            add_text_box(slide, value_text, text_x, Inches(y + 0.32), text_w, Inches(0.45),
                         font_size=20, font_name=Brand.HEADING_FONT, color=Brand.INK,
                         bold=True)

            if max_value:
                # A rating is read as stars, so draw stars.
                star_image = generate_star_rating_image(
                    str(value).replace(",", ""), max_value)
                if star_image:
                    slide.shapes.add_picture(star_image, text_x, Inches(y + 0.84),
                                             height=Inches(0.20))
                    continue

            change = kpi.get("change", "")
            if change:
                add_text_box(slide, f"{direction_glyph(change)}{change}",
                             text_x, Inches(y + 0.86), text_w, Inches(0.22),
                             font_size=9, color=status_rgb(change))

    return slide

def create_metrics_slide(prs, title, metrics_data, period_info):
    """Create a metrics slide with table and optional chart."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    add_header_line(slide)
    add_footer(slide)

    # Title
    add_text_box(slide, title, Inches(0.5), Inches(0.2), Inches(9), Inches(0.4),
                 font_size=24, font_name=Brand.HEADING_FONT, color=Brand.BLUE, bold=True)

    # Key Insights - with increased spacing to allow text wrapping
    insights = metrics_data.get("insights", [])
    table_start_y = 0.7
    if insights:
        add_text_box(slide, "Key Insights", Inches(0.5), Inches(0.65), Inches(4), Inches(0.25),
                     font_size=10, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)
        for i, insight in enumerate(insights[:3]):
            add_text_box(slide, f"• {insight}", Inches(0.5), Inches(0.93 + i * INSIGHT_SPACING),
                         Inches(4.3), Inches(INSIGHT_BOX_HEIGHT), font_size=8, color=Brand.MID_GREY)
        table_start_y = 0.93 + len(insights[:3]) * INSIGHT_SPACING + 0.15

    # Period footer
    if period_info.get("period"):
        period_text = period_info["period"]
        if period_info.get("priorPeriod"):
            period_text += f" vs {period_info['priorPeriod']}"
        add_text_box(slide, period_text, Inches(4), Inches(5.3), Inches(2), Inches(0.25),
                     font_size=8, color=Brand.MID_GREY, align=PP_ALIGN.CENTER)

    # Metrics table
    metrics = metrics_data.get("metrics", [])
    current_period = period_info.get("period", "Current")
    prior_year_period = period_info.get("priorPeriod", "Prior Year")  # e.g., 2024 or Q4 2024
    report_type = detect_report_type(current_period, period_info.get("periodType"))

    # For yearly reports, only show YoY comparison (no quarterly column)
    # For quarterly/monthly, show both period-over-period and year-over-year
    is_yearly = report_type == 'yearly'

    if metrics:
        rows = len(metrics) + 1  # +1 for header
        cols = 3 if is_yearly else 4
        table = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(table_start_y),
                                        Inches(4.3), Inches(0.3 * rows)).table

        # Build headers based on report type
        if is_yearly:
            # Yearly: Metric | Value | YoY Change
            headers = ["Metric", current_period, f"vs {prior_year_period}"]
        else:
            # Quarterly/Monthly: Metric | Value | vs Prior Period | vs Prior Year
            previous_period = get_previous_period(current_period)
            if previous_period:
                headers = ["Metric", current_period, f"vs {previous_period}", f"vs {prior_year_period}"]
            else:
                # Fallback if period detection failed
                headers = ["Metric", current_period, "Period Change", "Year Change"]

        for j, header in enumerate(headers):
            cell = table.cell(0, j)
            cell.text = header
            cell.fill.solid()
            cell.fill.fore_color.rgb = Brand.TABLE_HEADER_BG
            p = cell.text_frame.paragraphs[0]
            p.font.bold = True
            p.font.size = Pt(9)
            p.font.color.rgb = Brand.INK

        # Data rows
        for i, metric in enumerate(metrics):
            row_fill = Brand.WHITE if i % 2 == 0 else Brand.TABLE_ZEBRA

            if is_yearly:
                # Yearly: 3 columns - for yearly, periodChange IS the YoY change
                row_data = [
                    metric.get("name", ""),
                    format_metric_value(metric.get("value", "")),
                    decorate_delta(metric.get("yearChange") or metric.get("periodChange", "N/A"))
                ]
            else:
                # Quarterly/Monthly: 4 columns
                row_data = [
                    metric.get("name", ""),
                    format_metric_value(metric.get("value", "")),
                    decorate_delta(metric.get("periodChange", "N/A")),
                    decorate_delta(metric.get("yearChange", "N/A"))
                ]

            for j, value in enumerate(row_data):
                cell = table.cell(i + 1, j)
                cell.text = value
                cell.fill.solid()
                cell.fill.fore_color.rgb = row_fill
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(9)
                # Change columns carry direction, matching the stat tiles rather
                # than being the one place where +22% and -27% look identical.
                if j >= 2 and change_direction(value) != 0:
                    p.font.color.rgb = status_rgb(value)
                else:
                    p.font.color.rgb = Brand.INK

    # Chart - bar chart image or text fallback (compares to prior year same period)
    chart_data = metrics_data.get("chartData", [])
    if chart_data:
        has_prior = any(d.get('priorValue') is not None for d in chart_data)
        # Determine chart title based on platform's primary metric
        metric_titles = {
            "Google Business Profile": "Profile Views",
            "Facebook Performance": "Page Engagement",
            "Apple Maps Performance": "Discovery Views"
        }
        metric_name = metric_titles.get(title, "Monthly Activity")
        chart_title = f"{metric_name} - {current_period} vs {prior_year_period}" if has_prior else f"{metric_name} - Monthly Trend"
        chart_image = generate_bar_chart_image(chart_data, chart_title, has_prior,
                                                current_label=current_period,
                                                prior_label=prior_year_period)

        if chart_image:
            # Add chart image - constrain to fit within slide (max bottom at 5.1")
            chart_top = table_start_y
            chart_height = min(3.0, 5.1 - chart_top)  # Ensure chart doesn't exceed slide
            slide.shapes.add_picture(chart_image, Inches(5.2), Inches(chart_top),
                                     width=Inches(4.3), height=Inches(chart_height))
        else:
            # Text fallback if matplotlib unavailable
            add_text_box(slide, "Period Comparison", Inches(5), Inches(table_start_y),
                         Inches(4.5), Inches(0.3), font_size=12, font_name=Brand.HEADING_FONT,
                         color=Brand.NAVY, bold=True)

            for i, item in enumerate(chart_data[:6]):
                y = table_start_y + 0.4 + i * 0.4
                label = item.get("label", "")
                value = format_number(item.get("value", 0))
                prior = item.get("priorValue")

                if prior is not None:
                    prior_fmt = format_number(prior)
                    text = f"{label}: {value} (prior: {prior_fmt})"
                else:
                    text = f"{label}: {value}"

                add_text_box(slide, text, Inches(5), Inches(y), Inches(4.5), Inches(0.35),
                             font_size=10, color=Brand.MID_GREY)

    return slide

def create_keywords_slide(prs, keywords_data, period_info):
    """Create the keywords analysis slide."""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    add_header_line(slide)
    add_footer(slide)

    # Title
    add_text_box(slide, "Search Keywords Analysis", Inches(0.5), Inches(0.2), Inches(9), Inches(0.4),
                 font_size=24, font_name=Brand.HEADING_FONT, color=Brand.BLUE, bold=True)

    # Key Insights - with increased spacing to allow text wrapping
    insights = keywords_data.get("insights", [])
    table_start_y = 0.7
    if insights:
        add_text_box(slide, "Key Insights", Inches(0.5), Inches(0.65), Inches(4), Inches(0.25),
                     font_size=10, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)
        for i, insight in enumerate(insights[:3]):
            add_text_box(slide, f"• {insight}", Inches(0.5), Inches(0.93 + i * INSIGHT_SPACING),
                         Inches(4.3), Inches(INSIGHT_BOX_HEIGHT), font_size=8, color=Brand.MID_GREY)
        table_start_y = 0.93 + len(insights[:3]) * INSIGHT_SPACING + 0.15

    # Period footer
    if period_info.get("period"):
        period_text = period_info["period"]
        if period_info.get("priorPeriod"):
            period_text += f" vs {period_info['priorPeriod']}"
        add_text_box(slide, period_text, Inches(4), Inches(5.3), Inches(2), Inches(0.25),
                     font_size=8, color=Brand.MID_GREY, align=PP_ALIGN.CENTER)

    # Keywords table - calculate max rows that fit on slide
    keywords = keywords_data.get("topKeywords", [])
    if keywords:
        row_height = 0.26  # Height per row in inches
        max_table_bottom = 5.1  # Maximum Y position for table bottom
        available_height = max_table_bottom - table_start_y
        max_rows = int(available_height / row_height) - 1  # -1 for header
        max_keywords = min(len(keywords), max_rows, 8)  # Cap at 8 keywords max

        rows = max_keywords + 1  # +1 for header
        cols = 4
        table = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(table_start_y),
                                        Inches(5.5), Inches(row_height * rows)).table

        # Header
        headers = ["#", "Keyword", "Impressions", "Category"]
        for j, header in enumerate(headers):
            cell = table.cell(0, j)
            cell.text = header
            cell.fill.solid()
            cell.fill.fore_color.rgb = Brand.TABLE_HEADER_BG
            p = cell.text_frame.paragraphs[0]
            p.font.bold = True
            p.font.size = Pt(9)
            p.font.color.rgb = Brand.INK

        # Data rows
        for i, kw in enumerate(keywords[:max_keywords]):
            row_fill = Brand.WHITE if i % 2 == 0 else Brand.TABLE_ZEBRA
            row_data = [
                str(i + 1),
                kw.get("keyword", ""),
                str(kw.get("impressions", "")),
                kw.get("category", "")
            ]
            for j, value in enumerate(row_data):
                cell = table.cell(i + 1, j)
                cell.text = value
                cell.fill.solid()
                cell.fill.fore_color.rgb = row_fill
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(9)

    # Category distribution - pie chart or text fallback
    categories = keywords_data.get("categoryDistribution", [])
    if categories:
        chart_image = generate_breakdown_chart_image(categories, "Category Distribution")

        if chart_image:
            # Add pie chart image
            slide.shapes.add_picture(chart_image, Inches(6.2), Inches(table_start_y),
                                     width=Inches(3.2), height=Inches(3.2))
        else:
            # Text fallback
            add_text_box(slide, "Category Distribution", Inches(6.2), Inches(table_start_y),
                         Inches(3.2), Inches(0.3), font_size=12, font_name=Brand.HEADING_FONT,
                         color=Brand.NAVY, bold=True)

            total = sum(c.get("value", 0) for c in categories)
            for i, cat in enumerate(categories[:5]):
                y = table_start_y + 0.4 + i * 0.35
                name = cat.get("label") or cat.get("name", "")
                value = cat.get("value", 0)
                pct = (value / total * 100) if total > 0 else 0
                add_text_box(slide, f"• {name}: {pct:.1f}%", Inches(6.2), Inches(y),
                             Inches(3.2), Inches(0.3), font_size=10, color=Brand.MID_GREY)

    return slide

def create_reviews_slide(prs, reviews_data, period_info):
    """Create the reviews sentiment analysis slide."""
    if not reviews_data:
        return None

    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    add_header_line(slide)
    add_footer(slide)

    # Title
    add_text_box(slide, "Review Sentiment Analysis", Inches(0.5), Inches(0.2), Inches(9), Inches(0.4),
                 font_size=24, font_name=Brand.HEADING_FONT, color=Brand.BLUE, bold=True)

    # Key Insights - with increased spacing to allow text wrapping
    insights = reviews_data.get("insights", [])
    content_start_y = 0.7
    if insights:
        add_text_box(slide, "Key Insights", Inches(0.5), Inches(0.65), Inches(4), Inches(0.25),
                     font_size=10, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)
        for i, insight in enumerate(insights[:3]):
            add_text_box(slide, f"• {insight}", Inches(0.5), Inches(0.93 + i * INSIGHT_SPACING),
                         Inches(4.3), Inches(INSIGHT_BOX_HEIGHT), font_size=8, color=Brand.MID_GREY)
        content_start_y = 0.93 + len(insights[:3]) * INSIGHT_SPACING + 0.15

    # Summary stats
    total_reviews = reviews_data.get("totalReviews", 0)
    avg_rating = reviews_data.get("averageRating", 0)
    rating_change = reviews_data.get("ratingChange", "")

    summary_text = f"Total Reviews: {total_reviews:,}  |  Average Rating: {avg_rating} ({rating_change})"
    add_text_box(slide, summary_text, Inches(0.5), Inches(content_start_y), Inches(9), Inches(0.25),
                 font_size=10, color=Brand.MID_GREY)

    # Sentiment distribution - pie chart or text fallback
    sentiment = reviews_data.get("sentiment", {})
    if sentiment:
        chart_image = generate_sentiment_breakdown_chart(sentiment)

        if chart_image:
            # Add sentiment pie chart
            slide.shapes.add_picture(chart_image, Inches(0.5), Inches(content_start_y + 0.35),
                                     width=Inches(2.8), height=Inches(2.8))
        else:
            # Text fallback
            add_text_box(slide, "Sentiment Distribution", Inches(0.5), Inches(content_start_y + 0.35),
                         Inches(3), Inches(0.25), font_size=11, font_name=Brand.HEADING_FONT,
                         color=Brand.NAVY, bold=True)

            pos = sentiment.get("positive", 0)
            neu = sentiment.get("neutral", 0)
            neg = sentiment.get("negative", 0)

            add_text_box(slide, f"Positive: {pos}%", Inches(0.5), Inches(content_start_y + 0.65),
                         Inches(2), Inches(0.25), font_size=10, color=Brand.GREEN)
            add_text_box(slide, f"Neutral: {neu}%", Inches(0.5), Inches(content_start_y + 0.95),
                         Inches(2), Inches(0.25), font_size=10, color=Brand.LIGHT_BLUE)
            add_text_box(slide, f"Negative: {neg}%", Inches(0.5), Inches(content_start_y + 1.25),
                         Inches(2), Inches(0.25), font_size=10, color=Brand.ORANGE)

    # Top themes table
    themes = reviews_data.get("topThemes", [])
    if themes:
        add_text_box(slide, "Top Review Themes", Inches(4), Inches(content_start_y + 0.25),
                     Inches(5.5), Inches(0.25), font_size=10, color=Brand.MID_GREY, align=PP_ALIGN.CENTER)

        rows = min(len(themes), 5) + 1
        cols = 3
        table = slide.shapes.add_table(rows, cols, Inches(4), Inches(content_start_y + 0.55),
                                        Inches(5.5), Inches(0.28 * rows)).table

        # Header
        headers = ["Theme", "Mentions", "Sentiment"]
        for j, header in enumerate(headers):
            cell = table.cell(0, j)
            cell.text = header
            cell.fill.solid()
            cell.fill.fore_color.rgb = Brand.TABLE_HEADER_BG
            p = cell.text_frame.paragraphs[0]
            p.font.bold = True
            p.font.size = Pt(9)
            p.font.color.rgb = Brand.INK

        # Data rows
        for i, theme in enumerate(themes[:5]):
            row_fill = Brand.WHITE if i % 2 == 0 else Brand.TABLE_ZEBRA
            sentiment_val = theme.get("sentiment", "")
            row_data = [
                theme.get("theme", ""),
                str(theme.get("mentions", "")),
                sentiment_val.capitalize() if sentiment_val else ""
            ]
            for j, value in enumerate(row_data):
                cell = table.cell(i + 1, j)
                cell.text = value
                cell.fill.solid()
                cell.fill.fore_color.rgb = row_fill
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(9)
                if j == 2:  # Sentiment column
                    if sentiment_val == "positive":
                        p.font.color.rgb = Brand.GREEN
                    elif sentiment_val == "negative":
                        p.font.color.rgb = Brand.ORANGE

    return slide

def create_recommendations_slide(prs, recommendations):
    """Create the strategic recommendations slide."""
    if not recommendations:
        return None

    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    add_header_line(slide)
    add_footer(slide)

    # Title
    add_text_box(slide, "Strategic Recommendations", Inches(0.5), Inches(0.3), Inches(9), Inches(0.5),
                 font_size=24, font_name=Brand.HEADING_FONT, color=Brand.BLUE, bold=True)

    for i, rec in enumerate(recommendations[:3]):
        y = 1 + i * 1.4

        # Number circle
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.5), Inches(y), Inches(0.4), Inches(0.4))
        circle.fill.solid()
        circle.fill.fore_color.rgb = Brand.ORANGE
        circle.line.fill.background()

        # Number text
        add_text_box(slide, str(i + 1), Inches(0.5), Inches(y), Inches(0.4), Inches(0.4),
                     font_size=14, font_name=Brand.HEADING_FONT, color=Brand.WHITE, bold=True,
                     align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

        # Recommendation title
        add_text_box(slide, rec.get("title", ""), Inches(1.1), Inches(y), Inches(8.4), Inches(0.35),
                     font_size=14, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)

        # Description
        add_text_box(slide, rec.get("description", ""), Inches(1.1), Inches(y + 0.4),
                     Inches(8.4), Inches(0.5), font_size=11, color=Brand.MID_GREY)

        # Impact
        impact = rec.get("impact", "")
        if impact:
            add_text_box(slide, f"Expected Impact: {impact}", Inches(1.1), Inches(y + 0.9),
                         Inches(8.4), Inches(0.3), font_size=10, color=Brand.BLUE)

    return slide

def create_appendix_slide(prs, appendix_data):
    """Create the appendix/methodology slide."""
    if not appendix_data:
        return None

    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    add_header_line(slide)
    add_footer(slide)

    # Title
    add_text_box(slide, "Appendix: Data & Methodology", Inches(0.5), Inches(0.2), Inches(9), Inches(0.4),
                 font_size=24, font_name=Brand.HEADING_FONT, color=Brand.BLUE, bold=True)

    left_y = 0.7

    # Data Sources
    data_sources = appendix_data.get("dataSources", [])
    if data_sources:
        add_text_box(slide, "Data Sources", Inches(0.5), Inches(left_y), Inches(4.5), Inches(0.25),
                     font_size=11, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)
        left_y += 0.3
        for source in data_sources:
            add_text_box(slide, f"• {source}", Inches(0.5), Inches(left_y), Inches(4.5), Inches(0.2),
                         font_size=9, color=Brand.MID_GREY)
            left_y += 0.22
        left_y += 0.15

    # Reporting Period
    reporting_period = appendix_data.get("reportingPeriod", {})
    if reporting_period:
        add_text_box(slide, "Reporting Period", Inches(0.5), Inches(left_y), Inches(4.5), Inches(0.25),
                     font_size=11, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)
        left_y += 0.3

        # 'period' is the current key; 'quarter' is the legacy alias and is wrong
        # for monthly, half-yearly, and yearly reports.
        rows = [
            ("Period", reporting_period.get("period") or reporting_period.get("quarter")),
            ("Date Range", reporting_period.get("dateRange")),
            ("Data Freshness", reporting_period.get("dataFreshness")),
        ]
        for label, value in rows:
            if value:
                add_text_box(slide, f"{label}: {value}", Inches(0.5), Inches(left_y),
                             Inches(4.5), Inches(0.18), font_size=9, color=Brand.MID_GREY)
                left_y += 0.2

        lag_note = reporting_period.get("lagNote")
        if lag_note:
            add_text_box(slide, f"Note: {lag_note}", Inches(0.5), Inches(left_y),
                         Inches(4.5), Inches(0.35), font_size=8, color=Brand.MID_GREY)

    right_y = 0.7

    # Calculation Notes
    calc_notes = appendix_data.get("calculationNotes", [])
    if calc_notes:
        add_text_box(slide, "Calculation Notes", Inches(5.2), Inches(right_y), Inches(4.5), Inches(0.25),
                     font_size=11, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)
        right_y += 0.3
        for note in calc_notes:
            add_text_box(slide, f"• {note}", Inches(5.2), Inches(right_y), Inches(4.5), Inches(0.35),
                         font_size=8, color=Brand.MID_GREY)
            right_y += 0.32
        right_y += 0.1

    # Location Coverage
    loc_coverage = appendix_data.get("locationCoverage", {})
    if loc_coverage:
        add_text_box(slide, "Location Coverage", Inches(5.2), Inches(right_y), Inches(4.5), Inches(0.25),
                     font_size=11, font_name=Brand.HEADING_FONT, color=Brand.NAVY, bold=True)
        right_y += 0.3

        for key, label in [("totalLocations", "Total Locations"),
                           ("geographicCoverage", "Geographic Coverage"),
                           ("locationsWithGoogleData", "Locations with Google Data"),
                           ("locationsWithReviews", "Locations with Reviews")]:
            value = loc_coverage.get(key)
            if value:
                suffix = " active locations" if key == "totalLocations" else ""
                # Geographic coverage can have long country lists - give it more height
                box_height = 0.5 if key == "geographicCoverage" else 0.2
                row_spacing = 0.55 if key == "geographicCoverage" else 0.25
                add_text_box(slide, f"{label}: {value}{suffix}", Inches(5.2), Inches(right_y),
                             Inches(4.5), Inches(box_height), font_size=9, color=Brand.MID_GREY)
                right_y += row_spacing

    return slide

# =============================================================================
# Main Generation Function
# =============================================================================
def generate_report(data, output_path, is_draft=False):
    """
    Generate the complete PowerPoint presentation.

    Args:
        data: Report data dictionary
        output_path: Path to save the PPTX file
        is_draft: If True, adds "DRAFT - PENDING REVIEW" watermark on every slide
    """
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    # Track slides for watermarking
    slides_created = []

    # Period info for subtitles
    period_info = {
        "period": data.get("period"),
        "priorPeriod": data.get("priorPeriod"),
        # Carried so the metrics slides can honour an explicit --period without
        # re-guessing the report type from the period label.
        "periodType": get_period_type(data),
    }

    # Create slides
    print("Creating title slide...")
    slide = create_title_slide(prs, data)
    slides_created.append(slide)

    print("Creating executive summary...")
    slides_created.append(create_executive_summary(prs, data))

    # Platform metrics
    if data.get("google"):
        print("Creating Google Business Profile slide...")
        slides_created.append(create_metrics_slide(prs, "Google Business Profile", data["google"], period_info))

    if data.get("facebook"):
        print("Creating Facebook Performance slide...")
        slides_created.append(create_metrics_slide(prs, "Facebook Performance", data["facebook"], period_info))

    if data.get("apple"):
        print("Creating Apple Maps Performance slide...")
        slides_created.append(create_metrics_slide(prs, "Apple Maps Performance", data["apple"], period_info))

    # Keywords
    if data.get("keywords"):
        print("Creating Search Keywords slide...")
        slides_created.append(create_keywords_slide(prs, data["keywords"], period_info))

    # Reviews
    if data.get("reviews"):
        print("Creating Reviews Sentiment slide...")
        slide = create_reviews_slide(prs, data["reviews"], period_info)
        if slide:
            slides_created.append(slide)

    # Recommendations
    if data.get("recommendations"):
        print("Creating Recommendations slide...")
        slide = create_recommendations_slide(prs, data["recommendations"])
        if slide:
            slides_created.append(slide)

    # Appendix
    if data.get("appendix"):
        print("Creating Appendix slide...")
        slide = create_appendix_slide(prs, data["appendix"])
        if slide:
            slides_created.append(slide)

    # Add watermarks to all slides if in draft mode
    if is_draft:
        print("Adding draft watermarks...")
        for slide in slides_created:
            if slide:  # Some functions may return None
                add_draft_watermark(slide)

    # Save presentation
    prs.save(output_path)
    print(f"Presentation generated: {output_path}")

# =============================================================================
# CLI Interface
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Generate PinMeTo Location Analytics PowerPoint")
    parser.add_argument("--data", required=True, help="Path to JSON data file")
    parser.add_argument("--output", required=True, help="Output PPTX file path")
    parser.add_argument("--period", default="quarterly",
                        choices=["monthly", "quarterly", "half-yearly", "yearly"],
                        help="Report period type")
    parser.add_argument("--draft", action="store_true",
                        help="Add 'DRAFT - PENDING REVIEW' watermark on every slide")

    args = parser.parse_args()

    # Load data
    if not os.path.exists(args.data):
        print(f"Error: Data file not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.data, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.data}: {e}", file=sys.stderr)
        sys.exit(1)

    # The explicit --period wins unless the data file already states one.
    data["periodType"] = get_period_type(data) or args.period

    # Generate report
    try:
        generate_report(data, args.output, is_draft=args.draft)
        if args.draft:
            print("Note: This is a DRAFT presentation. Run without --draft flag to generate final version.")
    except PermissionError:
        print(f"Error: Cannot write to {args.output} - permission denied", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating presentation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
