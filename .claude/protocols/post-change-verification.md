# Post-Change Verification Protocol

Validate code integrity after every Edit() or Write().

## Verification triggers

After **every Edit() or Write()**, automatically determine test command:

| File type | Extension | Verification command | Timeout | Failure action |
|-----------|-----------|----------------------|---------|-----------------|
| Python | `.py` | `python -m py_compile {file}` | 5s | Show syntax error |
| Python (with tests) | `.py` | `pytest {test_file}` | 30s | Show test failure |
| TypeScript | `.ts` | `npx tsc --noEmit {file}` | 10s | Show type error |
| JavaScript | `.js` | `npx eslint {file}` | 10s | Show lint error |
| JSON | `.json` | `jq . < {file} > /dev/null` | 5s | Show parse error |
| YAML | `.yaml` | `yamllint {file}` | 5s | Show format error |
| Shell | `.sh` | `bash -n {file}` | 5s | Show syntax error |
| Markdown | `.md` | Skip (passive) | - | - |
| Config | `.json` `.yaml` | Auto-detect + validate | 5s | Show error |

## Verification flow

```
Edit(file_path) or Write(file_path)
  ↓
Detect file type
  ↓
Run verification command [timeout 30s]
  ↓
  ├─ PASS (exit code 0)
  │   └─ ✅ Show: "[file] verified"
  │       Continue normally
  │
  ├─ FAIL (exit code 1)
  │   └─ ❌ Show error output
  │       Route to Coder + Critic
  │       Update progress.json: status = "blocked"
  │       Ask: "Fix and retry?"
  │
  └─ TIMEOUT (>30s)
      └─ ⚠️ Show: "Verification took too long"
          Ask user: "Skip verification? [Yes/No]"
```

## Verification by language

### Python

```bash
# Step 1: Syntax check (always)
python -m py_compile {file}

# Step 2: Type check (if using type hints)
mypy {file} --ignore-missing-imports

# Step 3: Lint (if project has pylint/flake8)
pylint {file} --disable=all --enable=syntax-error

# Step 4: Unit tests (if {file} is in src/)
pytest tests/test_{basename}.py -v
```

### TypeScript/JavaScript

```bash
# Step 1: Type check (if TypeScript)
npx tsc --noEmit {file}

# Step 2: Lint
npx eslint {file}

# Step 3: Format check (if prettier)
npx prettier --check {file}

# Step 4: Tests (if modified)
npm test -- --testNamePattern={function_name}
```

### JSON/YAML

```bash
# JSON
jq . < {file} > /dev/null && echo "✅ Valid JSON"

# YAML
yamllint {file} && echo "✅ Valid YAML"

# Both
jsonschema validate {file} --schema {schema.json}
```

## Memory tracking

Update progress.json after verification:

```json
{
  "id": "TASK-001",
  "title": "Fix authentication bug",
  "status": "in_progress",
  "lastChange": {
    "file": "src/auth.ts",
    "timestamp": "2026-02-22T10:30:00Z",
    "verification": {
      "status": "passed",
      "command": "npm test -- auth.test.ts",
      "duration": "8.2s"
    }
  }
}
```

## Failure scenarios

### Scenario 1: Syntax error
```
❌ Verification failed: src/auth.ts

Error:
  File "src/auth.ts", line 42
    const user: User {  ← Missing '=' before '{'
          ^
SyntaxError

Action: Fix the syntax and retry.
Command: Edit src/auth.ts → Re-run verification
```

### Scenario 2: Test failure
```
❌ Verification failed: tests/auth.test.ts

Failure:
  ✗ should authenticate valid user
    Expected: true
    Received: false

Action:
  1. Debug: What changed that broke this test?
  2. Revert Edit or fix code
  3. Re-run verification

Need help? Reply: "debug this test"
```

### Scenario 3: Lint error
```
⚠️ Lint warnings in src/auth.ts

Warnings:
  Line 10: unused variable 'tempToken'
  Line 25: missing error handling for async call

Action:
  [ ] Fix warnings (recommended)
  [ ] Continue anyway (not recommended)
  [ ] Ask for help

Choice:
```

## Verification skip scenarios

Acceptable reasons to skip:
- File is `.md` (documentation)
- File is `.config.json` (configuration, manually validated)
- User explicitly says: "Skip verification"
- Verification command not available (e.g., no pytest in environment)

Never skip for:
- `.py` files in `src/`
- `.ts` files in `src/`
- Any file that will be committed

## Integration with feedback loop

After verification result:

| Result | Feedback Loop Action |
|--------|----------------------|
| ✅ PASS | Continue, proceed to next task |
| ❌ FAIL | Stop, route to Coder + show error |
| ⚠️ WARNING | Ask user: continue or fix? |
| ⏱️ TIMEOUT | Ask user: skip or investigate? |

## Auto-fix attempts

For known errors, Agent may auto-fix and retry:

```
Verification failed: Missing import

Fix attempt:
  Add: import { User } from './types'
  Re-verify...

✅ Verification passed after fix!
```

Acceptable auto-fixes:
- Add missing imports
- Fix obvious syntax errors
- Add type annotations (if type error)

Not acceptable (escalate):
- Logic changes
- Breaking API changes
- Data loss scenarios
