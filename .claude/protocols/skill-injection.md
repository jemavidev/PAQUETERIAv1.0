# Skill Injection Protocol — Reference

Defines how AgentX detects and injects skills into agent prompts on-demand.

## Architecture

```
AgentX dispatching to {agent}:

1. Read config/agent-skills.json["{agent}"].recommended
   → get list of candidate skills for this agent

2. Run detect-skills.sh to filter by task relevance:
   bash .claude/scripts/detect-skills.sh "{task}" {agent}
   → returns 0–3 skill names (max)

3. Load skill content on-demand:
   bash .claude/scripts/detect-skills.sh "{task}" {agent} --content
   → returns formatted skill blocks

4. Inject into Task() prompt
```

## Prompt structure with injection

```
[CONTEXT]
{memory context — ~150 tokens}
[/CONTEXT]

[SKILLS]
--- skill: {skill-name} ---
{skill content}
--- end skill ---
[/SKILLS]

[TASK]
{actual user task}
[/TASK]
```

## Selection rules

- **Max 3 skills** per Task() invocation (avoid context bloat)
- Skills are filtered by keyword relevance to the task
- Fallback: if no keyword match, use top 2 from agent's recommended list
- Skills live in `.claude/commands/{skill-name}.md`
- Agent→skills registry: `config/agent-skills.json`

## Agent skills registry (summary)

| Agent | Primary skills |
|-------|---------------|
| architect | architecture-patterns, api-design-principles, microservices-patterns |
| coder | systematic-debugging, error-handling-patterns, modern-javascript-patterns |
| critic | systematic-debugging, verification-before-completion, requesting-code-review |
| tester | test-driven-development, e2e-testing-patterns, javascript-testing-patterns |
| security | auth-implementation-patterns, code-reviewer |
| ux-designer | frontend-design, ui-ux-pro-max, accessibility-compliance |
| writer | doc-coauthoring, writing-skills, changelog-automation |
| devops | docker-expert, github-actions-templates, deployment-pipeline-design |
| data-scientist | sql-optimization-patterns, prompt-engineering-patterns |
| researcher | brainstorming, find-skills |
| product-manager | brainstorming, kpi-dashboard-design |
| teacher | writing-plans, doc-coauthoring |

## Important: skills are on-demand, not pre-loaded

Skills are NOT embedded in agent definition files. They are read from
`.claude/commands/` only when AgentX decides to inject them.
Each agent sees ONLY the skills relevant to the current task.
