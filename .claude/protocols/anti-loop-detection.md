# Anti-Loop Detection Protocol

Detect and prevent recursive patterns that waste tokens and confuse progress.

## When triggered

After **every 3 consecutive tool calls** from a single agent:
- Did output change meaningfully? (LOC, token contribution)
- Are we modifying the same file repeatedly?
- Has the goal shifted since dispatch?

## Safeguard checklist

```
[ ] Tool call #3: Pause and validate
  ├─ Am I closer to solution? (Yes/No)
  ├─ Is this the right approach? (Yes/No)
  ├─ Have I changed the same file 2x+ without result? (Yes → escalate)
  ├─ Can I explain progress in one sentence? (Yes → continue, No → stop)
  └─ Should user clarify intent? (Yes → ask)

[ ] If loop detected:
  ├─ Stop execution immediately
  ├─ Show: ⚠️ Loop detected after [N] calls
  ├─ Explain: "Repeatedly [action] without [result]"
  └─ Escalate to Critic + User

[ ] Exit conditions (mutually exclusive):
  ├─ COMPLETE: Observable outcome achieved ✅
  ├─ BLOCKED: Technical blocker (escalate)
  ├─ UNCLEAR: Intent ambiguity >30% (ask user)
  └─ DEFERRED: Task requires human decision
```

## Implementation for sub-agents

When dispatching Task() to Coder, Architect, etc., inject:

```markdown
[LOOP-GUARD]
After every 3 tool calls, pause and ask yourself:
1. Have I made forward progress?
2. Am I repeating the same action?
3. Should I escalate instead of continuing?

If LOOP DETECTED → return: "⚠️ LOOP: [explain]"
[/LOOP-GUARD]
```

## Memory tracking

In progress.json, log tool call count:
```json
{
  "id": "TASK-001",
  "title": "Fix authentication",
  "status": "in_progress",
  "toolCalls": 5,
  "lastToolCall": "Edit",
  "loopRisk": "yellow"  // "green" | "yellow" | "red"
}
```

Thresholds:
- **Green:** 1-3 tool calls, forward progress
- **Yellow:** 4-6 tool calls, same file being edited
- **Red:** 7+ tool calls OR same error 2x+ → escalate

## Common loop patterns to watch for

| Pattern | Symptom | Action |
|---------|---------|--------|
| Edit-Test-Edit-Test cycle | Same file edited 3x | Stop after #2, ask user |
| Search-Read-Search loop | Same grep 2x, different files | Narrow search, adjust goal |
| Refactor-Revert cycle | Code changed then reverted | Clarify intent with user |
| Debugging infinite loop | Same error appearing | Escalate to Critic |

## Critic escalation template

When loop detected, provide Critic with:

```
⚠️ LOOP DETECTED

Agent: [name]
Task: [original task]
Loop type: [pattern name]
Tool calls: [count]
Last action: [what was attempted]
Symptom: [repeating X without achieving Y]

User input needed:
- Should we continue? (Yes/No/Different approach)
- Is the goal still clear?
- Any constraints we're missing?
```
