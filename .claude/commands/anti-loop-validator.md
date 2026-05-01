# Anti-Loop Validator Skill

**For:** Coder, Architect, Critic agents
**When injected:** Multi-file changes, ambiguous tasks, debugging scenarios

## Quick self-check (after every 3 tool calls)

Ask yourself these questions — if you answer NO to any, STOP and escalate:

```
[ ] Forward progress? (Did output change meaningfully?)
[ ] Different approach? (Or repeating same action?)
[ ] Goal still clear? (Or drifted since start?)
[ ] Could complete soon? (Or stuck in recursion?)
```

## Loop detection patterns

### Pattern 1: Edit-Test-Edit cycle
```
Tool 1: Read file.ts
Tool 2: Edit file.ts (change A)
Tool 3: Run test → FAIL
Tool 4: Edit file.ts (change B)
Tool 5: Run test → FAIL
Tool 6: Edit file.ts (change C)
↓
🔴 LOOP: Same file edited 3x without success
Action: STOP. Escalate to Critic: "Bug requires deeper analysis"
```

### Pattern 2: Search-Read-Search
```
Tool 1: Grep("UserService", type="ts")
Tool 2: Read(file1.ts)
Tool 3: Grep("UserService") ← same grep again
Tool 4: Read(file2.ts)
Tool 5: Grep("UserService") ← THIRD grep
↓
🔴 LOOP: Same search repeated, expanding but not focusing
Action: STOP. Clarify: "What are we looking for exactly?"
```

### Pattern 3: Refactor-Revert
```
Tool 1: Edit file.ts (refactor logic A)
Tool 2: Run test → FAIL
Tool 3: Edit file.ts (revert logic A, keep structure)
Tool 4: Run test → same FAIL
Tool 5: Edit file.ts (back to original)
↓
🔴 LOOP: Changes made and reverted without understanding root cause
Action: STOP. Route to Critic: "Need systematic debugging"
```

### Pattern 4: Dependency chase
```
Tool 1: Read file.ts (imports B)
Tool 2: Read B.ts (imports C)
Tool 3: Read C.ts (imports D)
Tool 4: Read D.ts (imports E)
Tool 5: Read E.ts ← still chasing dependencies
↓
🔴 LOOP: Lost in dependency tree without clear goal
Action: STOP. Map out: "What are we trying to understand?"
```

## Exit conditions (pick one)

When loop risk is HIGH, you must exit with one of these:

### ✅ COMPLETE
Task achieved. Observable outcome:
- Code compiles/tests pass
- Feature working as expected
- Bug fixed with root cause understood
- Documentation updated and validated

Response format:
```
✅ COMPLETE: [What was accomplished]

Verification:
- [Command run]: [Result]
- [Outcome observed]: [Evidence]
```

### ⚠️ BLOCKED
Technical blocker preventing progress:
- Missing dependency
- Permission issue
- System limitation
- Conflicting requirements

Response format:
```
⚠️ BLOCKED: [What stopped us]

Reason: [Technical limitation]
To unblock: [What human needs to do]
Escalating to: [Critic/User]
```

### ❓ UNCLEAR
Goal ambiguity >30%:
- Multiple interpretations of requirement
- Conflicting constraints
- User intent unclear

Response format:
```
❓ UNCLEAR: [What's ambiguous]

Possible interpretations:
1. [Interpretation A]
2. [Interpretation B]

Clarification needed:
- [Specific question for user]
```

### 🔄 DEFERRED
Task needs human decision or external input:
- Architectural choice
- Product decision
- Business priority
- Human review

Response format:
```
🔄 DEFERRED: [Why human input needed]

Decision point: [What needs to be decided]
Options: [A], [B], [C]
Recommendation: [If applicable]
```

## Implementation checklist

Before every tool call #3, #6, #9, etc., verify:

```
Tool call #3 checkpoint:
  [ ] Am I making progress toward goal? YES / NO
  [ ] Have I changed the same file >1 time? YES / NO
  [ ] Is the goal still clear? YES / NO
  [ ] Can I explain what I'm doing in 1 sentence? YES / NO

  If ANY NO → Review loop patterns above
  If loop detected → STOP and respond with exit condition
```

## Escalation format (when escalating to Critic)

```markdown
⚠️ ESCALATION: Loop Detected

**Agent:** [Your role]
**Task:** [Original task]
**Loop pattern:** [Type from patterns above]
**Attempt count:** [N] tool calls
**Last action:** [What was just tried]

**Symptom:** Repeatedly [action] without achieving [goal]

**Questions for Critic:**
- Should we continue with different approach?
- Is the goal still valid?
- Are we missing something?

**Evidence:** [Show 2-3 tool calls that show the loop]
```

## Token savings via early exit

By catching loops at call #3-6:
- Avoid unnecessary 10+ tool calls
- Prevent context window waste
- Route to appropriate specialist faster
- Show user clear escalation reason

Example:
```
Bad (wasted tokens):
  Loop detected after 12 tool calls → 2000 tokens burned

Good (efficient):
  Loop detected after 5 tool calls → 800 tokens, clear escalation
  Savings: 1200 tokens, faster resolution
```

## Never ignore these signals

🚨 **ALWAYS escalate if:**
- Same file edited 3+ times without test passing
- Same error appearing 2+ times
- Search results expanding (100 → 200 → 500 matches)
- Tool calls increasing but output size decreasing
- User hasn't gotten status update for 5+ tool calls
- You can't explain progress in one sentence
