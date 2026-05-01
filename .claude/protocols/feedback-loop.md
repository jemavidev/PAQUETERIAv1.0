# Feedback Loop Protocol — Reference

Applied by AgentX after every agent returns a result, before integrating output.

## Quality Gate Checklist

```
[ ] Output addresses the actual task requirement?
[ ] Consistent with decisions in decision-log.json?
[ ] No contradictions with active patterns?
[ ] If architecture → Critic reviewed it? (mandatory)
[ ] If security-sensitive → Security agent reviewed it?
[ ] Output is complete (not truncated or partial)?
```

## Actions by condition

| Condition | Action |
|-----------|--------|
| Complete + consistent | Integrate → update memory |
| Contradicts prior decision | Flag to user + route to Critic |
| Incomplete output | Re-route same agent with gap specification |
| Architecture without Critic | Auto-route to Critic before integrating |
| Security issue found | Route to Security agent |

## Critic Gate (mandatory for architecture)

```
Phase N:   Task(subagent_type="architect", ...)  → design output
Phase N+1: Task(subagent_type="critic", prompt="Review: {output}")
Phase N+2: Integrate both → update decision-log.json
```

## Memory write triggers

After feedback loop completes on significant work:
- Architecture decision → `decision-log.json`
- Task completed → `progress.json`
- New pattern found → `patterns.json`
