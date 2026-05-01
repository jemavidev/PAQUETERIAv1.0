#!/bin/bash
# BetterAgents - Memory JSON Updater
# Updates a specific field in a JSON memory file using jq
# Usage: bash update-memory.sh <file> <jq-filter> [value]
# Example: bash update-memory.sh active-context.json '.project.phase' "development"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <memory-file> <jq-filter> [value]"
    echo "Examples:"
    echo "  $0 active-context.json '.project.phase' \"development\""
    echo "  $0 active-context.json '.currentFocus.feature' \"Auth system\""
    exit 1
fi

FILE="$MEMORY_DIR/$1"
FILTER="$2"
VALUE="${3:-}"

if [ ! -f "$FILE" ]; then
    echo "❌ File not found: $FILE"
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "❌ jq not found. Install with: sudo apt install jq"
    exit 1
fi

# Validate JSON
if ! jq empty "$FILE" 2>/dev/null; then
    echo "❌ Invalid JSON in $FILE"
    exit 1
fi

# Update the field
if [ -n "$VALUE" ]; then
    UPDATED=$(jq --arg v "$VALUE" "${FILTER} = \$v" "$FILE")
else
    UPDATED=$(jq "${FILTER}" "$FILE")
fi

echo "$UPDATED" > "$FILE"
echo "✅ Updated $1: $FILTER"
