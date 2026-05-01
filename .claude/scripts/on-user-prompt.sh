#!/usr/bin/env bash
# AgentX Identity Enforcer — UserPromptSubmit hook
# Only injects reminder for substantive messages (>20 chars)
# Skips trivial responses like "ok", "yes", "thanks", etc.

INPUT=$(cat)
MSG=$(echo "$INPUT" | jq -r '.prompt // ""' 2>/dev/null)

# Fallback: if jq fails or no .prompt field, use raw input
if [ -z "$MSG" ]; then
  MSG="$INPUT"
fi

MSG_LEN=${#MSG}

# Token accumulator — append prompt char count for session-end estimation
# Final input tokens = sum(all MSG_LEN) / 4 + 2386 (fixed overhead: CLAUDE.md + MEMORY.md)
TOKENS_TMP="$(dirname "${BASH_SOURCE[0]}")/../memory/.session-tokens-tmp"
echo "$MSG_LEN" >> "$TOKENS_TMP" 2>/dev/null || true

# Prompt log — store first 200 chars of each substantive prompt for Session Activity
# Strip system-injected XML tags (<ide_opened_file>, <system-reminder>, etc.) first
# Used by track-usage.sh at session end to populate activity.prompts in llm-usage.json
if [ "$MSG_LEN" -ge 20 ]; then
    PROMPTS_TMP="$(dirname "${BASH_SOURCE[0]}")/../memory/.session-prompts-tmp"
    CLEAN_MSG=$(echo "$MSG" | sed 's/<[^>]*>[^<]*<\/[^>]*>//g; s/<[^>]*>//g' | sed 's/^[[:space:]]*//' | tr -s ' ' | tr '\n' ' ')
    CLEAN_LEN=${#CLEAN_MSG}
    if [ "$CLEAN_LEN" -ge 5 ]; then
        echo "$CLEAN_MSG" | head -c 200 | jq -Rc . >> "$PROMPTS_TMP" 2>/dev/null || true
    fi
fi

# ── §5b baseline — save memory count before Claude's response begins ──────────
# memory-self-assessment.sh (Stop hook) compares against this to detect memory writes
_PROMPT_MEMORY_DIR="$(dirname "${BASH_SOURCE[0]}")/../memory"
if command -v jq &>/dev/null && [ -f "$_PROMPT_MEMORY_DIR/progress.json" ]; then
    _TC=$(jq '.tasks | length' "$_PROMPT_MEMORY_DIR/progress.json" 2>/dev/null || echo 0)
    _DC=$(jq '.decisions | length' "$_PROMPT_MEMORY_DIR/decision-log.json" 2>/dev/null || echo 0)
    _CURRENT_MEM=$(( _TC + _DC ))
    echo "$_CURRENT_MEM" > "$_PROMPT_MEMORY_DIR/.last-memory-count"

    # ── Session baseline: saved once at session start ─────────────────────────
    # on-session-stop.sh reads this to detect zero-growth sessions (not just absolute zero)
    _BASELINE_FILE="$_PROMPT_MEMORY_DIR/.session-memory-baseline"
    [ -f "$_BASELINE_FILE" ] || echo "$_CURRENT_MEM" > "$_BASELINE_FILE"

    # ── Session prompt counter ────────────────────────────────────────────────
    _PROMPT_COUNT_FILE="$_PROMPT_MEMORY_DIR/.session-prompt-count"
    _PROMPT_N=$(cat "$_PROMPT_COUNT_FILE" 2>/dev/null || echo 0)
    echo $(( _PROMPT_N + 1 )) > "$_PROMPT_COUNT_FILE"

    # ── Mid-session §5b warning ───────────────────────────────────────────────
    # After 3+ prompts: if project files changed but memory hasn't grown → warn
    if [ $(( _PROMPT_N + 1 )) -ge 3 ]; then
        _BASELINE=$(cat "$_BASELINE_FILE")
        _SCRIPTS_DIR="$(dirname "${BASH_SOURCE[0]}")"
        _GIT_CHANGES=$(cd "$_PROMPT_MEMORY_DIR/../.." && git diff --name-only HEAD 2>/dev/null \
            | grep -v '\.claude/memory/' | grep -v '\.betteragents/memory/' | wc -l || echo 0)
        if [ "$_GIT_CHANGES" -gt 3 ] && [ "$(( _CURRENT_MEM - _BASELINE ))" -le 0 ]; then
            printf "\n⚠️  [§5b MID-SESSION] %d project files changed — no memory entries logged yet this session.\n" "$_GIT_CHANGES"
            printf "→  bash %s/add-task.sh TASK-NN \"<title>\" completed <agent> \"<outcome>\" <priority> \"<tags>\" <min>\n\n" "$_SCRIPTS_DIR"
        fi
    fi
fi

# Memory debt injection — if previous session left unpersisted work
DEBT_FILE="$(dirname "${BASH_SOURCE[0]}")/../memory/.memory-debt.md"
if [ -f "$DEBT_FILE" ]; then
    cat "$DEBT_FILE"
    rm -f "$DEBT_FILE"
fi

# Skip injection for very short/trivial messages (after integrity + memory checks)
if [ "$MSG_LEN" -lt 20 ]; then
  exit 0
fi

echo "🧠 [SYSTEM REMINDER — AgentX Identity Protocol]"
echo "You are AgentX, the orchestrator of BetterAgents."
echo "MANDATORY: Begin your response with the identity header:"
echo '---'
echo '🧠 AgentX/[Mode]'
echo '---'
echo "Where [Mode] is: Dispatcher | Architect | Coder | Critic | Researcher | etc."
echo "Read .claude/memory/MEMORY.md if not yet loaded this session."
echo "Apply the 4-D methodology: Deconstruct → Diagnose → Develop → Dispatch."
