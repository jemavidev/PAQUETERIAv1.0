#!/bin/bash
# calculate-project-size.sh — Phase 4: Count project files and lines by category
# Writes: .claude/memory/project-size.json
# Called by: on-session-stop.sh (step 2)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"

[ -d "$MEMORY_DIR" ] || exit 0
command -v jq   &>/dev/null || exit 0
command -v find &>/dev/null || exit 0

NOW=$(date -Iseconds)
OUTPUT="$MEMORY_DIR/project-size.json"

# ── Count files per category ──────────────────────────────────────────────────
count_files() { find "$1" -maxdepth 2 -name "$2" -type f 2>/dev/null | wc -l | tr -d ' '; }
count_lines() {
    local total
    total=$(find "$1" -maxdepth 2 -name "$2" -type f 2>/dev/null \
            -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
    echo "${total:-0}"
}

SKILLS_FILES=$(count_files "$PROJECT_ROOT/.claude/commands"   "*.md")
SCRIPTS_SH=$(count_files   "$PROJECT_ROOT/.claude/scripts"    "*.sh")
SCRIPTS_JS=$(count_files   "$PROJECT_ROOT/.claude/scripts"    "*.js")
SCRIPTS_FILES=$(( SCRIPTS_SH + SCRIPTS_JS ))
PROTOCOLS_FILES=$(count_files "$PROJECT_ROOT/.claude/protocols" "*.md")
MEMORY_JSON=$(count_files  "$MEMORY_DIR"                       "*.json")
TEMPLATES_FILES=$(count_files "$PROJECT_ROOT/templates"         "*.html")
CONFIG_FILES=$(count_files "$PROJECT_ROOT/config"              "*.json")

SKILLS_LINES=$(count_lines    "$PROJECT_ROOT/.claude/commands"   "*.md")
SCRIPTS_LINES_SH=$(count_lines "$PROJECT_ROOT/.claude/scripts"   "*.sh")
SCRIPTS_LINES_JS=$(count_lines "$PROJECT_ROOT/.claude/scripts"   "*.js")
SCRIPTS_LINES=$(( SCRIPTS_LINES_SH + SCRIPTS_LINES_JS ))
PROTOCOLS_LINES=$(count_lines "$PROJECT_ROOT/.claude/protocols"  "*.md")
TEMPLATES_LINES=$(count_lines "$PROJECT_ROOT/templates"          "*.html")

# ── Project totals ────────────────────────────────────────────────────────────
TOTAL_FILES=$(find "$PROJECT_ROOT" \
    -not -path "*/.git/*" \
    -not -path "*/node_modules/*" \
    -not -name "*.zip" \
    -type f 2>/dev/null | wc -l | tr -d ' ')

TOTAL_SIZE_KB=$(du -sk "$PROJECT_ROOT" 2>/dev/null | cut -f1)
MEMORY_SIZE_KB=$(du -sk "$MEMORY_DIR" 2>/dev/null | cut -f1)

# ── Write project-size.json ───────────────────────────────────────────────────
TMP=$(mktemp)
if jq -n \
    --arg  now              "$NOW" \
    --argjson total_files   "${TOTAL_FILES:-0}" \
    --argjson total_size    "${TOTAL_SIZE_KB:-0}" \
    --argjson skills        "${SKILLS_FILES:-0}" \
    --argjson skills_lines  "${SKILLS_LINES:-0}" \
    --argjson scripts       "${SCRIPTS_FILES:-0}" \
    --argjson scripts_lines "${SCRIPTS_LINES:-0}" \
    --argjson protocols     "${PROTOCOLS_FILES:-0}" \
    --argjson proto_lines   "${PROTOCOLS_LINES:-0}" \
    --argjson mem_json      "${MEMORY_JSON:-0}" \
    --argjson mem_kb        "${MEMORY_SIZE_KB:-0}" \
    --argjson templates     "${TEMPLATES_FILES:-0}" \
    --argjson tmpl_lines    "${TEMPLATES_LINES:-0}" \
    --argjson config        "${CONFIG_FILES:-0}" \
    '{
        "lastCalculated": $now,
        "totalFiles":     $total_files,
        "totalSizeKB":    $total_size,
        "byCategory": {
            "skills":    { "files": $skills,    "lines": $skills_lines  },
            "scripts":   { "files": $scripts,   "lines": $scripts_lines },
            "protocols": { "files": $protocols, "lines": $proto_lines   },
            "memory":    { "files": $mem_json,  "sizeKB": $mem_kb       },
            "templates": { "files": $templates, "lines": $tmpl_lines    },
            "config":    { "files": $config,    "lines": 0              }
        }
    }' > "$TMP"; then
    mv "$TMP" "$OUTPUT"
    echo "✅ project-size.json: ${TOTAL_FILES} files, ${TOTAL_SIZE_KB}KB total"
else
    rm -f "$TMP"
    echo "❌ Failed to write project-size.json"
    exit 1
fi
