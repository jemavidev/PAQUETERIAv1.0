# Log Analysis & Diagnostics Skill

**For:** DevOps, Security, Tester agents
**When injected:** Debugging CI/CD failures, performance issues, security events

## Log types & parsing

### CI/CD Logs (GitHub Actions, GitLab, Jenkins)

**Structure:**
```
[timestamp] [job-id] [stage] [level] [message]

Example:
2026-02-22T10:30:45Z [build-123] [test] ERROR npm test failed: exit code 1
2026-02-22T10:30:50Z [build-123] [test] ERROR    at Function.Module._load (internal/modules/esm/loader.js:492:17)
2026-02-22T10:31:00Z [build-123] [deploy] BLOCKED Deployment halted due to test failures
```

**Key fields to extract:**
- Timestamp
- Job/Step name
- Status (PASS, FAIL, BLOCKED, TIMEOUT)
- Error message + context
- Duration

**Parsing strategy:**
```
1. Find lines with level=ERROR or FAIL
2. Extract context (2-3 lines before + after)
3. Identify error type (syntax, type, runtime, timeout)
4. Find root cause (not just symptom)
5. Suggest fixes
```

### Application Logs (Python, Node.js, Java)

**Structure:**
```
[timestamp] [logger] [level] [message] [stack-trace]

Example:
2026-02-22T10:30:45.123 auth.service ERROR Database connection failed
  Error: connect ECONNREFUSED 127.0.0.1:5432
    at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1141:14)
```

**Key fields:**
- Timestamp
- Logger name (service, module)
- Level (DEBUG, INFO, WARN, ERROR, FATAL)
- Message
- Stack trace (if available)

**Parsing strategy:**
```
1. Extract ERROR/FATAL lines
2. Look for stack traces (chain back to root cause)
3. Identify error class (TypeError, ConnectionError, etc)
4. Find where error originated (first file in stack)
5. Correlate with recent deployments
```

### Performance Logs (Flame graphs, timing data)

**Structure:**
```
[function] [time_ms] [samples] [percentage]

Example:
database.query 450ms 120 35%
authentication.validate 280ms 75 22%
json.stringify 180ms 48 14%
```

**Parsing strategy:**
```
1. Rank by time spent
2. Identify bottlenecks (>100ms)
3. Find hot paths (called frequently + slow)
4. Suggest optimization targets
```

## Debugging workflows

### Workflow 1: "CI pipeline failed"

```
Step 1: Identify failure point
  - Parse logs for ERROR/FAIL
  - Find first error (root cause)
  - Note the step/stage

Step 2: Understand error
  - Extract error message
  - Get context (2-3 lines before/after)
  - Identify error type (syntax, type, runtime)

Step 3: Root cause analysis
  - "npm test failed" → What test?
  - "Type error" → Which line?
  - "Connection refused" → Which service?

Step 4: Suggest fix
  - Syntax errors → Show correction
  - Type errors → Fix type or interface
  - Connection → Check service health
  - Timeout → Increase limit or optimize

Example:
```
Error: Cannot find module 'react'
  at Module._load (internal/modules/esm/loader.js:492:17)

Root cause: react not installed
Suggestion: npm install
```

### Workflow 2: "Performance degradation"

```
Step 1: Get baseline
  - Previous request time: 200ms
  - Current request time: 2000ms
  - Degradation: 10x slower

Step 2: Identify change
  - "What changed since last deploy?"
  - New database query?
  - New dependency?
  - More data processing?

Step 3: Profile hotspots
  - Where is time spent?
  - Database? API? Processing?
  - Frequency vs duration?

Step 4: Optimize
  - Add database index
  - Cache query results
  - Batch API calls
  - Async processing

Example:
```
Profile:
  - database.query: 1500ms (75%) ← Hotspot
  - json.stringify: 300ms (15%)
  - api.call: 200ms (10%)

Suggestion: Add index to slow database query
Command: CREATE INDEX idx_user_id ON orders(user_id)
```

### Workflow 3: "Security incident"

```
Step 1: Identify attack pattern
  - Multiple failed logins? Brute force?
  - Unusual data access? Privilege escalation?
  - High volume from single IP? DDoS?

Step 2: Timeline
  - When did it start?
  - Duration?
  - Impact scope?

Step 3: Containment
  - Block IP?
  - Reset passwords?
  - Rotate credentials?

Step 4: Investigation
  - What was accessed?
  - What was modified?
  - Evidence for forensics?

Example:
```
Pattern: 500 failed login attempts in 5 minutes
  From: 192.168.1.100
  Accounts targeted: admin, root, user1

Action: Block IP 192.168.1.100
Monitor: Watch for similar patterns
Investigate: Why this IP? Compromised user nearby?
```

## Error pattern recognition

### Pattern 1: Memory leak
```
Symptoms:
  - Memory usage increases over time
  - GC pauses getting longer
  - Eventually crashes with OutOfMemory

Indicators in logs:
  - "Heap out of memory"
  - GC time increasing
  - Request latency spikes

Root causes:
  - Unclosed database connections
  - Event listeners not removed
  - Global caches growing unbounded
  - Circular references

Fixes:
  - Close connections properly
  - Remove listeners on cleanup
  - Implement cache eviction
  - Use WeakMap for caches
```

### Pattern 2: N+1 query problem
```
Symptoms:
  - Database queries exploding
  - Page load time increasing
  - Database CPU at 100%

