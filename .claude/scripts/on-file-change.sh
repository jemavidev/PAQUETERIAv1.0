#!/bin/bash
# BetterAgents - File Change Hook
# Runs after Write/Edit/NotebookEdit tool use (PostToolUse hook)
# Tracks meaningful context: file category, change type, recent activity
# Usage: Called automatically by .claude/settings.local.json PostToolUse hook

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"

exec 2>/dev/null

[ -d "$MEMORY_DIR" ] || exit 0
command -v jq &>/dev/null || exit 0
[ -f "$MEMORY_DIR/active-context.json" ] || exit 0

TIMESTAMP=$(date -Iseconds 2>/dev/null || date)
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-${1:-}}"

# Extract changed file path from env or argument
CHANGED_FILE=""
if [ -n "$CLAUDE_TOOL_INPUT" ]; then
    CHANGED_FILE=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // .path // empty' 2>/dev/null || echo "")
fi
if [ -z "$CHANGED_FILE" ]; then
    CHANGED_FILE=$(echo "$TOOL_INPUT" | grep -oE '"(file_path|path)":"[^"]*"' | head -1 | cut -d'"' -f4 2>/dev/null || echo "")
fi

# Skip if we can't identify the file
[ -z "$CHANGED_FILE" ] && exit 0

# If a memory file was written via Write tool, trigger a fast dashboard rebuild
# Exception: skip active-context.json to prevent write loops (it's written by this script)
if [[ "$CHANGED_FILE" == *"/.claude/memory/"* ]] || [[ "$CHANGED_FILE" == *".claude/memory/"* ]]; then
    if [[ "$CHANGED_FILE" != *"active-context.json"* ]] && [[ "$CHANGED_FILE" != *"dashboard.html"* ]]; then
        bash "$SCRIPT_DIR/quick-dashboard.sh" 2>/dev/null &
    fi
    exit 0
fi

# Determine file category from path
categorize_file() {
    local f="$1"
    case "$f" in
        */.claude/agents/*)    echo "agent" ;;
        */.claude/commands/*)  echo "command" ;;
        */.claude/scripts/*)   echo "script" ;;
        */CLAUDE.md)           echo "orchestrator" ;;
        */config/*)            echo "config" ;;
        */docs/*)              echo "documentation" ;;
        */templates/*)         echo "template" ;;
        */scripts/*)           echo "script" ;;
        *.sh)                  echo "script" ;;
        *.md)                  echo "documentation" ;;
        *.json)                echo "config" ;;
        *.py|*.js|*.ts|*.go)   echo "code" ;;
        *)                     echo "other" ;;
    esac
}

CATEGORY=$(categorize_file "$CHANGED_FILE")
BASENAME=$(basename "$CHANGED_FILE")
RELPATH="${CHANGED_FILE#$PROJECT_ROOT/}"

# Set response-changed flag for memory-self-assessment.sh (Stop hook §5b)
# Appends relative path — one line per file changed in this response
echo "$RELPATH" >> "$MEMORY_DIR/.response-changed"

# Build change entry
CHANGE_ENTRY=$(jq -n \
    --arg ts "$TIMESTAMP" \
    --arg file "$RELPATH" \
    --arg name "$BASENAME" \
    --arg cat "$CATEGORY" \
    '{timestamp: $ts, file: $file, name: $name, category: $cat}')

# Update active-context.json:
# - Update lastUpdated
# - Append to recentChanges (max 15 entries)
# - Update currentFocus.feature if it's a significant file (orchestrator/agent)
UPDATED=$(jq \
    --arg ts "$TIMESTAMP" \
    --argjson entry "$CHANGE_ENTRY" \
    --arg cat "$CATEGORY" \
    --arg name "$BASENAME" \
    '
    .lastUpdated = $ts |
    .context.recentChanges = (
        [($entry)] + (.context.recentChanges // [])
        | .[0:15]
    ) |
    if ($cat == "orchestrator" or $cat == "agent") then
        .currentFocus.feature = ("Editing \($cat): \($name)")
    else . end
    ' \
    "$MEMORY_DIR/active-context.json" 2>/dev/null)

if [ -n "$UPDATED" ]; then
    echo "$UPDATED" > "$MEMORY_DIR/active-context.json"
fi

exit 0
