---
description: Force a memory checkpoint — saves all decisions, tasks, and context from the current session. Use during long sessions or before closing to prevent memory loss.
---

# /checkpoint — Memory Checkpoint

This command forces an immediate memory write for everything done in the current session.

## What to Do

Execute ALL of these steps in order. Do not skip any.

### Step 1 — Gather session context
```bash
git log --oneline -5
git diff --name-only HEAD 2>/dev/null || git ls-files --others --exclude-standard 2>/dev/null
jq '.tasks | length' .betteragents/memory/progress.json
jq '.decisions | length' .betteragents/memory/decision-log.json
```

### Step 2 — Score using the Self-Assessment Gate (Protocol §5b)
For everything done this session, score each work unit:
- Any file edited or created: +1
- Structural/architectural choice made: +1
- 2+ files changed: +1
- Bug fixed, request completed, or finding resolved: +1

### Step 3 — Write tasks (one per significant unit of work)
```bash
bash .betteragents/scripts/add-task.sh \
  TASK-NN \
  "<short title>" \
  completed \
  <agent: agentx|coder|architect|critic|...> \
  "<specific outcome: files changed, root cause, approach used>" \
  <priority: high|medium|low> \
  "<tag1,tag2,tag3>" \
  <duration_minutes>
```

### Step 4 — Write decisions (one per architectural/structural choice)
```bash
bash .betteragents/scripts/add-decision.sh \
  DEC-NN \
  "<short title>" \
  "<the problem that forced this decision — NOT the solution>" \
  <agent> \
  implemented \
  "<tag1,tag2>"
```

### Step 5 — Update active context
```bash
bash .betteragents/scripts/update-context.sh \
  --focus "<current feature or area>" \
  --objective "<one-line goal>" \
  --stats-completed N --stats-pending M \
  --add-change "<what changed>" "<main file>" "<feature|bugfix|refactor>" "<description>"
```

### Step 6 — Confirm to user
After all writes, output:

```
💾 Checkpoint saved — [date]
Tasks logged   : N
Decisions      : N
Context updated: yes
Next session will resume from: [focus]
```

## Rules
- Write IMMEDIATELY — do not defer
- IDs are sequential: check existing entries first (`jq '.tasks[-1].id' .betteragents/memory/progress.json`)
- outcome must be specific: files changed, root cause found, approach used — NOT a copy of the title
- If unsure whether to log something → log it. Omission is worse than duplication
- Show `💾 Memory Update: [file] — [description]` for each write
