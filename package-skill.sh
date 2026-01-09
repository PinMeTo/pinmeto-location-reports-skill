#!/bin/bash
# Package the PinMeTo Location Reports skill into a .skill file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$SCRIPT_DIR/pinmeto-location-reports"
DIST_DIR="$SCRIPT_DIR/dist"
SKILL_NAME="pinmeto-location-reports"
OUTPUT_FILE="$DIST_DIR/$SKILL_NAME.skill"

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Remove old skill file if it exists
rm -f "$OUTPUT_FILE"

# Change to skill directory
cd "$SKILL_DIR"

# Create the .skill file (zip archive) with only necessary files
# Excludes: node_modules, test files, package files, __pycache__
zip -r "$OUTPUT_FILE" \
    SKILL.md \
    references/ \
    scripts/ \
    assets/ \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*.DS_Store" \
    -x "test_*.json"

echo ""
echo "Skill packaged successfully!"
echo "Output: $OUTPUT_FILE"
echo ""
echo "File size: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
echo ""
echo "Contents:"
unzip -l "$OUTPUT_FILE" | head -20
