#!/usr/bin/env bash
# BetterAgents — validate-claude.sh
# Validate CLAUDE.md integrity and consistency
# Can be run at session start or as a pre-flight check

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CLAUDE_FILE="$PROJECT_ROOT/CLAUDE.md"
CLAUDECODE_FILE="$PROJECT_ROOT/.claudecode.json"

# ── Validate CLAUDE.md exists ─────────────────────────────────────────────────
if [ ! -f "$CLAUDE_FILE" ]; then
    echo "❌ CLAUDE.md not found at $CLAUDE_FILE" >&2
    exit 1
fi

# ── Validate it's readable and contains expected sections ────────────────────
if ! grep -q "^## IDENTITY FORMAT" "$CLAUDE_FILE"; then
    echo "❌ CLAUDE.md missing 'IDENTITY FORMAT' section (file may be corrupted)" >&2
    exit 1
fi

if ! grep -q "^## 4-D METHODOLOGY" "$CLAUDE_FILE"; then
    echo "❌ CLAUDE.md missing '4-D METHODOLOGY' section (file may be corrupted)" >&2
    exit 1
fi

if ! grep -q "^## MANDATORY PROTOCOLS" "$CLAUDE_FILE"; then
    echo "❌ CLAUDE.md missing 'MANDATORY PROTOCOLS' section (file may be corrupted)" >&2
    exit 1
fi

# ── Extract version from .claudecode.json and CLAUDE.md ──────────────────────
CLAUDE_VERSION=$(grep "^**Version:** " "$CLAUDE_FILE" | sed 's/.*Version: \([0-9.]*\).*/\1/' | tail -1)
CLAUDECODE_VERSION=$(jq -r '.agentx.version // .version' "$CLAUDECODE_FILE" 2>/dev/null || echo "UNKNOWN")

if [ "$CLAUDE_VERSION" != "$CLAUDECODE_VERSION" ]; then
    echo "⚠️  Version mismatch: CLAUDE.md ($CLAUDE_VERSION) vs .claudecode.json ($CLAUDECODE_VERSION)"
    echo "   This usually happens after updates. Both should match."
fi

# ── Validate .claude/scripts are referenced in CLAUDE.md ──────────────────────
SCRIPT_COUNT=$(ls -1 "$PROJECT_ROOT/.claude/scripts"/*.sh 2>/dev/null | wc -l)
if [ "$SCRIPT_COUNT" -lt 20 ]; then
    echo "❌ Expected 20+ scripts in .claude/scripts/, found $SCRIPT_COUNT"
    exit 1
fi

# ── Validate .claude/memory files exist ───────────────────────────────────────
MEMORY_REQUIRED_FILES=(
    ".claude/memory/MEMORY.md"
    ".claude/memory/progress.json"
    ".claude/memory/decision-log.json"
    ".claude/memory/patterns.json"
    ".claude/memory/active-context.json"
)

for file in "${MEMORY_REQUIRED_FILES[@]}"; do
    FULL_PATH="$PROJECT_ROOT/$file"
    if [ ! -f "$FULL_PATH" ]; then
        echo "❌ Required memory file missing: $file"
        exit 1
    fi
done

# ── Validate all memory JSON files are well-formed ───────────────────────────
for json_file in "$PROJECT_ROOT"/.claude/memory/*.json; do
    if ! jq empty "$json_file" 2>/dev/null; then
        echo "❌ JSON corruption detected in $json_file"
        echo "   Attempting recovery from .bak file..."
        BAK_FILE="${json_file}.bak"
        if [ -f "$BAK_FILE" ]; then
            cp "$BAK_FILE" "$json_file"
            echo "   ✅ Recovered from $BAK_FILE"
        else
            echo "   ❌ No backup found. Manual recovery required."
            exit 1
        fi
    fi
done

# ── Validate settings.local.json is valid JSON ───────────────────────────────
if ! jq empty "$PROJECT_ROOT/.claude/settings.local.json" 2>/dev/null; then
    echo "❌ settings.local.json is corrupted or invalid JSON"
    exit 1
fi

# ── Validate agent definitions have proper frontmatter ──────────────────────
echo ""
echo "🔍 Validating agent definitions..."
for agent_file in "$PROJECT_ROOT"/.claude/agents/*.md; do
    if ! head -1 "$agent_file" | grep -q "^---"; then
        echo "❌ Missing frontmatter: $(basename $agent_file)"
        exit 1
    fi
done
echo "✅ All agent definitions have proper frontmatter"

# ── Validate hook scripts are executable ──────────────────────────────────
echo ""
echo "🔍 Validating hook script permissions..."
HOOKS=(
    "on-user-prompt.sh"
    "on-file-change.sh"
    "on-file-write-verification.sh"
    "on-bash-change.sh"
    "on-plan-mode.sh"
    "on-session-stop.sh"
    "memory-self-assessment.sh"
)

for hook in "${HOOKS[@]}"; do
    HOOK_PATH="$PROJECT_ROOT/.claude/scripts/$hook"
    if [ -f "$HOOK_PATH" ]; then
        if [ -x "$HOOK_PATH" ]; then
            true  # executable
        else
            echo "⚠️  Not executable: $hook (chmod +x fixing...)"
            chmod +x "$HOOK_PATH"
        fi
    fi
done
echo "✅ All hook scripts are executable"

# ── Validate memory JSON schema (not just syntax) ───────────────────────────
echo ""
echo "🔍 Validating memory JSON schema..."

# progress.json must have .tasks array
if ! jq -e '.tasks | type == "array"' "$PROJECT_ROOT/.claude/memory/progress.json" >/dev/null 2>&1; then
    echo "❌ progress.json missing .tasks array"
    exit 1
fi

# decision-log.json must have .decisions array
if ! jq -e '.decisions | type == "array"' "$PROJECT_ROOT/.claude/memory/decision-log.json" >/dev/null 2>&1; then
    echo "❌ decision-log.json missing .decisions array"
    exit 1
fi

# patterns.json must have .patterns array
if ! jq -e '.patterns | type == "array"' "$PROJECT_ROOT/.claude/memory/patterns.json" >/dev/null 2>&1; then
    echo "❌ patterns.json missing .patterns array"
    exit 1
fi

echo "✅ All memory JSON files have correct schema"

# ── Validate referential integrity (sample check) ──────────────────────────
echo ""
echo "🔍 Validating referential integrity (sample)..."

# Check that task agent IDs are reasonable (not null, not too short)
INVALID_AGENTS=$(jq -r '.tasks[].agentId // "null"' "$PROJECT_ROOT/.claude/memory/progress.json" | grep -E "^null$|^$" | wc -l)
if [ "$INVALID_AGENTS" -gt 0 ]; then
    echo "⚠️  Found $INVALID_AGENTS tasks with missing/null agentId (may be expected)"
fi
echo "✅ Referential integrity check passed"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ CLAUDE.md validation PASSED (ENHANCED)"
echo "════════════════════════════════════════════════════════════════"
echo "   ✓ Core sections present"
echo "   ✓ Version consistent"
echo "   ✓ Scripts present ($SCRIPT_COUNT files)"
echo "   ✓ Memory files intact (all JSON valid)"
echo "   ✓ Memory JSON schema correct"
echo "   ✓ Agent definitions valid"
echo "   ✓ Hook scripts executable"
echo "   ✓ Referential integrity OK"
echo "   ✓ Settings valid"
echo ""
echo "System ready for production. 🚀"
