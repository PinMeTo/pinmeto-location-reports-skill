# Publishing Guide

## Automated Release Process

This repository uses GitHub Actions to automatically create releases with the packaged `.skill` file attached.

### 1. Update Version

Edit `CHANGELOG.md` to document your changes:

```markdown
## [1.1.0] - 2025-01-16

### Added
- New feature description

### Fixed
- Bug fix description
```

### 2. Commit Changes

```bash
git add .
git commit -m "chore: Prepare release v1.1.0"
git push origin main
```

### 3. Create and Push Tag

```bash
# Create an annotated tag
git tag -a v1.1.0 -m "Release version 1.1.0"

# Push the tag to trigger the release workflow
git push origin v1.1.0
```

### 4. Automatic Workflow

Once you push the tag, GitHub Actions will automatically:
1. Package the skill using `package-skill.sh`
2. Create a GitHub release with release notes
3. Attach the `.skill` file to the release
4. Make it available at the "latest" download URL

## Installation for Users

Users can install the skill directly from GitHub releases:

### Option 1: One-Click Download

Visit the [latest release](https://github.com/PinMeTo/pinmeto-location-analytics-skill/releases/latest) and download `pinmeto-location-reports.skill`, then copy it to `~/.claude/skills/`

### Option 2: Command Line

```bash
curl -L -o pinmeto-location-reports.skill https://github.com/PinMeTo/pinmeto-location-analytics-skill/releases/latest/download/pinmeto-location-reports.skill
mkdir -p ~/.claude/skills
mv pinmeto-location-reports.skill ~/.claude/skills/
```

After installation, restart Claude Desktop to load the skill.

## Manual Testing

If you want to test locally before releasing:

```bash
# Package the skill
./package-skill.sh

# Copy to your local skills directory
cp dist/pinmeto-location-reports.skill ~/.claude/skills/

# Restart Claude Desktop and test
```

## Workflow Summary

```
Development
    ├── Make changes to code
    ├── Test locally (./package-skill.sh)
    ├── Update CHANGELOG.md
    ├── git commit & push
    └── git tag vX.X.X & push tag
         ↓
GitHub Actions (Automated)
    ├── Package skill (.skill file)
    ├── Create GitHub release
    └── Attach .skill file to release
         ↓
Users
    └── Download from GitHub releases
    └── Install in ~/.claude/skills/
```

## Version Management

Follow [Semantic Versioning](https://semver.org/):

- **Major version** (X.0.0): Breaking changes that require user updates
- **Minor version** (0.X.0): New features that are backward compatible
- **Patch version** (0.0.X): Bug fixes and minor improvements

Always update `CHANGELOG.md` with your changes before creating a release tag.
