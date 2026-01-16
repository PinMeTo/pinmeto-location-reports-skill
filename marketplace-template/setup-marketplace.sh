#!/bin/bash

# Setup script for PinMeTo Skills Marketplace
# Run this in your cloned PinMeTo/skills repository

set -e

echo "🚀 Setting up PinMeTo Skills Marketplace..."

# Create directory structure
echo "Creating directory structure..."
mkdir -p skills
mkdir -p docs

# Copy marketplace configuration
echo "Creating marketplace.json..."
# (You'll need to copy marketplace.json here manually)

# Create README
echo "Creating README.md..."
# (You'll need to copy README.md here manually)

# Create .gitignore
cat > .gitignore << 'EOF'
.DS_Store
*.log
.vscode/
.idea/
EOF

# Create CONTRIBUTING.md
cat > CONTRIBUTING.md << 'EOF'
# Contributing to PinMeTo Skills

## Adding a New Skill

1. Develop your skill in its own repository (e.g., `PinMeTo/my-skill`)
2. Package the skill using `./package-skill.sh`
3. Fork this repository
4. Add your packaged `.skill` file to the `skills/` directory
5. Update `marketplace.json` with your skill's metadata
6. Update `README.md` with your skill's description
7. Submit a pull request

## Skill Requirements

- Must follow Claude Code skill format
- Must include comprehensive documentation
- Must include example usage
- Must specify all required dependencies
- Must include proper error handling

## Version Management

Skills should follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

## Testing

Before submitting:
1. Test the skill locally
2. Verify all documentation
3. Check that dependencies are listed
4. Ensure example code works
EOF

# Create initial commit message template
cat > .gitmessage << 'EOF'
# Skill update format:
# [skill-name] Brief description
#
# - Change 1
# - Change 2
#
# Version: X.X.X
EOF

git config commit.template .gitmessage

echo "✅ Marketplace setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy marketplace.json from marketplace-template/"
echo "2. Copy README.md from marketplace-template/"
echo "3. Add your first skill to skills/ directory"
echo "4. Commit and push to GitHub"
echo ""
echo "Then users can install with:"
echo "  claude /plugin install https://github.com/PinMeTo/skills"
