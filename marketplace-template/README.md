# PinMeTo Skills Marketplace

Official Claude Code skills for PinMeTo's location analytics platform.

## Available Skills

### 📊 PinMeTo Location Reports

Generate professional location analytics reports in PDF and PowerPoint format.

**Features:**
- PDF report generation with ReportLab
- PowerPoint presentations with python-pptx
- Real-time data fetching from PinMeTo MCP server
- Monthly, quarterly, half-yearly, and yearly report periods
- Professional branding, validated colourblind-safe chart palette

**Version:** 1.1.0
**Requires:** [PinMeTo Location MCP](https://github.com/PinMeTo/pinmeto-location-mcp) 4.0.0 or later
**Repository:** [pinmeto-location-reports-skill](https://github.com/PinMeTo/pinmeto-location-reports-skill)

## Installation

### Using Claude Code Plugin Manager

```bash
claude /plugin install https://github.com/PinMeTo/skills
```

Then enable the specific skill you want:

```bash
claude /plugin enable pinmeto-location-reports
```

### Manual Installation

1. Download the skill file from the [`skills/`](./skills/) directory
2. Copy to your Claude Code skills directory:

```bash
cp skills/pinmeto-location-reports.skill ~/.claude/skills/
```

## Usage

Once installed, you can use the skill in Claude Code:

```
Generate a quarterly location analytics report for Q4 2024
```

Claude will invoke the skill and guide you through the report generation process.

## Requirements

- Claude Code 2.0.20 or later (Skills support)
- PinMeTo MCP server configured and running
- Python 3.8+ with required packages (reportlab, python-pptx, pillow)

## For Developers

If you're developing new PinMeTo skills:

1. Fork the skill template repository
2. Develop and test your skill
3. Package using `./package-skill.sh`
4. Submit a PR to this marketplace repository

See [PUBLISHING.md](https://github.com/PinMeTo/pinmeto-location-reports-skill/blob/main/PUBLISHING.md) for detailed instructions.

## Support

For issues or questions:
- Skill issues: Open an issue in the specific skill repository
- Marketplace issues: Open an issue in this repository
- PinMeTo platform: Contact PinMeTo support

## License

Each skill has its own license. See individual skill repositories for details.
