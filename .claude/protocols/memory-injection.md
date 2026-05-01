# Memory Injection Protocol — Reference

Read by AgentX when preparing a Task() dispatch. Defines exactly what context
to inject and at what token budget.

## Injection Template

```
[CONTEXT]
Project: {active-context.project.name} | Phase: {active-context.project.phase}
Focus: {active-context.currentFocus.feature}
Stack: {active-context.techStack.languages}, {active-context.techStack.frameworks}
Decisions: {dec.id}: {dec.title} | {dec.id}: {dec.title}
Tasks: {task.id}: {task.title} [{task.status}] | {task.id}: {task.title} [{task.status}]
[/CONTEXT]
```

## Rules

| Field | What to include | Max |
|-------|----------------|-----|
| Project | name + phase only | 1 line |
| Focus | currentFocus.feature (current objective) | 1 line |
| Stack | language + framework names only (no versions) | 1 line |
| Decisions | ID + title only — NO full decision text | 2 entries |
| Tasks | ID + title + status only — NO descriptions | 2 entries |

**Target: ~120–150 tokens total.** Never include full decision or task text in context injection — it bloats the prompt and fragments attention. If the agent needs full detail on a decision, it can request it.

## When to expand context

- **Architecture task:** add `Constraints: {techStack.constraints}` if non-empty
- **Continuation task:** add the most recent task's outcome field if available
- **Debug task:** skip decisions/tasks — add only focus + stack

## Source files

```
active-context.json  → project, phase, focus, stack
decision-log.json    → last 2 entries, fields: id + title only
progress.json        → last 2 entries, fields: id + title + status only
```

## Anti-patterns

- Do NOT inject full decision text (300+ tokens each)
- Do NOT inject full task descriptions
- Do NOT inject patterns.json content (use skill injection instead)
- Do NOT inject more than 2 decisions or 2 tasks — diminishing returns beyond this
