# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code skill** for generating professional location analytics reports from PinMeTo's multi-location brand analytics platform. The skill creates board-ready PDF and PowerPoint reports using data fetched via the PinMeTo MCP server.

For detailed project documentation, data schemas, and domain knowledge, see [AGENTS.md](./AGENTS.md).

## Architecture

```
pinmeto-location-reports-skill/
├── pinmeto-location-reports/         # Skill package
│   ├── SKILL.md                      # Skill definition (triggers, workflow, branding)
│   ├── scripts/
│   │   ├── generate_pdf.py           # ReportLab-based PDF generation
│   │   ├── generate_pptx.py           # python-pptx-based PowerPoint generation
│   │   ├── validate_report_data.py   # Schema check for report_data.json
│   │   ├── check_mcp_parity.js       # Verifies the MCP tool surface
│   │   └── fetch_pinmeto_data.js     # MCP client for fetching real data
│   ├── references/                   # Report structures, schema, branding
│   └── assets/                       # Logos and bundled Montserrat fonts
├── docs/                             # PinMeTo brand assets
├── dist/                             # Packaged skill (.skill file)
└── AGENTS.md                         # Project documentation and beads workflow
```

## Commands

### PDF Generation
```bash
cd pinmeto-location-reports
pip install reportlab pillow matplotlib
python scripts/generate_pdf.py --data report_data.json --output report.pdf --period quarterly
```

`matplotlib` is a hard dependency here: `generate_pdf.py` imports it at module level, so a
missing install is an ImportError before any work happens.

### PPTX Generation
```bash
cd pinmeto-location-reports
pip install python-pptx pillow matplotlib
python scripts/generate_pptx.py --data report_data.json --output report.pptx --period quarterly
```

`generate_pptx.py` treats `matplotlib` as optional: without it the script warns and degrades to
text-based charts instead of failing. The asymmetry with the PDF path is deliberate but easy to
trip over, so install matplotlib for both.

Both generators register the bundled Montserrat faces from `assets/fonts/` with ReportLab and
matplotlib. If those TTFs are missing the PDF falls back to Helvetica document-wide and says so
on stderr; output is still produced but is not brand-compliant.

### Fetch Real Data from PinMeTo MCP
```bash
node scripts/fetch_pinmeto_data.js --year 2025 --output pinmeto_2025_data.json
```
