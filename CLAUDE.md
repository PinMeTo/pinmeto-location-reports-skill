# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code skill** for generating professional location analytics reports from PinMeTo's multi-location brand analytics platform. The skill creates board-ready PDF and PowerPoint reports using data fetched via the PinMeTo MCP server.

For detailed project documentation, data schemas, and domain knowledge, see [AGENTS.md](./AGENTS.md).

## Architecture

```
pinmeto-location-analytics-skill/
├── pinmeto-location-reports/         # Skill package
│   ├── SKILL.md                      # Skill definition (triggers, workflow, branding)
│   ├── scripts/
│   │   ├── generate_pdf.py           # ReportLab-based PDF generation
│   │   ├── generate_pptx.py           # python-pptx-based PowerPoint generation
│   │   └── fetch_pinmeto_data.js     # MCP client for fetching real data
│   ├── references/                   # Period-specific report structures
│   └── assets/                       # Logos and HTML templates
├── docs/                             # PinMeTo brand assets
├── dist/                             # Packaged skill (.skill file)
└── AGENTS.md                         # Project documentation and beads workflow
```

## Commands

### PDF Generation
```bash
cd pinmeto-location-reports
pip install reportlab pillow
python scripts/generate_pdf.py --data report_data.json --output report.pdf --period quarterly
```

### PPTX Generation
```bash
cd pinmeto-location-reports
pip install python-pptx pillow
python scripts/generate_pptx.py --data report_data.json --output report.pptx --period quarterly
```

### Fetch Real Data from PinMeTo MCP
```bash
node scripts/fetch_pinmeto_data.js --year 2025 --output pinmeto_2025_data.json
```
