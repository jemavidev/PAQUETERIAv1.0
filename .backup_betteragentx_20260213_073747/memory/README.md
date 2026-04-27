# 💾 Memory System - BetterAgents

The memory system maintains persistent context between work sessions, allowing agents to remember decisions, progress, and project patterns.

---

## 📁 Memory Files

### 1. active-context.md
**Purpose:** Maintain current project context

**When to update:**
- At the start of each session
- When changing main task
- When making important decisions

**What to include:**
- Current task you're working on
- Immediate objective
- Project status
- Next steps

**Usage example:**
```markdown
## Current Task
Implement JWT authentication system

## Objective
Enable secure user login

## Status
- [x] Design phase
- [x] Implementation phase
- [ ] Testing phase
- [ ] Documentation phase
```

---

### 2. progress.md
**Purpose:** Progress and task tracking

**When to update:**
- When completing a task
- When starting a new task
- At the end of each work session

**What to include:**
- Completed tasks with dates
- Tasks in progress
- Pending tasks
- Progress metrics

**Usage example:**
```markdown
## Completed Tasks ✅

### 2026-02-12 - Implement JWT Authentication
- **Agent:** Coder
- **Description:** Complete authentication system with JWT
- **Result:** Login and registration working
- **Files:** auth.py, jwt_utils.py, tests/test_auth.py
```

---

### 3. decision-log.md
**Purpose:** Technical decisions log (ADR)

**When to update:**
- When making any important technical decision
- When choosing between alternatives
- When changing a previous decision

**What to include:**
- Decision context
- What was decided and why
- Alternatives considered
- Expected consequences

**Usage example:**
```markdown
## 2026-02-12 - Decision #001: Use JWT for Authentication

### Context
We need an authentication system for the REST API

### Decision
Implement JWT (JSON Web Tokens) for stateless authentication

### Reasons
1. Scalability - Doesn't require storing sessions on server
2. Portability - Works well with microservices
3. Standard - Widely adopted and supported

### Alternatives Considered
- **Sessions with Redis:** Rejected - Adds dependency and complexity
- **OAuth2:** Rejected - Too complex for our needs

### Consequences
**Positive:**
- Stateless and scalable system
- Easy to implement across multiple services

**Negative:**
- Tokens cannot be revoked before expiration
- Requires implementing refresh tokens

### Agents Involved
- Architect - Solution design
- Security - Security review
- Critic - Trade-off analysis
```

---

### 4. patterns.md
**Purpose:** Document reusable patterns and learnings

**When to update:**
- When identifying a useful pattern
- When solving a problem elegantly
- When learning something new and important

**What to include:**
- Reusable code patterns
- Solutions to common problems
- Project learnings
- Anti-patterns to avoid

**Usage example:**
```markdown
## Pattern #1: Dependency Injection for Testing

**Context:** We need to test code that uses database

**Problem:** Slow and fragile tests due to real DB dependency

**Solution:**
```python
class UserService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_user(self, user_id):
        return self.db.query(User).get(user_id)

# In tests, inject a mock
def test_get_user():
    mock_db = MockDatabase()
    service = UserService(mock_db)
    user = service.get_user(1)
    assert user.id == 1
```

**Advantages:**
- Fast tests (no real DB)
- More testable code
- Easy to mock

**Used in:**
- services/user_service.py
- services/auth_service.py
```

---

## 🔄 Recommended Workflow

### When Starting a Session

1. **Read `active-context.md`**
   - Remember where you left off
   - Review next steps

2. **Update `active-context.md`**
   - Define current task
   - Establish session objective

### During Work

3. **Document decisions in `decision-log.md`**
   - Each important technical decision
   - Include context and reasons

4. **Identify patterns in `patterns.md`**
   - Reusable solutions
   - Important learnings

### When Ending a Session

5. **Update `progress.md`**
   - Mark completed tasks
   - Update tasks in progress
   - Add new pending tasks

6. **Update `active-context.md`**
   - Document current status
   - Define next steps for next session

---

## 💡 Usage Tips

### For Agents

**Architect:**
- Use `decision-log.md` to document design decisions
- Use `patterns.md` for architectural patterns

**Coder:**
- Use `progress.md` for implementation tracking
- Use `patterns.md` for snippets and reusable solutions

**Critic:**
- Review `decision-log.md` to validate decisions
- Identify anti-patterns in `patterns.md`

**Tester:**
- Use `progress.md` for coverage tracking
- Use `patterns.md` for testing patterns

**Writer:**
- Use all files as source for documentation
- Keep documentation synchronized with memory

### For Users

1. **Be consistent:** Update memory regularly
2. **Be concise:** Relevant information, not novels
3. **Be specific:** Technical details matter
4. **Be honest:** Document mistakes and learnings too

---

## 🎯 Memory System Benefits

✅ **Continuity:** Resume work where you left off  
✅ **Context:** Agents understand the complete project  
✅ **Decisions:** Record of why things were done  
✅ **Learning:** Captures project knowledge  
✅ **Collaboration:** All agents share context  
✅ **Documentation:** Base for final documentation  

---

## 📊 Complete Usage Example

### Day 1 - Project Start

**active-context.md:**
```markdown
## Current Project
**Name:** Task Management API
**Stack:** Python, FastAPI, PostgreSQL

## Current Task
Design system architecture

## Objective
Define API structure and database
```

**decision-log.md:**
```markdown
## 2026-02-12 - Decision #001: Use FastAPI
[Complete decision documentation]
```

### Day 2 - Implementation

**active-context.md:**
```markdown
## Current Task
Implement authentication endpoints

## Status
- [x] Design phase
- [x] Implementation phase (50%)
```

**progress.md:**
```markdown
## Completed Tasks ✅
### 2026-02-12 - Architecture design
- Agent: Architect
- Result: Diagram and documented decisions

## Tasks In Progress 🔄
### Implement authentication
- Agent: Coder
- Status: Basic endpoints working
- Next step: Add refresh tokens
```

### Day 3 - Testing

**patterns.md:**
```markdown
## Pattern #1: Endpoint Testing with pytest
[Code and pattern explanation]
```

---

**The memory system is ready to use!**

Start by updating `active-context.md` with your current project.
