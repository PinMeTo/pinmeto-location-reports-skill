# Customer Review Checklist

Use this checklist when reviewing draft reports before finalizing.

## Overview

Draft reports include a visible "DRAFT - PENDING REVIEW" watermark on every page/slide. This watermark is removed when you approve the report and the final version is generated.

---

## Review Sections

### 1. Executive Summary

- [ ] Narrative accurately describes the period's performance
- [ ] Tone is appropriate for the audience (executive/board-level)
- [ ] Key highlights reflect actual data trends
- [ ] No inaccurate claims or misrepresentations

**Common issues:**
- Narrative mentions events that didn't occur (e.g., "strong holiday performance" when there were issues)
- Tone too technical for executive audience
- Missing context for significant changes

### 2. KPI Values

- [ ] All expected metrics are present
- [ ] Values appear reasonable and accurate
- [ ] Change indicators (%, YoY, QoQ) are correct
- [ ] No obviously missing or zero values where data should exist

**Common issues:**
- Values showing as "N/A" when data should be available
- Percentage changes that seem too high (>100% may need verification)
- Missing metrics that were expected in the report

### 3. Charts & Graphs

- [ ] All charts render properly (no blank or broken charts)
- [ ] Chart titles are descriptive and accurate
- [ ] Axis labels are readable
- [ ] Legend is present where needed
- [ ] Data in charts matches table values
- [ ] Comparison bars/lines show correct periods

**Common issues:**
- Charts appearing blank or with placeholder data
- Missing legend making bars/lines indistinguishable
- Wrong period labels on comparison data

### 4. Tables

- [ ] All rows have complete data (no unexpected blanks)
- [ ] Column headers are correct and descriptive
- [ ] Numbers are formatted consistently (commas, decimals)
- [ ] Totals/averages calculate correctly
- [ ] Metric names display properly (not blank)

**Common issues:**
- Missing "name" field causing blank metric labels
- Inconsistent number formatting
- Tables cut off or wrapping incorrectly

### 5. Text Content

- [ ] Section titles are correct
- [ ] No placeholder text remaining (e.g., "[PLACEHOLDER]")
- [ ] Insights are data-driven and relevant
- [ ] Recommendations are actionable
- [ ] No grammatical or spelling errors
- [ ] Period names are correct throughout

**Common issues:**
- Wrong quarter/year mentioned in text
- Generic placeholder recommendations
- Insights that don't match the data shown

### 6. Branding & Layout

- [ ] PinMeTo logo appears correctly
- [ ] Colors match brand guidelines
- [ ] Fonts are consistent throughout
- [ ] Page numbers are present and correct
- [ ] Headers/footers are consistent
- [ ] Overall layout is professional and readable

**Common issues:**
- Logo stretched or distorted
- Inconsistent spacing between sections
- Text overlapping or cut off

---

## Providing Feedback

### For Approved Reports

Simply respond with "Approved" and the final version will be generated without the watermark.

### For Reports Needing Changes

Be specific about what needs correction:

**Good feedback examples:**
- "The executive summary mentions 'strong Q4 growth' but we actually had supply issues in December. Please adjust the narrative."
- "The Google views chart is blank - can you regenerate it?"
- "The KPI section is missing the 'Total Reviews' metric."
- "The table on page 3 has a blank row - the metric name is missing."

**Less helpful feedback:**
- "Something looks wrong" (too vague)
- "Fix the data" (which data?)

---

## Correction Workflow

1. **You provide feedback** - Describe what needs to be changed
2. **Claude fixes the issue** - Updates data JSON or regenerates charts
3. **New draft generated** - Still includes watermark for verification
4. **Review again** - Verify the fix, provide more feedback if needed
5. **Approve when ready** - Final version generated without watermark

---

## Quick Reference

| Check | What to Look For |
|-------|-----------------|
| Executive Summary | Accurate narrative, appropriate tone |
| KPIs | All metrics present, values correct |
| Charts | Render properly, correct labels |
| Tables | Complete data, no blank cells |
| Text | No placeholders, correct periods |
| Branding | Logo, colors, formatting correct |