Indicators:
  - "Executing 1000 queries for 100 users"
  - SELECT in a loop
  - Per-row database calls

Fixes:
  - Batch queries with JOIN
  - Load related data upfront
  - Implement caching
  - Use DataLoader pattern
```

### Pattern 3: Cascading failures
```
Symptoms:
  - One service fails
  - Calls to service timeout
  - Whole system goes down

Indicators:
  - Service A fails
  - Service B calls Service A → timeout
  - Service C calls Service B → timeout
  - Cascade continues

Fixes:
  - Add circuit breakers
  - Implement timeouts
  - Graceful degradation
  - Bulkhead isolation
```

### Pattern 4: Dependency version conflict
```
Symptoms:
  - "Module not found"
  - "Unexpected token" in imported code
  - "X is not a function"

Indicators in logs:
  - TypeError at module level
  - Module structure changed
  - Version mismatch

Fixes:
  - npm list {package} (find conflicts)
  - npm dedupe (consolidate versions)
  - npm update (latest compatible)
  - Lock file corruption? Delete node_modules + reinstall
```

## Log parsing commands

### Extract errors
```bash
# Find all ERROR lines
grep -i ERROR log.txt | head -20

# With context
grep -i ERROR -A 5 log.txt

# Count errors by type
grep -i ERROR log.txt | cut -d: -f2 | sort | uniq -c | sort -rn
```

### Parse structured logs (JSON)
```bash
# Pretty print
jq . log.json | head -100

# Extract field
jq '.errors[].message' log.json

# Filter by level
jq '.[] | select(.level=="ERROR")' log.json

# Count by error type
jq '[.[] | select(.level=="ERROR") | .error_type] | group_by(.) | map({type: .[0], count: length})' log.json
```

### Analyze performance
```bash
# Extract request times
grep "request_time:" log.txt | sed 's/.*request_time: //g' | sort -rn | head -20

# Calculate average
grep "request_time:" log.txt | sed 's/.*request_time: //g' | awk '{sum+=$1; count++} END {print sum/count}'

# Find slow requests
grep "request_time:" log.txt | awk -F: '$NF > 1000 {print}' | head -20
```

## Best practices

### DO:

✅ **Correlate logs across services**
```
Service A ERROR → Check Service B logs at same timestamp
↓
Find cascading failure pattern
↓
Identify root cause
```

✅ **Look for patterns, not just errors**
```
Single error: Might be transient
Same error 3x: Problem pattern emerging
Same error 100x: Systemic issue
```

✅ **Get full context**
```
Error message: "Database error"
← Not helpful alone

Error message + context:
  "Database error: ECONNREFUSED port 5432"
  "Previous: Database healthy"
  "Recent: Database server rebooted"
← Much more actionable
```

✅ **Check timestamps carefully**
```
Error at 10:30:45
↓
What changed at 10:30? (Deployment? Spike?)
↓
Correlate with other service logs
```

### DON'T:

❌ **Assume first error is root cause**
```
You see: "Module not found"
Don't assume: Missing npm install
Check: Did import path change? Version conflict? Cache issue?
```

❌ **Ignore error patterns**
```
"Connection timeout" appearing 100x?
Don't assume: Temporary network issue
Check: Service constantly crashing? Overloaded?
```

❌ **Miss the signal in noise**
```
1 ERROR in 10,000 lines of logs?
Don't assume: Irrelevant
Check: When did it happen? What service? What changed?
```

## Integration with other skills

### With Anti-Loop Validator:
```
If analysis loops:
- Fetch logs → Find same error
- Fetch logs again → Same error
- Fetch logs 3x → Same error

⚠️ Loop detected: "Fetching same logs repeatedly"
Action: Try different log source or deeper analysis
```

### With Post-Change Validator:
```
After DevOps change:
- Change deployed
- Logs fetched and analyzed
- Errors detected → Block deployment
- Fix + re-deploy
```

### With Tool Selection Guide:
```
Parse logs with:
✅ Grep for error patterns
✅ Read for context
✅ Bash with jq for JSON parsing
❌ Not Bash with complex sed/awk chains
```

## Real examples

### Example 1: GitHub Actions failure

```
Logs show:
  npm ERR! 404  Not Found - GET https://registry.npmjs.org/some-package
  npm ERR! 404  In most cases you or one of your dependencies are requesting
  npm ERR! 404  a package version that doesn't exist.

Root cause: Package version doesn't exist
Suggestion: Check package.json version string, use npm list some-package

Fix: Update package.json to valid version
```

### Example 2: Database performance

```
Logs show:
  query: SELECT * FROM orders WHERE user_id = ? → 1200ms
  query: SELECT * FROM orders WHERE user_id = ? → 1150ms
  query: SELECT * FROM orders WHERE user_id = ? → 1300ms

Root cause: Missing index on user_id
Suggestion: CREATE INDEX idx_orders_user_id ON orders(user_id)

Expected after fix: 1200ms → 50ms (24x faster)
```

### Example 3: Memory leak

```
Logs show:
  Memory: 150MB (start)
  Memory: 280MB (after 1000 requests)
  Memory: 450MB (after 2000 requests)
  GC pause: 100ms
  GC pause: 250ms
  GC pause: 500ms

Root cause: Memory not being released
Investigation: Check for:
  - Unclosed database connections
  - Event listeners not removed
  - Growing arrays in memory
  - Circular references

Action: Profile with heap dump, identify retainers
```

