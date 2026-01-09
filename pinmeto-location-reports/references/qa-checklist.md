# Quality Assurance Checklist

Complete this checklist before delivering any report to ensure quality and accuracy.

## Contents

- [Pre-Generation Checks](#pre-generation-checks)
- [Data Quality Checks](#data-quality-checks)
- [Report Content Checks](#report-content-checks)
- [Branding Compliance](#branding-compliance)
- [Format-Specific Checks](#format-specific-checks)
- [Client Review](#client-review)
- [Final Review](#final-review)
- [Issue Resolution](#issue-resolution)
- [Sign-Off](#sign-off)

---

## Pre-Generation Checks

### Request Validation
- [ ] Report period correctly identified (monthly/quarterly/half-yearly/yearly)
- [ ] Date range is specific and valid
- [ ] Date range accounts for Google's ~10-day data lag
- [ ] Location scope is clear (all locations or specific store IDs)
- [ ] Output format confirmed (PDF, PPTX, or both)
- [ ] Comparison types appropriate for period (MoM, QoQ, HoH, YoY)

### Data Availability
- [ ] MCP server connection verified
- [ ] All required tools accessible
- [ ] Prior period data available for comparisons
- [ ] Prior year data available for YoY comparisons

## Data Quality Checks

### Completeness
- [ ] All MCP tool calls completed successfully
- [ ] No missing data for required metrics
- [ ] All locations included (or specified subset)
- [ ] Keywords retrieved up to specified limit (10/15/20/25)

### Accuracy
- [ ] Date ranges in responses match request
- [ ] Comparison periods are correct
- [ ] No negative values where impossible (views, reviews)
- [ ] Ratings within valid range (1.0-5.0)
- [ ] Percentage changes calculated correctly

### Consistency
- [ ] Location counts consistent across all tools
- [ ] Time periods aligned across platforms
- [ ] Totals match sum of components
- [ ] YoY comparisons use same period structure

## Report Content Checks

### Structure
- [ ] Page count within specified range
- [ ] All required sections included
- [ ] Sections in correct order
- [ ] Table of contents accurate (if included)

### Data Presentation
- [ ] All numbers formatted consistently (thousands separators, decimals)
- [ ] Percentages shown with consistent precision (1 decimal place)
- [ ] Currency formatted appropriately (if applicable)
- [ ] Dates formatted consistently

### Charts & Visualizations
- [ ] All charts have clear titles
- [ ] Axes labeled with units
- [ ] Legend included where needed
- [ ] Colors consistent with brand guidelines
- [ ] Data labels readable

### Tables
- [ ] Column headers clear and descriptive
- [ ] Row headers present
- [ ] Data aligned properly
- [ ] Totals/averages calculated correctly
- [ ] Comparison columns labeled with periods

### Text Content
- [ ] Executive summary reflects actual data
- [ ] No placeholder text remaining ([PLACEHOLDER])
- [ ] Insights are data-driven
- [ ] Recommendations are actionable
- [ ] No grammatical errors in generated text

## Branding Compliance

### Colors
- [ ] Primary Blue (#3399FF) used correctly
- [ ] Accent Orange (#FF8854) used for highlights
- [ ] Dark backgrounds use Blue Marine (#001334)
- [ ] Light backgrounds use Grey (#F2F3F4)
- [ ] No off-brand colors used

### Typography
- [ ] Headlines use Montserrat
- [ ] Long body text uses Recursive (if applicable)
- [ ] Font sizes appropriate for format
- [ ] Text contrast sufficient for readability

### Logo
- [ ] PinMeTo logo present on cover
- [ ] Logo in header/footer (if applicable)
- [ ] Logo not stretched or distorted
- [ ] Clear space maintained around logo
- [ ] Correct logo variant used (landscape/vertical)

## Format-Specific Checks

### PDF Reports
- [ ] Page numbers present
- [ ] Headers/footers consistent
- [ ] Margins appropriate
- [ ] Images render clearly
- [ ] Links functional (if included)
- [ ] File size reasonable (<10MB)

### PowerPoint Presentations
- [ ] Slide dimensions correct (16:9)
- [ ] Master slide styling consistent
- [ ] Animations appropriate (minimal or none for data)
- [ ] Speaker notes included (if requested)
- [ ] File opens without errors

## Client Review

**Important:** Before delivering the final report, generate a draft version for client review.

### Draft Generation
- [ ] Generated report with `--draft` flag
- [ ] Watermark ("DRAFT - PENDING REVIEW") visible on all pages/slides
- [ ] File named with "_DRAFT" suffix (e.g., `Brand_Q4_Report_DRAFT.pdf`)

### Present to Client
- [ ] Summary of key data points provided
- [ ] Review checklist shared (see `references/client-review.md`)
- [ ] Clear instructions for approval or feedback

### Client Verification
Have the client verify:
- [ ] Executive summary narrative is accurate
- [ ] KPI values are present and correct
- [ ] Charts and graphs render properly
- [ ] Tables have complete data
- [ ] Text content is correct (no placeholders)
- [ ] Branding looks correct

### Handle Feedback
- [ ] If changes requested: fix issues, regenerate draft with watermark
- [ ] Repeat review until approved
- [ ] If approved: regenerate final version without `--draft` flag
- [ ] Verify watermark is removed from final version

## Final Review

### Accuracy Final Check
- [ ] Cross-check 3 random numbers against source data
- [ ] Verify executive summary matches detailed data
- [ ] Confirm period labels accurate throughout

### Readability Check
- [ ] Report scannable for key insights
- [ ] Visual hierarchy clear
- [ ] Most important information prominent
- [ ] Appropriate for target audience (executives)

### Delivery Readiness
- [ ] File named appropriately: `[Brand]_[Period]_Report_[Date].[ext]`
- [ ] File size appropriate for delivery method
- [ ] Confidentiality notice included (if required)
- [ ] Report metadata correct

## Issue Resolution

### Common Issues & Fixes

| Issue | Resolution |
|-------|------------|
| Missing comparison data | Note in report, proceed with available data |
| Inconsistent location counts | Use intersection of all data sources |
| Negative growth shown as positive | Verify calculation, fix sign |
| Charts not rendering | Fall back to tables |
| Logo not displaying | Use JPG fallback |

### Escalation Triggers

Flag for human review if:
- Data shows >100% change (verify accuracy)
- Rating changed by >0.5 in one period
- Total views/actions dropped >50%
- Multiple locations missing data
- Comparison period unavailable

## Sign-Off

```
Report: [Report Name]
Period: [Period]
Generated: [Date]

Data Quality: [ ] Pass [ ] Issues noted
Branding: [ ] Pass [ ] Issues noted
Content: [ ] Pass [ ] Issues noted

Ready for Delivery: [ ] Yes [ ] Needs revision
```
