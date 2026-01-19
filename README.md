# PinMeTo Location Reports Skill

[![Latest Release](https://img.shields.io/github/v/release/PinMeTo/pinmeto-location-reports-skill)](https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest)
[![Download .skill](https://img.shields.io/badge/Download-.skill-green)](https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest/download/pinmeto-location-reports.skill)

Generate professional, board-ready reports from your PinMeTo location analytics data using Claude Desktop, Claude Code, or Claude.ai.

## What This Skill Does

This skill transforms your PinMeTo multi-location analytics data into polished PDF and PowerPoint reports. Perfect for:

- Executive presentations
- Board meetings
- Quarterly business reviews
- Marketing performance summaries

## Report Types

| Type | Best For | Example Request |
|------|----------|-----------------|
| **Monthly** | Regular check-ins | "Create a report for October 2024" |
| **Quarterly** | Business reviews | "Generate Q3 2024 report" |
| **Half-Yearly** | Mid-year summaries | "Create H1 2024 report" |
| **Yearly** | Annual reviews | "Generate 2024 annual report" |

## What's Included in Reports

Each report contains insights from your connected platforms:

- **Google Business Profile** - Views, searches, website clicks, direction requests, phone calls
- **Facebook Pages** - Page views, reach, engagement metrics
- **Apple Maps** - Discovery views, directions, website taps
- **Reviews & Ratings** - Average ratings, review sentiment, top themes
- **Search Keywords** - How customers are finding your locations
- **Strategic Recommendations** - Data-driven action items

## How to Use

Simply ask Claude to create a report. Here are some examples:

> "Create a monthly location report for November 2024"

> "Generate a Q4 2024 report as PDF and PowerPoint"

> "Make an annual report for 2024 for our board meeting"

> "Create a half-yearly report for H2 2024"

## Prerequisites

Before installing this skill, you need the [PinMeTo MCP Server](https://github.com/PinMeTo/pinmeto-location-mcp) connected to your PinMeTo account. The MCP server provides access to your location analytics data that this skill uses to generate reports.

See the [PinMeTo MCP Server documentation](https://github.com/PinMeTo/pinmeto-location-mcp#installation) for installation instructions.

## Installation

### For Claude Desktop & Claude.ai

**[📥 Download Latest Version](https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest/download/pinmeto-location-reports.skill)**

1. Download the [latest .skill file](https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest/download/pinmeto-location-reports.skill)
2. Go to **Settings** → **Capabilities** in Claude
3. Enable **"Code execution and file creation"**
4. Click **"Upload skill"** and select the downloaded `.skill` file
5. The skill will be available immediately in your conversations

### For Claude Code (CLI)

Install via command line:

```bash
# Download and install the latest version
curl -L -o pinmeto-location-reports.skill \
  https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest/download/pinmeto-location-reports.skill

# Install globally (available in all projects)
mkdir -p ~/.claude/skills
mv pinmeto-location-reports.skill ~/.claude/skills/

# OR install locally (for current project only)
mkdir -p .claude/skills
mv pinmeto-location-reports.skill .claude/skills/
```

Claude Code will automatically discover and load the skill. No restart required.

### Verify Installation

Ask Claude to create a report:
> "Create a monthly location report for November 2024"

If the skill is installed correctly, Claude will use it to generate your report.

### Troubleshooting

**Skill not activating automatically?**

If Claude doesn't use the skill automatically, explicitly tell it to use the skill:

> "Use the PinMeTo Location Reports skill to create a monthly report for November 2024"

or

> "Using the location reports skill, generate a Q4 2024 report"

This helps Claude recognize that you want to use this specific skill for your request.

## Requirements

**For Claude Desktop & Claude.ai:**
- Claude Desktop or Claude.ai with Pro, Team, or Enterprise plan
- Code execution capability enabled
- [PinMeTo MCP Server](https://github.com/PinMeTo/pinmeto-location-mcp) connected to your PinMeTo account

**For Claude Code:**
- Claude Code CLI (latest version)
- [PinMeTo MCP Server](https://github.com/PinMeTo/pinmeto-location-mcp) connected to your PinMeTo account

## Output Formats

- **PDF** - Multi-page document with charts and tables, ideal for printing or email
- **PowerPoint** - Presentation-ready slides in 16:9 format, perfect for meetings

## Tips for Best Results

1. **Be specific about dates** - "October 2024" is clearer than "last month"
2. **Allow for data lag** - Google metrics have a ~10 day reporting delay
3. **Request both formats** - Say "PDF and PowerPoint" if you need both
4. **Specify the audience** - Mention "board meeting" or "team review" for appropriate detail level

## Questions?

Ask Claude! It can explain any metric, clarify report sections, or help you understand the data.

## License

© 2025 PinMeTo AB. All rights reserved.

Use of this skill is restricted to authorized users of PinMeTo's services.
See [LICENSE](./LICENSE) for full terms.
