#!/bin/bash
# Auto-verification after file write (Hook)
# Triggered by Claude Code PostToolUse for Write/Edit operations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read file path from Claude Code env (PostToolUse provides CLAUDE_TOOL_INPUT as JSON)
FILE_PATH=$(echo "${CLAUDE_TOOL_INPUT:-}" | jq -r '.file_path // empty' 2>/dev/null)
# Fallback: use first argument if env not set (manual invocation)
if [ -z "$FILE_PATH" ]; then
  FILE_PATH="${1:-}"
fi
OPERATION="${2:-edit}"  # "write" or "edit"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Extract file extension
EXT="${FILE_PATH##*.}"
FILENAME="$(basename "$FILE_PATH")"
DIRNAME="$(dirname "$FILE_PATH")"

# Function to run verification command
verify_file() {
    local file="$1"
    local ext="$2"

    case "$ext" in
        py)
            echo -e "${YELLOW}🔍 Verifying Python file: $FILENAME${NC}"
            python -m py_compile "$file" 2>&1 | head -10
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Python syntax valid${NC}"
                return 0
            else
                echo -e "${RED}❌ Python syntax error${NC}"
                return 1
            fi
            ;;
        ts)
            echo -e "${YELLOW}🔍 Verifying TypeScript file: $FILENAME${NC}"
            if command -v npx &> /dev/null; then
                npx tsc --noEmit "$file" 2>&1 | head -10
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ TypeScript types valid${NC}"
                    return 0
                else
                    echo -e "${RED}❌ TypeScript type error${NC}"
                    return 1
                fi
            else
                echo -e "${YELLOW}⚠️  TypeScript compiler not available, skipping${NC}"
                return 0
            fi
            ;;
        js)
            echo -e "${YELLOW}🔍 Verifying JavaScript file: $FILENAME${NC}"
            if command -v npx &> /dev/null; then
                npx eslint "$file" 2>&1 | head -10
                echo -e "${GREEN}✅ Linting complete (check above for issues)${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠️  ESLint not available${NC}"
                return 0
            fi
            ;;
        json)
            echo -e "${YELLOW}🔍 Verifying JSON file: $FILENAME${NC}"
            if jq . < "$file" > /dev/null 2>&1; then
                echo -e "${GREEN}✅ JSON syntax valid${NC}"
                return 0
            else
                echo -e "${RED}❌ JSON syntax error:${NC}"
                jq . < "$file" 2>&1 | head -5
                return 1
            fi
            ;;
        yaml|yml)
            echo -e "${YELLOW}🔍 Verifying YAML file: $FILENAME${NC}"
            if command -v yamllint &> /dev/null; then
                yamllint "$file" 2>&1 | head -10
                echo -e "${GREEN}✅ YAML validation complete${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠️  yamllint not available${NC}"
                return 0
            fi
            ;;
        sh|bash)
            echo -e "${YELLOW}🔍 Verifying Shell script: $FILENAME${NC}"
            if bash -n "$file" 2>&1; then
                echo -e "${GREEN}✅ Shell syntax valid${NC}"
                return 0
            else
                echo -e "${RED}❌ Shell syntax error${NC}"
                return 1
            fi
            ;;
        md)
            echo -e "${YELLOW}📝 Markdown file (no verification needed)${NC}"
            return 0
            ;;
        *)
            # Unknown type, skip verification
            return 0
            ;;
    esac
}

# Main logic
if [ ! -f "$FILE_PATH" ]; then
    echo -e "${RED}❌ File not found: $FILE_PATH${NC}"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "📦 POST-CHANGE VERIFICATION"
echo "═══════════════════════════════════════════════════════"
echo "File: $FILENAME"
echo "Type: $EXT"
echo "Operation: $OPERATION"
echo ""

# Run verification
verify_file "$FILE_PATH" "$EXT"
VERIFY_RESULT=$?

echo ""
echo "═══════════════════════════════════════════════════════"

if [ $VERIFY_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Verification passed${NC}"
    bash "$SCRIPT_DIR/increment-safety-metric.sh" verificationsPassed 2>/dev/null
else
    echo -e "${RED}❌ Verification failed${NC}"
    echo -e "${YELLOW}💡 Fix the error above and retry${NC}"
    bash "$SCRIPT_DIR/increment-safety-metric.sh" verificationsFailed 2>/dev/null
fi

echo "═══════════════════════════════════════════════════════"
echo ""

exit $VERIFY_RESULT
