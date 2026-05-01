#!/bin/bash
# BetterAgents - Memory Health Audit
# Checks all memory files for integrity and reports issues
# Usage: bash audit-memory.sh [--fix]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

FIX_MODE="${1:-}"
ISSUES=0
WARNINGS=0

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 BetterAgents Memory Audit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -d "$MEMORY_DIR" ]; then
    echo -e "${RED}❌ Memory directory not found: $MEMORY_DIR${NC}"
    exit 1
fi

# Check required files
REQUIRED_FILES=(
    "active-context.json"
    "decision-log.json"
    "progress.json"
    "patterns.json"
    "llm-usage.json"
    "memory-stats.json"
    "MEMORY.md"
)

echo "📁 Checking required files..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$MEMORY_DIR/$file" ]; then
        SIZE=$(wc -c < "$MEMORY_DIR/$file" 2>/dev/null || echo "0")
        echo -e "  ${GREEN}✅ $file${NC} (${SIZE} bytes)"
    else
        echo -e "  ${RED}❌ $file — MISSING${NC}"
        ISSUES=$((ISSUES + 1))
    fi
done

echo ""
echo "🔍 Validating JSON integrity..."

for file in "$MEMORY_DIR"/*.json; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")

    if command -v jq &>/dev/null; then
        if jq empty "$file" 2>/dev/null; then
            ENTRIES=$(jq 'if type == "object" then (to_entries | length) elif type == "array" then length else 1 end' "$file" 2>/dev/null || echo "?")
            echo -e "  ${GREEN}✅ $filename${NC} — valid JSON ($ENTRIES top-level keys/items)"
        else
            echo -e "  ${RED}❌ $filename — INVALID JSON${NC}"
            ISSUES=$((ISSUES + 1))
        fi
    fi
done

echo ""
echo "📊 Memory statistics..."

if [ -f "$MEMORY_DIR/decision-log.json" ] && command -v jq &>/dev/null; then
    DECISIONS=$(jq '.decisions | length' "$MEMORY_DIR/decision-log.json" 2>/dev/null || echo "?")
    echo "  Decisions: $DECISIONS entries"
fi

if [ -f "$MEMORY_DIR/progress.json" ] && command -v jq &>/dev/null; then
    TASKS=$(jq '.tasks | length' "$MEMORY_DIR/progress.json" 2>/dev/null || echo "?")
    COMPLETED=$(jq '[.tasks[] | select(.status == "completed")] | length' "$MEMORY_DIR/progress.json" 2>/dev/null || echo "?")
    echo "  Tasks: $TASKS total, $COMPLETED completed"
fi

if [ -f "$MEMORY_DIR/patterns.json" ] && command -v jq &>/dev/null; then
    PATTERNS=$(jq '.patterns | length' "$MEMORY_DIR/patterns.json" 2>/dev/null || echo "?")
    echo "  Patterns: $PATTERNS entries"
fi

if [ -f "$MEMORY_DIR/llm-usage.json" ] && command -v jq &>/dev/null; then
    SESSIONS=$(jq '.sessions | length' "$MEMORY_DIR/llm-usage.json" 2>/dev/null || echo "?")
    TOTAL=$(jq '.totals.total // 0' "$MEMORY_DIR/llm-usage.json" 2>/dev/null || echo "?")
    echo "  Sessions tracked: $SESSIONS (Total tokens: $TOTAL)"
fi

echo ""
echo "📄 MEMORY.md check..."
if [ -f "$MEMORY_DIR/MEMORY.md" ]; then
    LINES=$(wc -l < "$MEMORY_DIR/MEMORY.md")
    if [ "$LINES" -gt 200 ]; then
        echo -e "  ${YELLOW}⚠️  MEMORY.md has $LINES lines (should be <200)${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "  ${GREEN}✅ MEMORY.md — $LINES lines (within 200-line limit)${NC}"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ISSUES -gt 0 ]; then
    echo -e "${RED}❌ Audit failed: $ISSUES issue(s), $WARNINGS warning(s)${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Audit passed with $WARNINGS warning(s)${NC}"
else
    echo -e "${GREEN}✅ Memory audit passed — all files healthy${NC}"
fi
echo ""
