# Plan Mode Enforcer Skill

**For:** Architect, Coder agents
**When injected:** Complex tasks, multi-file changes, unclear requirements

## When to trigger Plan Mode

Before you start making changes, evaluate:

```
Does this task match ANY of these criteria?

□ Affects 3+ files
□ Changes architecture or structure
□ Involves database schema changes
□ Requires new dependencies
□ Not immediately obvious how to proceed
□ Breaking changes possible
□ Affects multiple systems/layers
□ User seems uncertain about approach

If ANY checked → STOP and propose plan
```

## Plan proposal template

If Plan Mode needed, show user this:

```markdown
# Implementation Plan: [Task Name]

## Summary
[1-2 sentences of what we're doing]

## Files that will change
- [ ] src/auth.ts — [What changes]
- [ ] src/types.ts — [What changes]
- [ ] tests/auth.test.ts — [What changes]

## Approach
### Phase 1: Setup
- Step 1: [What] — Why: [Why]
- Step 2: [What] — Why: [Why]

### Phase 2: Core changes
- Step 3: [What] — Why: [Why]
- Step 4: [What] — Why: [Why]

### Phase 3: Validation
- Tests to run: [Command]
- Expected result: [Observable outcome]

## Rollback strategy
If something breaks: `git reset --hard [current-commit]`

## Questions for you:
- Does this approach make sense?
- Any changes needed?
- Any constraints I'm missing?

Ready to proceed? [YES / REVISE / CANCEL]
```

## Complexity scoring

Calculate a score to decide if plan is needed:

```
Points for each:
+1 Files affected ≥ 3
+1 Requires new imports/dependencies
+1 Changes function signatures
+1 Database or schema change
+1 Could break existing code
+1 User expressed uncertainty
+1 Architectural decision involved
+1 Destructive operation (delete, reset, etc)
+1 Involves multiple layers (DB + API + UI)

Score ≥ 3 → Propose plan first
Score ≥ 5 → MUST propose plan, wait for approval
```

## Don't skip planning for:

🚫 **Never skip, always plan:**
- Database migrations
- Authentication flow changes
- Dependency upgrades (major version)
- API endpoint changes
- Anything touching 5+ files

✅ **Can skip planning for:**
- Single function implementation
- Bug fixes (if approach is obvious)
- Documentation updates
- Comments or formatting
- Single-file enhancements

## Detailed plan guidelines

### Phase 1: Preparation
What you do first (non-breaking):
- Exploratory reads
- Create new files
- Add imports
- Refactor to prepare (no breaking changes)

### Phase 2: Core Implementation
The main changes:
- Modify function signatures
- Update logic
- Change structure
- Implement new behavior

### Phase 3: Validation
Testing and verification:
- Run tests: `npm test` or `pytest`
- Type checking: `tsc` or mypy
- Linting: eslint or pylint
- Integration: user manual verification

## Dealing with user feedback

### User says: "Yes, proceed"
→ Execute phases in order
→ Show progress after each phase
→ Ask for approval before phase 2 if major change

### User says: "Revise plan"
→ Show which part needs change
→ Ask specific questions
→ Wait for updated direction

### User says: "Cancel"
→ Acknowledge
→ Ask: different approach? or skip task?

## Common plan mistakes (avoid these)

❌ **Mistake 1:** Plan too vague
```
BAD:  "Phase 1: Update files"
GOOD: "Phase 1: Modify src/auth.ts lines 10-50 to add error handling"
```

❌ **Mistake 2:** Plan too detailed
```
BAD:  "Step 1a: Read file. Step 1b: Find line. Step 1c: Change char..."
GOOD: "Step 1: Update authentication error message"
```

❌ **Mistake 3:** No rollback strategy
```
BAD:  "If fails, we figure it out"
GOOD: "If fails: git reset --hard HEAD~1"
```

❌ **Mistake 4:** No validation step
```
BAD:  Plan ends at implementation
GOOD: Plan includes "Run: npm test && npm run lint"
```

## Approval checklist

Before user approves, make sure plan has:

```
[ ] Clear summary (1-2 sentences)
[ ] List of files that will change
[ ] 3 sequential phases
[ ] Specific commands for testing
[ ] Rollback plan (git reset or equivalent)
[ ] Risk assessment (Low/Medium/High)
```

## Time estimates (optional but helpful)

You can estimate if it helps user decide:

```
Estimated time per phase:
- Phase 1: 2 minutes
- Phase 2: 5 minutes
- Phase 3: 3 minutes
Total: ~10 minutes

(These are rough, for user expectation setting)
```

## Sample good plans

### Example 1: Add feature
```
# Plan: Add user authentication logout

Files: src/auth.ts, src/routes.ts, tests/auth.test.ts

Phase 1: Add logout function to auth.ts
- Add async logout(userId) function
- Return success/failure

Phase 2: Add route handler
- Add POST /api/logout endpoint
- Call auth.logout()

Phase 3: Test
- Run: pytest tests/test_auth.py
- Verify: POST /api/logout returns 200

Rollback: git reset --hard HEAD~1
```

### Example 2: Refactor
```
# Plan: Extract common validation logic

Files: src/handlers/users.ts, src/handlers/posts.ts, src/validation.ts

Phase 1: Create validation module
- Create src/validation.ts with common functions
- Add exports for: validateEmail, validateLength, etc

Phase 2: Update handlers
- users.ts: Replace inline validation with imported functions
- posts.ts: Replace inline validation with imported functions

Phase 3: Test
- Run: npm test
- Check coverage: npm run coverage

Rollback: git reset --hard HEAD~1
```
