# PinMeTo Brand Reference

Authoritative source: **PinMeTo Graphic Manual (May 2026)** and **PinMeTo Brand Book**. Where
this file and a generator disagree, the generator is wrong: fix the code, not this file.

Read this file when editing a generator's tokens, adding a chart type, or answering a brand
question. Producing a report from unchanged generators does not require it: both generators
already hardcode everything below.

## Brand Colours

| Name | Hex | RGB | Pantone | Usage |
|------|-----|-----|---------|-------|
| Blue | `#3399FF` | 51 / 153 / 255 | 2727C | Headings, rules, brand accents |
| Orange | `#FF8854` | 255 / 136 / 84 | 1635C | Highlights, emphasis |
| Navy | `#000050` | 0 / 0 / 80 | — | Body ink, dark backgrounds |
| Light Blue | `#BBD9FA` | 187 / 217 / 250 | — | Secondary backgrounds |
| Mid Grey | `#333333` | 51 / 51 / 51 | 412C | Secondary text |
| Grey | `#F2F3F4` | 242 / 243 / 244 | 663C | Light backgrounds |

Navy is `#000050`. Earlier versions of this skill used `#001334`, which is not a brand colour.

## Text Contrast

WCAG 2.1 AA is the floor, and EU accessibility law requires it. "Large" means regular weight at
18pt+ or bold/black weight at 14pt+.

| Text | Minimum ratio |
|------|---------------|
| Normal (under ~18pt) | 4.5:1 |
| Large (18pt+, or 14pt+ bold) | 3.0:1 |
| AAA enhanced, ideal for body | 7:1 |

Measured pairs from the Brand Book, which decide every text-on-colour choice in a report:

| Pair | Ratio | Verdict |
|------|-------|---------|
| Navy `#000050` on Orange `#FF8854` | 8.9:1 | Safe at all sizes |
| Navy `#000050` on Blue `#3399FF` | 5.9:1 | Safe at all sizes |
| White on Blue `#3399FF` | 3.0:1 | Large **and** bold/black weight only |
| White on Orange `#FF8854` | 2.0:1 | **Never.** Fails even the large-text floor |

Use Navy as the standard dark text on both brand backgrounds: it passes on both and stays
on-brand. Never set body copy in white on a brand colour. White is acceptable only for big,
short, bold display text on Blue, never on Orange.

## Typography

**Montserrat is the only brand typeface.** No serif or mono companion exists; earlier versions of
this skill named "Recursive Mono Linear" for body text, which was never a PinMeTo font.

| Role | Face |
|------|------|
| Headlines, KPI values, table headers | Montserrat Bold |
| Subheadings, emphasis | Montserrat SemiBold |
| Body, labels, chart text | Montserrat Regular |

The three faces ship in `assets/fonts/` under the SIL Open Font License (`assets/fonts/OFL.txt`),
so a report renders on-brand on a machine that has never installed Montserrat.

**PDF** embeds the fonts, subset, and is therefore the format to deliver when typography must be
guaranteed. If a TTF is missing or unreadable, `generate_pdf.py` prints a warning and falls back
to Helvetica for the whole document rather than mixing families or aborting.

**PPTX** references fonts by name; python-pptx cannot embed a typeface. Slide text renders in
Montserrat only where the viewer has it installed, otherwise PowerPoint substitutes. Chart
images are unaffected: they are rasterised at generation time with the bundled TTFs.

## Chart and Status Colours

The brand palette is a UI palette. Measured against a white chart surface, `#BBD9FA` reads gray
and both `#3399FF` and `#FF8854` fall below the 3:1 contrast floor, so brand hues are kept for
typography and rules rather than for data marks. Data marks use deepened steps of the brand hues.

| Token | Hex | Usage |
|-------|-----|-------|
| Chart blue | `#1F7AE0` | Categorical slot 1, all single-series bars |
| Chart orange | `#E8690B` | Categorical slot 2 |
| Chart violet | `#5B4B8A` | Categorical slot 3 |
| Prior wash | `#C9DCF3` | Prior-period series (de-emphasis, not a slot) |
| Status good | `#0E7C4A` | Positive change |
| Status bad | `#CC3311` | Negative change |
| Star amber | `#C77700` | Star rating fill |

**Direction is never colour alone.** Every delta carries a triangle (▲ / ▼ / –) alongside the
status colour, because the previous green/orange pair measured ΔE 1.8 under protanopia:
red-green colourblind readers could not tell a rise from a fall.

Both generators define these tokens at the top of the file. After changing them, re-run the
`dataviz` skill's validator rather than eyeballing the result:

```bash
node <dataviz-skill>/scripts/validate_palette.js "#1F7AE0,#E8690B,#5B4B8A" --mode light
```

## Chart Conventions

- Categorical hues are assigned in fixed slot order, so a chart with fewer series never repaints
  the survivors.
- Nominal categories (keyword types, themes) get **one** hue for every bar. Identity comes from
  the labels; a darker-where-bigger ramp would double-encode length as colour.
- Sentiment is polarity, so it is the one breakdown where colour means state: good, neutral gray,
  bad.
- Part-to-whole breakdowns render as labelled horizontal bars, not pies. These distributions
  routinely have close values (52% vs 38%), where arc length stops being comparable.
- Only the current series is directly labelled. A number above every bar goes unread; the
  recessive grid and the table carry the rest.
- A KPI with a `max` renders as stars (see [data-schema.md](data-schema.md)). The last star fills
  to the exact remainder rather than rounding to a half, so the stars never overstate the printed
  number.

## Logo Usage

Logos live in `assets/logos/` as SVG and JPG. python-pptx and ReportLab both need the raster
versions, so the generators use the JPGs.

- Landscape lockup for report headers and footers; vertical for cover pages and title slides.
- Maintain clear space of at least the logo height around it.
- Never stretch, recolour, or rearrange logo elements.
- On a dark or busy background, use the all-white logo rather than recolouring the standard one.

## Tone of Voice for Report Narrative

Generated prose (executive summaries, insights, recommendations) carries the brand voice too.

**Is:** professional, clear, confident, structured, insightful, modern.
**Is not:** buzzword-heavy, overly technical, hype-driven, casual or slang-heavy, visionary
without substance.

The governing principle is "Intelligent, not loud": communicate with confidence, not
exaggeration, and never overpromise.

- Frame findings as outcomes (visits, engagement, revenue, competitive position), not features
  or raw metric names.
- Avoid fear-driven or alarmist framing for a declining metric. Report the decline plainly and
  give the next action. Guide rather than pressure.
- Explain value in plain, outcome-driven language. Simplify any term that needs explaining.
- Use **customer** or **user**, never "client". The brand treats the relationship as a
  partnership, not a transaction.
