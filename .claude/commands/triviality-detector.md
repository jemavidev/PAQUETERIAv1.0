# Triviality Detector Skill

**For:** AgentX (Dispatcher), Coder agents
**When injected:** User proposes a change, before dispatching agent

## Scoring algorithm (run this first)

```python
def score_triviality(task_description):
    """Rate how trivial a task is (0-5 scale)"""

    score = 0

    # Criterion 1: Single file?
    if "single file" in context or files_affected == 1:
        score += 1

    # Criterion 2: Few lines?
    if lines_to_change <= 5:
        score += 1

    # Criterion 3: No breaking changes?
    if not "breaking" in task_description.lower():
        if not "delete" in task_description.lower():
            if not "refactor" in task_description.lower():
                score += 1

    # Criterion 4: No new dependencies?
    if "dependency" not in task_description.lower():
        if "import" not in task_description.lower() or "missing import" in task:
            score += 1

    # Criterion 5: Manual would be faster?
    if estimated_manual_seconds < 120:  # <2 minutes
        score += 1

    return score  # 0-5
```

## Decision thresholds

```
Score 5 ─→ 🟢 TRIVIAL (strongly suggest manual)
Score 4 ─→ 🟢 TRIVIAL (suggest manual)
Score 3 ─→ 🟡 BORDERLINE (ask user preference)
Score 2 ─→ 🔵 COMPLEX (use agent)
Score 1 ─→ 🔴 VERY COMPLEX (use specialist agent)
Score 0 ─→ 🔴 ARCHITECTURAL (use architect + critic)
```

## Trivial examples (score 4-5)

✅ **"Fix typo in README: 'dependancies' → 'dependencies'"**
- Files: 1 (README.md)
- Lines: 1
- Breaking: No
- Manual time: 30 seconds
- **Score: 5** → Suggest: "Use Ctrl+H Find & Replace"

✅ **"Add missing import for React"**
- Files: 1 (component.ts)
- Lines: 1 (add import statement)
- Breaking: No
- Dependencies: No (just import)
- Manual time: 45 seconds
- **Score: 4** → Suggest: "Copy import line from example"

✅ **"Update version in package.json from 1.0 to 1.1"**
- Files: 1
- Lines: 1
- Breaking: No
- Manual time: 20 seconds
- **Score: 5** → Suggest: "Edit package.json line 3"

✅ **"Change constant from false to true in config"**
- Files: 1
- Lines: 1
- Breaking: Maybe (depends on constant)
- Manual time: 30 seconds
- **Score: 4 or 3** (borderline)

## Borderline examples (score 3)

❓ **"Rename userId to user_id across the codebase"**
- Files: >3 potentially
- Lines: 5-10
- Breaking: Yes (API changes)
- Manual time: 5-10 minutes
- **Score: 2-3** → "This needs agent + review"

❓ **"Add error handling to login function"**
- Files: 1 (function + possibly tests)
- Lines: 5-10
- Breaking: No (adds safety)
- Manual time: 5 minutes
- **Score: 3** → Ask user: "Manual or agent?"

## Complex examples (score 0-2)

❌ **"Refactor authentication flow"**
- Files: Multiple (auth.ts, routes.ts, middleware.ts)
- Breaking: High risk
- Logic: Complex
- **Score: 0-1** → Use agent + Architect

❌ **"Migrate database schema from MySQL to PostgreSQL"**
- Files: Multiple (schema, migrations, queries)
- Breaking: Yes (full change)
- Risk: High
- **Score: 0** → Use DevOps + Architect + Tester

❌ **"Implement OAuth2 integration"**
- Files: Multiple
- New dependencies: Yes
- Breaking changes: Possible
- Complexity: High
- **Score: 0-1** → Use Security + Architect + Developer

## User interaction for trivial tasks

When score ≥ 4, show this to user:

```
💡 This looks trivial! (Score: 4/5)

Task: Fix typo in README

File: docs/README.md
Current line: "Instaling BetterAgents"
Fix needed: "Installing BetterAgents"

🎯 Options:
  1. Fix manually (fastest)
     └─ Ctrl+H → Find: "Instaling" → Replace: "Installing"
     └─ Time: <1 minute

  2. Let me handle it (convenient)
     └─ I'll fix it for you
     └─ Time: ~30 seconds (including overhead)
     └─ Token cost: ~1,500

💰 Token savings if manual: 1,500 tokens

Your choice:
[ ] Manual (I'll fix it myself)
[ ] Agent (please handle it)
[ ] Cancel (not needed)
```

## User interaction for borderline (score 3)

```
⚖️ This could go either way (Score: 3/5)

Task: Add error handling to login()

Decision:
✓ Manual pros: You know your code best
✓ Agent pros: Consistent, handles edge cases

My recommendation: Use agent (safer)
But your choice:

[ ] Manual
[ ] Agent
[ ] Cancel
```

## Suggested manual solutions (copy-paste ready)

For common trivial tasks, provide ready-to-use solutions:

### Typo in file
```
File: {filename}
Line: {line_number}

Current: {old_text}
Fixed:   {new_text}

Quick fix (no agent needed):
  Ctrl+H (Find & Replace)
  Find:    "{old_text}"
  Replace: "{new_text}"
  Replace all
```

### Missing import
```
File: {filename}
Add this line (around line 5):

import { ComponentName } from './module'

Copy & paste ready. No agent needed.
```

### Config value change
```
File: {config_file} (usually JSON or YAML)
Find this:   {old_value}
Change to:   {new_value}
Location:    Around line {line}

No parsing needed, direct edit. <1 minute.
```

### Add comment
```
File: {filename}
Add comment at line {line}:

// {comment_text}

Or in multi-line:
/*
  {comment_text}
*/

No agent needed, just type it in.
```

## Memory tracking

Log trivial suggestion outcome:

```json
{
  "id": "TASK-001",
  "title": "Fix typo in README",
  "triviality": {
    "score": 5,
    "suggested": "manual",
    "userChoice": "manual",
    "tokensSaved": 1500,
    "estimatedTime": "30s"
  }
}
```

## Cumulative reporting

Track per session:

```
Session Report:
  Total tasks: 15
  Trivial tasks detected: 5 (score ≥4)
  User chose manual: 4
  User chose agent: 1

  Tokens saved: 6,000
  Tokens spent on agent: 8,500
  Net efficiency: ~41% savings on trivial tasks

  Top trivial reasons:
    - Typos (2 tasks, 3,000 tokens saved)
    - Import fixes (2 tasks, 2,500 tokens saved)
    - Config updates (1 task, 500 tokens saved)
```

## Decision tree

```
User proposes task
  ↓
Calculate triviality score
  ↓
  ├─ Score ≥4 (Trivial)
  │   └─ Suggest: "Fix manually using..."
  │       ├─ User: Manual → Show steps
  │       ├─ User: Agent → Proceed, log choice
  │       └─ User: Cancel → Done
  │
  ├─ Score 3 (Borderline)
  │   └─ Ask: "Manual or agent?"
  │       ├─ User: Manual → Show steps
  │       ├─ User: Agent → Proceed
  │       └─ User: Cancel → Done
  │
  └─ Score ≤2 (Complex)
      └─ Proceed with agent dispatch
          ├─ If multi-file → EnterPlanMode
          └─ If architectural → Route to Architect
```

## Never skip detection for

🚨 **ALWAYS run triviality scorer:**
- Any task user describes as simple
- Single-file changes
- Documentation changes
- Configuration changes
- Typo fixes
- Import additions

Never skip and assume complex for:
- Tasks that SOUND complex but are 1 line
- Refactoring with obvious process
- Multi-file changes with repetitive pattern
