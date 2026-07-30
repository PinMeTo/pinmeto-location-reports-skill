# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds


<!-- bv-agent-instructions-v1 -->

---

## Beads Workflow Integration

This project uses [beads_viewer](https://github.com/Dicklesworthstone/beads_viewer) for issue tracking. Issues are stored in `.beads/` and tracked in git.

### Essential Commands

```bash
# View issues (launches TUI - avoid in automated sessions)
bv

# CLI commands for agents (use these instead)
bd ready              # Show issues ready to work (no blockers)
bd list --status=open # All open issues
bd show <id>          # Full issue details with dependencies
bd create --title="..." --type=task --priority=2
bd update <id> --status=in_progress
bd close <id> --reason="Completed"
bd close <id1> <id2>  # Close multiple issues at once
bd sync               # Commit and push changes
```

### Workflow Pattern

1. **Start**: Run `bd ready` to find actionable work
2. **Claim**: Use `bd update <id> --status=in_progress`
3. **Work**: Implement the task
4. **Complete**: Use `bd close <id>`
5. **Sync**: Always run `bd sync` at session end

### Key Concepts

- **Dependencies**: Issues can block other issues. `bd ready` shows only unblocked work.
- **Priority**: P0=critical, P1=high, P2=medium, P3=low, P4=backlog (use numbers, not words)
- **Types**: task, bug, feature, epic, question, docs
- **Blocking**: `bd dep add <issue> <depends-on>` to add dependencies

### Session Protocol

**Before ending any session, run this checklist:**

```bash
git status              # Check what changed
git add <files>         # Stage code changes
bd sync                 # Commit beads changes
git commit -m "..."     # Commit code
bd sync                 # Commit any new beads changes
git push                # Push to remote
```

### Best Practices

- Check `bd ready` at session start to find available work
- Update status as you work (in_progress → closed)
- Create new issues with `bd create` when you discover tasks
- Use descriptive titles and set appropriate priority/type
- Always `bd sync` before ending session

<!-- end-bv-agent-instructions -->

---

## Project Documentation

### Key Components

**SKILL.md** - The skill definition file that Claude reads when invoking this skill. Contains:
- Report period detection patterns (monthly, quarterly, half-yearly, yearly)
- MCP tool reference for PinMeTo data fetching
- Date range calculation logic
- Brand color palette and typography
- Report generation workflow steps

**Report Generators:**
- `generate_pdf.py`: Uses ReportLab for multi-page PDFs with charts (line, bar, pie), tables, and branded styling
- `generate_pptx.py`: Uses python-pptx + matplotlib for 16:9 presentations with image-based charts for Keynote compatibility

Both are pure Python (`reportlab`, `python-pptx`, `pillow`, `matplotlib`). The skill has no
runtime npm dependencies; the Node scripts use built-in modules only.

**Data and Validation Scripts:**
- `fetch_pinmeto_data.js`: Batch fetch a full year over stdio MCP. Resolves the server via
  `--server`, `PINMETO_MCP_PATH`, local `node_modules`, or an installed desktop extension.
- `check_mcp_parity.js`: Compares the connected server's tool surface against the contract the
  skill assumes. Exits non-zero on drift.
- `validate_report_data.py`: Validates report data JSON before generation.

**Packaging:**
To package the skill for distribution, run:
```bash
./package-skill.sh
```
This creates a `.skill` file in the `dist/` directory that can be installed in Claude Code.

### Data Flow

1. Parse user request → determine period type and date range
2. Validate dates (Google has ~10-day data lag)
3. Fetch data via PinMeTo MCP tools (`pinmeto_get_google_insights`, etc.)
4. Transform to report data structure (JSON format documented below)
5. Generate PDF and/or PPTX with brand styling

### Data Schema

The single source of truth is
[pinmeto-location-reports/references/data-schema.md](pinmeto-location-reports/references/data-schema.md),
with `test_data.json` as a complete worked example. Do not duplicate the schema here: it drifted
once already and the copies disagreed.

Enforce it mechanically rather than by eye:
```bash
python scripts/validate_report_data.py report_data.json
```

Required top-level keys: `companyName`, `title`, `period`, `dateRange`, `executiveSummary`,
`kpis`, `google`, `facebook`, `apple`, `keywords`, `reviews`, `recommendations`, `appendix`.
Each platform section needs an `insights` array, and each metric needs `name`, `value`,
`periodChange`, `yearChange`.

### Brand Guidelines

| Color | Hex | Usage |
|-------|-----|-------|
| Blue (Primary) | `#3399FF` | Headers, links, primary elements |
| Orange (Accent) | `#FF8854` | Highlights, CTAs |
| Blue Marine | `#001334` | Dark backgrounds, text |
| Light Blue | `#bbd9fa` | Secondary backgrounds |
| Grey | `#F2F3F4` | Light backgrounds |

**Typography**: Montserrat for headlines, Recursive for body text (Arial/Helvetica fallbacks in generators)

**Logos**: Located in `assets/logos/` - use landscape for headers, vertical for cover pages

### MCP Tool Reference

**Targets PinMeTo Location MCP >= 4.0.0** (12 tools). The authoritative contract reference is
`pinmeto-location-reports/references/workflow-details.md`. Verify a connected server with:

```bash
cd pinmeto-location-reports && npm run check-mcp
```

- `pinmeto_get_locations` - List locations (paginated, filterable)
- `pinmeto_get_location` - Single location by `storeId`
- `pinmeto_search_locations` - Resolve a name or partial ID to a `storeId`
- `pinmeto_get_google_insights` - Google impressions and actions
- `pinmeto_get_google_ratings` - Rating aggregates
- `pinmeto_get_google_reviews` - Individual review text
- `pinmeto_get_google_review_insights` - Sentiment and rating statistics
- `pinmeto_get_google_keywords` - Search keyword data
- `pinmeto_get_facebook_insights` - Facebook location metrics
- `pinmeto_get_facebook_brandpage_insights` - Facebook brand-page metrics
- `pinmeto_get_facebook_ratings` - Facebook rating aggregates
- `pinmeto_get_apple_insights` - Apple Maps metrics

Aggregation options: `total`, `daily`, `weekly`, `monthly`, `quarterly`, `half-yearly`, `yearly`
(**hyphen**, not underscore: `half_yearly` fails with `-32602`)
Comparison types: `none`, `prior_period`, `prior_year` (parameter name is `compare_with`)

**Contract gotchas that have bitten this skill before:**
- `storeId` is camelCase. Unknown parameter names are silently stripped, so `store_id` returns
  all-locations data instead of erroring.
- Keywords take `YYYY-MM`; every other tool takes `YYYY-MM-DD`.
- Ratings tools accept no `aggregation` and no `compare_with`.
- The keywords tool has no `limit`; take the top N client-side.
- `insights` is an array keyed by metric name, with flat `priorValue`/`delta`/`deltaPercent`.
- The server does no review theme extraction, despite `analysisType: "themes"` being accepted.

### Testing

```bash
cd pinmeto-location-reports
npm test              # v4 response-shape parser tests (no dependencies)
npm run check-mcp     # tool-surface parity against a connected server
```

`tests/fixtures/` holds v4 payloads generated by running the MCP server's own transform
pipeline over its raw API examples. `tests/evaluations.json` is the skill evaluation spec
(query plus expected behavior per report type), used for manual and harness-driven eval runs.

### Important Considerations

- **Google data lag**: Google metrics have ~10-day reporting delay. Validate end dates accordingly.
- **Chart compatibility**: PPTX generator renders charts as PNG images for cross-platform compatibility (Keynote/PowerPoint)
- **Period detection**: Parse natural language carefully - "Q3 2024" is quarterly, "October 2024" is monthly, "H1 2024" is half-yearly
- **Keyword classification**: Apply rules from `references/keyword-classification.md` (Branded, Discovery, Navigational)
