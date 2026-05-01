---
description: View, search, and manage the BetterAgents memory system. Shows current project context, recent decisions, active patterns, task progress, and memory health stats.
---

# Memory Management Command

This command provides access to the **BetterAgents persistent memory system**.

## Memory Files
All memory is stored in `.claude/memory/`:

| File | Contents |
|------|----------|
| `MEMORY.md` | Auto-loaded summary (always in context) |
| `active-context.json` | Current project state and focus |
| `decision-log.json` | Architecture decisions (ADR format) |
| `progress.json` | Task tracking and completion |
| `patterns.json` | Reusable patterns and learnings |
| `llm-usage.json` | Session and token usage |
| `memory-stats.json` | Memory health stats |
| `project-metrics.json` | Project size metrics |
| `dashboard.html` | Interactive visualization |

## What to Do

When invoked, provide a summary of the current memory state:

1. **Read** `.claude/memory/active-context.json` — Show current focus, recent decisions, open tasks
2. **Read** `.claude/memory/decision-log.json` — Show last 3-5 decisions
3. **Read** `.claude/memory/progress.json` — Show completed and in-progress tasks
4. **Read** `.claude/memory/patterns.json` — Show active patterns
5. **Read** `.claude/memory/MEMORY.md` — Show the summary

## Output Format

```
---
🧠 AgentX/Memory
---

## 📊 Project Context
**Project:** [name]
**Phase:** [phase]
**Focus:** [current focus]

## 📋 Recent Decisions (last 3)
- DEC-XXX: [title] ([date])
- DEC-XXX: [title] ([date])

## ✅ Recent Tasks
- TASK-XXX: [title] — [status]

## 🔄 Active Patterns
- PAT-XXX: [name]

## 📈 Memory Health
- Decisions: [N] entries
- Tasks: [N] total, [N] completed
- Patterns: [N] patterns

## 💡 Actions Available
- "Add a decision to memory: ..."
- "Update the current focus to ..."
- "Mark task TASK-XXX as completed"
- "Open dashboard: bash .claude/scripts/update-dashboard.sh"
```

Read the memory files and present this summary to the user.
