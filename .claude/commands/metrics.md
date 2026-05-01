---
description: View token usage, session statistics, and project metrics for the BetterAgents system. Shows LLM usage tracking, project size, and memory stats.
---

# Metrics Command

This command displays **usage statistics and project metrics** for the BetterAgents system.

## What to Do

When invoked, read and present the following metrics:

1. **Read** `.claude/memory/llm-usage.json` — Show session count, total tokens, recent sessions
2. **Read** `.claude/memory/memory-stats.json` — Show memory health stats
3. **Read** `.claude/memory/project-metrics.json` — Show project size metrics

## Output Format

```
---
🧠 AgentX/Metrics
---

## 📊 LLM Usage Stats

### Sessions
- Total sessions: [N]
- Total tokens: [N input] in + [N output] out = [N total]
- Average per session: [N tokens]

### Recent Sessions (last 5)
| Date | Input | Output | Total |
|------|-------|--------|-------|
| [date] | [N] | [N] | [N] |

## 📁 Project Metrics
- Total files: [N]
- Total lines: [N]
- Project size: [N KB]

## 🧠 Memory Stats
- Memory files: [N]
- Decision log: [N entries]
- Progress tracker: [N tasks]
- Patterns: [N patterns]
- Last updated: [timestamp]

## 💡 Dashboard
Open the interactive dashboard:
```bash
bash .claude/scripts/update-dashboard.sh
xdg-open .claude/memory/dashboard.html
```
```

Read the metrics files and calculate/display these statistics. If a file doesn't exist, show "Not available" for that section.
