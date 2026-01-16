# PinMeTo Location Analytics Skill

[![Latest Release](https://img.shields.io/github/v/release/PinMeTo/pinmeto-location-reports-skill)](https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest)
[![Download](https://img.shields.io/github/downloads/PinMeTo/pinmeto-location-reports-skill/total)](https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest/download/pinmeto-location-reports.skill)

Generate professional, board-ready reports from your PinMeTo location analytics data using Claude Desktop.

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

> "Create a monthly location analytics report for November 2024"

> "Generate a Q4 2024 report as PDF and PowerPoint"

> "Make an annual report for 2024 for our board meeting"

> "Create a half-yearly report for H2 2024"

## Installation

### Step 1: Download the Skill

**[📥 Download Latest Version](https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest/download/pinmeto-location-reports.skill)**

Or install via command line:

```bash
# Download and install the latest version
curl -L -o pinmeto-location-reports.skill https://github.com/PinMeTo/pinmeto-location-reports-skill/releases/latest/download/pinmeto-location-reports.skill
mkdir -p ~/.claude/skills
mv pinmeto-location-reports.skill ~/.claude/skills/
```

### Step 2: Restart Claude Desktop

After copying the `.skill` file to `~/.claude/skills/`, restart Claude Desktop to load the skill.

### Step 3: Verify Installation

In Claude Desktop, you should now be able to ask for location analytics reports and Claude will use this skill to generate them.

## Requirements

- **Claude Desktop** (latest version)
- **PinMeTo MCP Server** connected to your PinMeTo account

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
