# Tool Selection Guide Skill

**For:** Coder, Architect, DevOps, Researcher agents
**When injected:** Tasks involving search, file operations, or exploration

## Quick Reference Matrix

| Task | Right Tool | Wrong Tool | Why |
|------|-----------|-----------|-----|
| Find files by pattern | **Glob** | `bash find` | Glob is optimized, returns sorted results |
| Search file contents | **Grep** | `bash grep` | Ripgrep engine, faster, regex support |
| Read file | **Read** | `bash cat` | Context-aware, handles large files |
| Modify file | **Edit/Write** | `bash sed` | Tracked by Claude Code, easier to review |
| Run commands | **Bash** | Other tools | Bash is only execution tool |
| Git operations | **Bash** | Other tools | Git requires shell protocol |
| Chain independent searches | **Parallel calls** | Sequential bash | Faster, clearer intent |

## Decision Tree

```
I need to:
  ├─ Find files?
  │   └─ Use Glob(pattern="**/*.ts")
  │       └─ Returns: sorted file list
  │
  ├─ Search file contents?
  │   ├─ Exact match?
  │   │   └─ Use Grep(pattern="exact_string", type="py")
  │   ├─ Regex pattern?
  │   │   └─ Use Grep(pattern="regex.*pattern", type="ts")
  │   └─ Multiple files?
  │       └─ Glob first, then Grep on matches
  │
  ├─ Read a file?
  │   ├─ Specific lines?
  │   │   └─ Use Read(file_path, offset=50, limit=10)
  │   └─ Whole file?
  │       └─ Use Read(file_path)
  │
  ├─ Modify a file?
  │   ├─ Single change?
  │   │   └─ Use Edit(old_string, new_string)
  │   └─ Create new?
  │       └─ Use Write(file_path, content)
  │
  └─ Execute command?
      └─ Use Bash(command="...")
```

## Common patterns

### Pattern 1: "Find all Python files with async"
```
WRONG:
bash -c 'find . -name "*.py" | xargs grep "async def"'

RIGHT:
Glob(pattern="**/*.py")  # Step 1: Find files
Grep(pattern="async def", type="py")  # Step 2: Search in results

Why:
- Glob returns sorted file list
- Grep operates on file paths
- Both are optimized, parallel-friendly
- Clearer intent
```

### Pattern 2: "Search for Router class definition"
```
WRONG:
bash -c 'find . -type f -name "*.ts" | grep -E "class Router"'

RIGHT:
Grep(pattern="class Router", type="ts", head_limit=10)

Why:
- Single tool = single intent
- Grep searches all .ts files automatically
- head_limit prevents overwhelming results
- Return only relevant matches
```

### Pattern 3: "Find imports from a module"
```
WRONG:
bash -c 'grep -r "from ./auth" . | head -20'

RIGHT:
Grep(pattern="from ./auth", glob="**/*.ts", head_limit=5)

Why:
- Grep has glob parameter
- type filtering (ts, py, js) is clearer
- Returns immediately when limit hit
- Consistent behavior
```

### Pattern 4: "Show me a file around line 50"
```
WRONG:
bash -c 'sed -n "45,55p" src/auth.ts'

RIGHT:
Read(file_path="src/auth.ts", offset=45, limit=10)

Why:
- Read is designed for this
- Handles file encoding properly
- Shows line numbers in output
- Integrates with Claude Code features
```

### Pattern 5: "Replace word across files"
```
WRONG:
bash -c 'find . -type f -name "*.ts" -exec sed -i "s/userId/user_id/g" {} \;'

RIGHT:
1. Glob(pattern="**/*.ts")  # Find files
2. For each file: Edit(old_string="userId", new_string="user_id")
3. Verify with: Glob + Grep to confirm changes

Why:
- Edit is tracked by Claude Code
- Each change is reversible
- Can verify after each change
- User sees progress
```

### Pattern 6: "Check if file exists and read it"
```
WRONG:
bash -c 'if [ -f "$file" ]; then cat "$file"; fi'

RIGHT:
Read(file_path=...)  # Returns error if not found, handled gracefully

Why:
- Read handles errors
- Claude Code UI shows results clearly
- No bash conditionals needed
```

## Anti-patterns (NEVER do these)

🚫 **Anti-pattern 1: Chain tools in Bash**
```
WRONG:
bash -c 'find . -name "*.ts" | grep "Router" | head -5'

RIGHT:
Glob(pattern="**/*.ts")
Grep(pattern="Router", type="ts", head_limit=5)
```

🚫 **Anti-pattern 2: Use sed for modifications**
```
WRONG:
bash -c 'sed -i "s/old/new/g" src/file.ts'

RIGHT:
Read(file_path="src/file.ts")
Edit(old_string="old", new_string="new")
```

