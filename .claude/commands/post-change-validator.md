# Post-Change Validator Skill

**For:** Coder, Tester, DevOps agents
**When injected:** After every Edit() or Write() call

## Automatic verification by file type

After you write or edit a file, **immediately run the verification command for that file type:**

| File type | Command | Timeout | Meaning |
|-----------|---------|---------|---------|
| `.py` | `python -m py_compile {file}` | 5s | Syntax valid? |
| `.ts` | `npx tsc --noEmit {file}` | 10s | Types valid? |
| `.js` | `npx eslint {file}` | 10s | Code style OK? |
| `.json` | `jq . < {file} > /dev/null` | 5s | JSON valid? |
| `.yaml` | `yamllint {file}` | 5s | YAML format OK? |
| `.sh` | `bash -n {file}` | 5s | Shell syntax OK? |
| `.md` | (skip) | - | Documentation, no validation |

## Step-by-step verification

### Step 1: Detect file type
```bash
file_extension="${file##*.}"
```

### Step 2: Run appropriate command
```python
# For .py files:
python -m py_compile src/auth.py
echo $?  # 0 = success, 1 = syntax error

# For .ts files:
npx tsc --noEmit src/auth.ts
echo $?  # 0 = no type errors, 1 = type error
```

### Step 3: Check result
```
If exit code = 0:
  ✅ Verification passed
  Continue to next task

If exit code ≠ 0:
  ❌ Verification failed
  Show error output
  Route to fixing
```

## Handling verification failures

### Failure type: Syntax error
```
❌ Syntax error in src/auth.py:

  File "src/auth.py", line 42
    async def login(user: User {  ← Missing ':' after 'User'
                                 ^

Action: Fix syntax error and re-verify
Command: npx tsc --noEmit src/auth.ts
```

### Failure type: Type error
```
❌ Type error in src/auth.ts:

  src/auth.ts:42 - error TS2339
  Property 'userId' does not exist on type 'User'.

Action: Check User interface or fix property access
Possible fixes:
  - Add userId property to User type
  - Change user.userId to user.id
```

### Failure type: Lint error
```
⚠️ Linting issues in src/auth.ts:

  Line 10: unused variable 'tempToken'
  Line 25: Missing error handling for async function

Action:
  [ ] Fix lint issues (recommended)
  [ ] Continue anyway (not recommended)
  [ ] Ask for help

Decision?
```

## Testing after verification

If syntax check passes, **run tests if available:**

```bash
# Python
pytest tests/test_auth.py -v

# TypeScript/JavaScript
npm test -- auth.test.ts

# Check: Do tests pass?
If PASS (✅):
  → Verification complete, proceed
If FAIL (❌):
  → Code has a logic error, fix it
If NO TESTS:
  → Proceed (but document why)
```

## Verification checklist

After every Edit() or Write(), verify:

```
✓ Step 1: Syntax check
  └─ Command: [appropriate for file type]
  └─ Result: ✅ PASS / ❌ FAIL / ⚠️ WARN

✓ Step 2: If PASS, run tests
  └─ Command: pytest / npm test / [whatever applies]
  └─ Result: ✅ PASS / ❌ FAIL / N/A (no tests)

✓ Step 3: Report result
  └─ ✅ "Verification passed, file is ready"
  └─ ❌ "Verification failed, fix needed"
  └─ ⚠️ "Warnings present, continue anyway?"
```

## Fast path (when you auto-fix)

If error is obvious and fixable, auto-fix and retry:

```
Original code (has error):
  const user: User {  ← Syntax error

Auto-fix:
  const user: User = {

Re-verify:
  python -m py_compile src/auth.py  ← Pass

✅ Fixed and verified
```

Auto-fixes you CAN do:
- ✅ Add missing import: `import { Type } from './module'`
- ✅ Fix obvious syntax: missing `:`, `=`, `{`, etc
- ✅ Add missing type annotation
- ✅ Fix indentation/formatting

Auto-fixes you CANNOT do:
- ❌ Logic changes (could break functionality)
- ❌ API signature changes (affects other code)
- ❌ Data structure changes
- ❌ Breaking changes

## Integration with feedback loop

After verification:

```
Edit(file)
  ↓
Run verification
  ↓
  ├─ ✅ PASS → Show "Verified" → Continue
  │
  ├─ ⚠️ WARN → Ask "Fix warnings?" → Continue or fix
  │
  └─ ❌ FAIL → Show error → Either:
        ├─ Auto-fix if obvious → Re-verify
        └─ Escalate to Critic if complex → Show error, ask for help
```

## Reporting results

Always show verification result clearly:

```
After Edit(src/auth.ts):

Verification: ✅ PASSED
  - Syntax: ✅ Valid TypeScript
  - Types: ✅ No type errors
  - Tests: ✅ All tests passed (3/3)

Ready for next step.
```

Or if failure:

```
After Edit(src/auth.ts):

Verification: ❌ FAILED
  - Syntax: ✅ OK
  - Types: ❌ Property 'userId' not found on User
  - Tests: (skipped due to type error)

Error details:
  src/auth.ts:42 - error TS2339
  Property 'userId' does not exist on type 'User'

Fix needed: Update User interface or correct property name

Need help? Or should I fix this?
```

## Environment considerations

Not all environments have all tools:

```
If npx tsc not found:
  → Notify: "TypeScript not available in environment"
  → Skip type checking (not an error)
  → Continue with other checks

If pytest not available:
  → Notify: "pytest not available"
  → Skip tests (not an error)
  → Recommend user runs locally

If tool not available but critical:
  → Escalate: "Cannot verify without [tool]"
  → Ask user to setup or verify manually
```

## Never skip for

🚨 **ALWAYS verify these, no exceptions:**
- Any `.py` or `.ts` file in `src/` directory
- Any file that will be committed
- Any file affecting logic (not comments only)
- Any file after the first Write() to it

✅ **OK to skip for:**
- `.md` documentation (passive)
- `.json` files if you validated before writing
- Temporary test files (if purpose is obvious)
