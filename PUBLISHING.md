# Publishing Guide

## Repository Setup

### 1. Push to GitHub

```bash
# After creating the repo on GitHub
git push -u origin main
```

### 2. Tag Releases

```bash
# When you make updates
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Publishing to Marketplace

### 1. Build the Skill Package

```bash
./package-skill.sh
```

This creates `dist/pinmeto-location-reports.skill`

### 2. Copy to Skills Marketplace

```bash
# Clone the marketplace repo (one-time setup)
cd ~/Projects/code
git clone git@github.com:PinMeTo/skills.git
cd skills

# Copy the packaged skill
cp ~/Projects/code/pinmeto-location-reports-skill/dist/pinmeto-location-reports.skill ./skills/

# Commit and push
git add skills/pinmeto-location-reports.skill
git commit -m "Update pinmeto-location-reports skill to v1.0.0"
git push
```

### 3. Update Marketplace Catalog

Edit the `marketplace.json` and `README.md` in the skills repo to include this skill.

## Installation for Users

Users can install from the marketplace:

```bash
# Using Claude Code
claude /plugin install https://github.com/PinMeTo/skills
```

Or manually copy the `.skill` file:

```bash
cp skills/pinmeto-location-reports.skill ~/.claude/skills/
```

## Workflow Summary

```
Development Repo (pinmeto-location-reports-skill)
    ├── Make changes
    ├── Test locally
    ├── ./package-skill.sh
    ├── git commit & push
    └── git tag vX.X.X
         ↓
Marketplace Repo (skills)
    ├── Copy .skill file
    ├── Update marketplace.json
    └── git push
         ↓
Users
    └── claude /plugin install
```

## Version Management

1. **Development**: Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
2. **Changelog**: Document changes in CHANGELOG.md
3. **Breaking Changes**: Bump major version
4. **New Features**: Bump minor version
5. **Bug Fixes**: Bump patch version

## Testing Before Publishing

```bash
# Test locally before publishing
cp dist/pinmeto-location-reports.skill ~/.claude/skills/
# Then test in Claude Code
```