🚫 **Anti-pattern 3: Guess file paths**
```
WRONG:
Read(file_path="src/handlers/auth")  # What if it's .ts? .js?

RIGHT:
Glob(pattern="src/handlers/auth*")  # Find it first
Read(file_path=results[0])  # Then read
```

🚫 **Anti-pattern 4: Recursive bash operations**
```
WRONG:
bash -c 'for file in $(find . -name "*.ts"); do ...; done'

RIGHT:
Glob(pattern="**/*.ts")  # Get list
# Process in agent logic, not bash loop
```

🚫 **Anti-pattern 5: Combine unrelated operations in Bash**
```
WRONG:
bash -c 'find files && grep patterns && sed replace && run test'

RIGHT:
Glob(...)
Grep(...)
Edit(...)
Bash(command="npm test")  # Only execution in bash
```

## Performance tips

### Speed ranking (fastest → slowest):
1. **Glob** — File discovery (instant)
2. **Grep** — Pattern search (ripgrep engine, very fast)
3. **Read** — File content (fast, with caching)
4. **Edit** — Single change (fast, atomic)
5. **Bash** — Command execution (depends on command)

### Optimization checklist:

- [ ] Use Glob BEFORE Grep (find files, then search)
- [ ] Use type parameter in Grep (filter by extension)
- [ ] Use head_limit in Grep (stop at N results)
- [ ] Use Glob patterns efficiently (narrow search first)
- [ ] Batch independent Glob/Grep calls (parallel)
- [ ] Never pipe in Bash if tool exists
- [ ] Use offset/limit in Read (don't read whole file if you don't need to)

## Example: Good vs Bad code search

### BAD (anti-pattern):
```bash
# 5 operations, sequential, hard to debug
bash -c '
  find . -name "*.ts" -type f | \
  xargs grep "function searchUsers" | \
  cut -d: -f1 | \
  sort | \
  uniq
'
```

### GOOD (tool-selection way):
```
Step 1: Grep(pattern="function searchUsers", type="ts")
  └─ Returns: files with matches

Step 2: Result shows which files contain the function
  └─ Read(file_path=...) to see implementation
```

Why GOOD:
- Single intent per tool
- Results visible immediately
- Easy to refine (narrow search, read specific file)
- Parallel-friendly
- Reviewable

## When Bash is OK

Bash is appropriate for:
- ✅ Git operations: `git log`, `git diff`, `git status`
- ✅ System commands: `npm test`, `pytest`, `docker run`
- ✅ Piping to standard tools: `jq`, `yamllint`, `tsc`
- ✅ File system checks: `ls`, `mkdir` (but Glob preferred for discovery)
- ✅ Environment info: `echo $PATH`, `which python`

Bash is NOT appropriate for:
- ❌ File discovery: Use Glob
- ❌ Content search: Use Grep
- ❌ File reading: Use Read
- ❌ File modification: Use Edit/Write
- ❌ Chaining unrelated operations

## Integration with Anti-Loop Validator

If you find yourself doing:
```
Tool 1: Bash find (❌ should be Glob)
Tool 2: Bash grep (❌ should be Grep)
Tool 3: Bash find again (❌ loop pattern detected!)
```

→ Anti-loop validator catches this:
```
⚠️ Loop detected: "Same search pattern repeated 2x"
Suggestion: Use Glob + Grep together, not bash loops
```

## Real-world examples

### Example 1: Find and fix all typos
```
Task: Fix "dependancies" → "dependencies" in all files

RIGHT:
1. Grep(pattern="dependancies")
2. Shows 3 files with the typo
3. Edit(file1, old_string="dependancies", new_string="dependencies")
4. Edit(file2, ...)
5. Edit(file3, ...)
6. Verify: Grep(pattern="dependancies") → 0 results

Duration: ~10 seconds
```

### Example 2: Update API endpoint
```
Task: Change /api/users → /api/v2/users

RIGHT:
1. Grep(pattern="/api/users", type="ts", glob="src/**/*.ts")
2. Shows 7 matches across 4 files
3. Read each file to understand context
4. Edit each file carefully
5. Verify with Grep to confirm all changed

Duration: ~1 minute (careful, deliberate)
```

### Example 3: Debug type error
```
Task: TS2339 - Property 'userId' not on User type

RIGHT:
1. Grep(pattern="interface User", type="ts")
2. Read User interface definition
3. Grep(pattern="userId", type="ts")
4. See where userId is used
5. Edit User interface or usage
6. Verify: npm test

Duration: ~2 minutes
```

## Checklist before each operation

```
Before I use a tool, am I:
[ ] Using the right tool for this task?
[ ] Avoiding bash pipes/chains?
[ ] Parallel-friendly (can calls run together)?
[ ] Specific about what I'm looking for (pattern, type, limit)?
[ ] Checking results before proceeding?
[ ] Documenting my intent clearly?
```

If ANY answer is NO → Reconsider your approach
