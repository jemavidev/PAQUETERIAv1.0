#!/bin/bash
# BetterAgents Memory Dashboard Builder
# Reads JSON memory files and generates standalone HTML dashboard with embedded data
# Usage: bash update-dashboard.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Paths
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"
TEMPLATE="$PROJECT_ROOT/templates/memory/dashboard.html"
OUTPUT="$MEMORY_DIR/dashboard.html"
TEMP_OUTPUT="${OUTPUT}.tmp"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Building Memory Dashboard...${NC}"

# Check if template exists
if [ ! -f "$TEMPLATE" ]; then
    echo "❌ Template not found: $TEMPLATE"
    echo "   Using existing dashboard.html as-is"
    exit 0
fi

# Check memory files exist
for file in decision-log.json patterns.json progress.json active-context.json; do
    if [ ! -f "$MEMORY_DIR/$file" ]; then
        echo "❌ Memory file not found: $MEMORY_DIR/$file"
        exit 1
    fi
done

# Read JSON files
DECISIONS=$(jq -c '.decisions' "$MEMORY_DIR/decision-log.json")
PATTERNS=$(jq -c '.patterns' "$MEMORY_DIR/patterns.json")
PROGRESS=$(jq -c '.tasks' "$MEMORY_DIR/progress.json")
CONTEXT=$(jq -c '.' "$MEMORY_DIR/active-context.json")
STATS=$(jq -c '.' "$MEMORY_DIR/memory-stats.json" 2>/dev/null || echo 'null')
METRICS=$(jq -c '.' "$MEMORY_DIR/project-metrics.json" 2>/dev/null || echo 'null')

# Get timestamps
TIMESTAMP=$(date -Iseconds)
READABLE_TIME=$(date "+%Y-%m-%d %H:%M:%S")

# Create new memoryData block
MEMORY_DATA_BLOCK="        let memoryData = {
            decisions: ${DECISIONS},
            tasks: ${PROGRESS},
            patterns: ${PATTERNS},
            context: ${CONTEXT},
            stats: ${STATS},
            metrics: ${METRICS},
            audit: null,
            lastUpdate: \"${TIMESTAMP}\",
            lastUpdateReadable: \"${READABLE_TIME}\"
        };"

# Process template replacing memoryData block
IN_MEMORY_BLOCK=false
BRACE_COUNT=0

while IFS= read -r line; do
    if [[ "$line" =~ "let memoryData = {" ]]; then
        IN_MEMORY_BLOCK=true
        BRACE_COUNT=1
        echo "$MEMORY_DATA_BLOCK"
        continue
    fi

    if [ "$IN_MEMORY_BLOCK" = true ]; then
        OPEN_BRACES=$(echo "$line" | grep -o "{" | wc -l)
        BRACE_COUNT=$((BRACE_COUNT + OPEN_BRACES))
        CLOSE_BRACES=$(echo "$line" | grep -o "}" | wc -l)
        BRACE_COUNT=$((BRACE_COUNT - CLOSE_BRACES))
        if [ $BRACE_COUNT -le 0 ] && [[ "$line" =~ ";" ]]; then
            IN_MEMORY_BLOCK=false
        fi
        continue
    fi

    echo "$line"
done < "$TEMPLATE" > "$TEMP_OUTPUT"

# Move to final location
mv "$TEMP_OUTPUT" "$OUTPUT"

echo -e "${GREEN}✅ Dashboard updated!${NC}"
echo -e "   📁 Output: $OUTPUT"
echo -e "   🕐 Updated: $READABLE_TIME"
echo -e "   📊 Decisions: $(echo "$DECISIONS" | jq 'length'), Tasks: $(echo "$PROGRESS" | jq 'length'), Patterns: $(echo "$PATTERNS" | jq 'length')"
echo -e ""
echo -e "${BLUE}🌐 Open:${NC} xdg-open $OUTPUT"
