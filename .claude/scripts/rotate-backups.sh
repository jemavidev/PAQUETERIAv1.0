#!/usr/bin/env bash
# BetterAgents — rotate-backups.sh
# Automatic backup rotation: keep only latest 3 backups per memory file
# Prevents unbounded accumulation of .bak files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/.claude/memory"

echo "🧹 Rotating memory backups..."
echo "   Keeping latest 3 per file, removing older ones"

# Memory files to rotate
MEMORY_FILES=(
    "progress.json"
    "decision-log.json"
    "patterns.json"
    "active-context.json"
)

ROTATED_COUNT=0

for file in "${MEMORY_FILES[@]}"; do
    FULL_PATH="$MEMORY_DIR/$file"

    if [ ! -f "$FULL_PATH" ]; then
        continue
    fi

    # ── Find all backup files for this file ───────────────────────────────
    # Look for: progress.json.bak, progress.json.bak.1, progress.json.bak.2, etc.
    BACKUPS=$(find "$MEMORY_DIR" -maxdepth 1 -name "${file}.bak*" -type f | sort -V | tac)

    # ── Keep only latest 3, delete the rest ───────────────────────────────
    COUNT=0
    for backup in $BACKUPS; do
        COUNT=$((COUNT + 1))

        if [ "$COUNT" -gt 3 ]; then
            rm -f "$backup"
            echo "   🗑️  Deleted: $(basename $backup)"
            ROTATED_COUNT=$((ROTATED_COUNT + 1))
        fi
    done
done

if [ "$ROTATED_COUNT" -eq 0 ]; then
    echo "   ✅ No old backups to clean (all recent)"
else
    echo "   ✅ Cleaned $ROTATED_COUNT old backup file(s)"
fi

# ── Optional: Print summary ────────────────────────────────────────────────
echo ""
echo "📊 Backup summary:"
for file in "${MEMORY_FILES[@]}"; do
    BAKS=$(find "$MEMORY_DIR" -maxdepth 1 -name "${file}.bak*" -type f | wc -l)
    echo "   • $file: $BAKS backup(s)"
done
