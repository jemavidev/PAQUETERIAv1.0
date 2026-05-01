# Plan Mode Enforcement Protocol

Ensure major changes are reviewed before execution.

## Automatic triggers for EnterPlanMode

```
IF ( files_affected ≥ 3
     OR complexity_score ≥ 5
     OR ambiguity_score ≥ 30
     OR destructive_operation )
THEN EnterPlanMode
```

## Detailed triggers

| Trigger | Condition | Action |
|---------|-----------|--------|
| Multi-file refactor | Files affected ≥ 3 | **MUST** EnterPlanMode |
| Architecture change | Domain redesign | **MUST** EnterPlanMode |
| Database migration | Schema change | **MUST** EnterPlanMode |
| CI/CD pipeline update | GitHub Actions/workflow change | **MUST** EnterPlanMode |
| Package upgrades | Major version bumps (1.x → 2.x) | **MUST** EnterPlanMode |
| Unclear intent | Ambiguity >30% | **MUST** EnterPlanMode |
| Destructive ops | `rm`, `git reset`, `drop table`, etc | **MUST** EnterPlanMode |
| Complex algorithm | New data structure/algorithm | **MUST** EnterPlanMode |

## Complexity scoring (determine auto)

```
Score each criterion (0 or 1):
├─ Files affected ≥ 3: +1
├─ Logic changes (not just refactor): +1
├─ New dependencies added: +1
├─ Database schema change: +1
├─ Breaking changes: +1
├─ Requires coordination (multiple people): +1
└─ User unclear on approach: +1

Total ≥ 3 → Complexity score ≥ 3 (consider EnterPlanMode)
Total ≥ 5 → MANDATORY EnterPlanMode
```

## Plan structure (required by EnterPlanMode)

```markdown
# Implementation Plan: [Task Name]

## Current State
- Problem being solved: [1-2 sentences]
- Affected files: [list]
- Risk level: [Low/Medium/High]

## Proposed State
- Expected outcome: [1-2 sentences]
- New components: [list or "none"]
- Modified files: [list]
- Breaking changes: [none/list]

## Phases (sequential)
### Phase 1: Preparation
- What: [specific action]
- Why: [rationale]
- Rollback if needed: [git reset? data restore?]

### Phase 2: Core Changes
- What: [specific action]
- Why: [rationale]
- Testing: [how to verify]

### Phase 3: Validation
- What: [tests/verification commands]
- Success criteria: [observable outcomes]

## Rollback plan
- If phase 1 fails: `git reset --hard [COMMIT]`
- If phase 2 fails: `git revert [COMMITS]` + restore data
- If phase 3 fails: [specific steps]

## User approvals needed
- [ ] User approves Phase 1
- [ ] User approves Phase 2
- [ ] User approves Phase 3 validation
```

## User interaction flow

```
User → Task(something complex)
  ↓
AgentX detects: complexity ≥ 5
  ↓
"I'm going to modify multiple files. Let me propose a plan first."
EnterPlanMode
  ↓
Show user: Plan template (filled)
  ↓
User: ✅ Approve / 🔄 Modify / ❌ Cancel
  ↓
IF ✅ → proceed with Task() dispatch
IF 🔄 → refine plan interactively
IF ❌ → abort, ask for clarification
```

## Preventing "plan bypass"

Sub-agents MUST NOT:
- ❌ Skip Plan Mode "to save time"
- ❌ Modify 5+ files without mentioning plan
- ❌ Make destructive changes without human approval

Enforcement:
- If Agent writes to 3+ files in sequence → AgentX pauses and asks user
- If destructive operation detected → abort + escalate to user + Critic
