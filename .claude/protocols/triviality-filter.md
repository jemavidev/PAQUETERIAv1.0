# Triviality Filter Protocol

Identify minor changes and suggest manual fixes instead of burning agent tokens.

## Triviality scoring

Calculate a numeric score (0-5 scale) for every proposed change:

```python
def calculate_triviality_score(task):
    score = 0

    # 1. Single file affected?
    if files_affected == 1:
        score += 1

    # 2. Few lines changed (<5)?
    if lines_changed <= 5:
        score += 1

    # 3. No breaking changes?
    if not is_breaking_change:
        score += 1

    # 4. No new dependencies?
    if not adds_dependency:
        score += 1

    # 5. User could do it faster (<2 minutes)?
    if estimated_manual_time_minutes < 2:
        score += 1

    return score  # 0-5
```

## Triviality thresholds

```
Score 5   → TRIVIAL (strongly suggest manual)
Score 4   → TRIVIAL (suggest manual)
Score 3   → BORDERLINE (ask user preference)
Score 2   → COMPLEX (use agent)
Score 0-1 → VERY COMPLEX (use agent + specialist)
```

## Trivial change examples

```
✅ TRIVIAL (Score: 5)
├─ "Fix typo in README: 'dependancies' → 'dependencies'"
├─ "Add missing import statement"
├─ "Update version in package.json"
├─ "Change constant from OLD to NEW"
├─ "Add single comment explaining logic"
└─ "Fix one line: change False → True in config"

❓ BORDERLINE (Score: 3)
├─ "Rename variable across 2 files"
├─ "Add error handling to one function"
├─ "Update config section"
└─ "Add 3-line utility function"

❌ COMPLEX (Score: 1-2)
├─ "Refactor authentication flow"
├─ "Add testing to 10 functions"
├─ "Migrate database schema"
└─ "Implement new feature"
```

## User interaction for trivial tasks

Instead of dispatching agent:

```
💡 This looks like a trivial change!

File: docs/README.md, Line 42
Current: "Instaling BetterAgents"
Suggested: "Installing BetterAgents"

Triviality Score: 5/5
Manual time: <1 minute
Token cost if agent: ~1500
Token cost if manual: ~0

🎯 Recommendation: Fix manually using Find & Replace

Would you like to:
[ ] Fix manually (fastest)
[ ] Let me handle it (convenient)
[ ] Cancel (not needed)
```

## Suggested fix templates

### Typo in file

```
File: {filename}:{line}
Current: "{old_text}"
Suggested: "{new_text}"

Quick fix: Ctrl+H → Find: "{old_text}", Replace: "{new_text}"
```

### Missing import

```
File: {filename}
Add this line at top:
  import { FunctionName } from './module'

Location: After other imports, around line 5
```

### Config value update

```
File: {config_file}
Change:
  {key}: {old_value}
To:
  {key}: {new_value}

Location: Around line {line}
```

### Version bump

```
File: package.json
Find: "version": "{old_version}"
Replace: "version": "{new_version}"

Or use: npm version {major|minor|patch}
```

## Filtering rules (when to suppress agent)

| Type | Condition | Action |
|------|-----------|--------|
| Typo | 1 word misspelled, <10 occurrences | Suggest manual |
| Import | Missing 1 import line | Suggest manual |
| Comment | Add/update comment only | Suggest manual |
| Constant | Change 1 constant value | Suggest manual |
| Version | Update version number | Suggest manual |
| Config | Change 1 config entry | Suggest manual (or use agent if unsure about format) |
| Whitespace | Format/indentation only | Suggest manual |
| Rename var | Rename across <3 files | Suggest manual |

## When NOT to filter (always use agent)

- Logic changes (even if small)
- Changes that could introduce bugs
- Tests or verification code
- Anything touching authentication/security
- Changes requiring human judgment
- Multi-file edits (>1 file, even if trivial)

## Memory tracking

Log triviality suggestions in progress.json:

```json
{
  "id": "TASK-001",
  "title": "Fix README typo",
  "status": "suggested-manual",
  "triviality": {
    "score": 5,
    "reason": "Single file, <5 lines, <1min manual",
    "userDecision": "manual",
    "tokensSaved": 1500
  }
}
```

## Cumulative token savings

Track for each session:

```
Session Summary:
  Tasks processed: 23
  Trivial tasks suggested (score ≥4): 7
  User chose manual: 6
  Tokens saved: 9,000
  Tokens spent: 35,000
  Efficiency: 20% token savings

Top triviality reasons:
  1. Typo fixes (3 tasks, 4,500 tokens saved)
  2. Import additions (2 tasks, 3,000 tokens saved)
  3. Config updates (1 task, 1,500 tokens saved)
```

## Critic gate for borderline cases

If score = 3 (BORDERLINE), show decision to user:

```
Score: 3/5 (Borderline)

This could go either way:
✓ Pros (manual): Quick, no waiting
✓ Pros (agent): Consistent, less error-prone

Choose:
[ ] Manual (I'll do it)
[ ] Agent (please handle it)
[ ] Cancel
```
