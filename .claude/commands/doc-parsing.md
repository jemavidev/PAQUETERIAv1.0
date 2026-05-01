# Doc Parsing & External API Research Skill

**For:** Researcher agent
**When injected:** Tasks requiring reading external documentation, API specs, or technical references

## Domains

- OpenAPI/Swagger specifications
- Framework documentation (React, Next.js, FastAPI, Django, etc)
- Third-party API references (Stripe, AWS, Firebase, etc)
- Technical guides and tutorials
- Architecture documentation
- Implementation examples

## Research workflow

### Phase 1: Discovery

**Before fetching:**
1. Clarify what you're researching: "React hooks API"
2. Identify sources: Official docs, GitHub, specification
3. Estimate scope: 1 doc or 5+ docs?

**What to fetch:**
- Official documentation (most reliable)
- GitHub README + examples
- API specification (OpenAPI/Swagger)
- Implementation guides
- Comparison articles

**What to skip:**
- Blog posts (often outdated)
- Stack Overflow answers (fragmented)
- Medium articles (medium quality)
- Reddit discussions (subjective)

### Phase 2: Fetching

Use WebFetch for:
```
WebFetch(
  url="https://react.dev/reference/react/hooks",
  prompt="List all React hooks with brief descriptions"
)
```

Best practices:
- ✅ Fetch official docs first
- ✅ Use specific URLs (not homepage)
- ✅ Limit to 5 WebFetch calls per session (context budget)
- ✅ Specific prompt describing what you need
- ✅ Include version info if relevant

### Phase 3: Synthesis

After fetching, synthesize:

```
Research: "How does OAuth2 work?"

Fetched:
1. OAuth2 official spec (RFC 6749)
2. Auth0 implementation guide
3. Google OAuth2 example

Synthesis:
→ OAuth2 is a delegation protocol (not authentication)
→ 4 grant types: Authorization Code, Implicit, Client Credentials, Resource Owner
→ Best for: delegating access without sharing passwords
→ Modern alternative: OpenID Connect (adds authentication)
```

## Common research patterns

### Pattern 1: "Understand a new library"

```
Task: Research GraphQL and its benefits

1. Discovery:
   - Official: graphql.org
   - Implementation: apollo.io
   - Comparison: GraphQL vs REST

2. Fetch:
   WebFetch("https://graphql.org/learn", "What is GraphQL and why use it?")
   WebFetch("https://www.apollographql.com/docs", "GraphQL advantages")

3. Synthesis:
   → Query language for APIs (strongly typed)
   → Request exactly what you need (no over/under fetching)
   → Real-time subscriptions
   → Introspection (self-documenting)
   → Better DX than REST
   → Trade-off: Complexity, caching, N+1 queries
```

### Pattern 2: "Compare two approaches"

```
Task: Should we use REST or GraphQL?

1. Discovery:
   - REST best practices
   - GraphQL specification
   - Real-world comparisons

2. Fetch:
   WebFetch("https://restfulapi.net", "REST principles and examples")
   WebFetch("https://graphql.org", "GraphQL advantages")
   WebFetch(comparison article, "REST vs GraphQL trade-offs")

3. Synthesis:
   REST:
   ├─ Pros: Simple, cacheable, ubiquitous
   └─ Cons: Over-fetching, under-fetching, versioning

   GraphQL:
   ├─ Pros: Exact queries, real-time, introspection
   └─ Cons: Complexity, N+1, caching harder

   Recommendation:
   ├─ REST: For simple CRUD, public APIs, third-party integration
   └─ GraphQL: For complex queries, mobile clients, real-time
```

### Pattern 3: "API implementation details"

```
Task: How to implement OAuth2 in Node.js?

1. Discovery:
   - Official OAuth2 spec
   - Passport.js guide
   - Express.js middleware
   - Example implementation

2. Fetch:
   WebFetch("https://oauth.net/2/", "OAuth2 flows")
   WebFetch("http://www.passportjs.org", "Passport.js strategy")
   WebFetch(example, "Node OAuth2 implementation")

3. Synthesis:
   Flow:
   ├─ User clicks "Login with Google"
   ├─ Redirect to Google consent screen
   ├─ Google redirects back with auth code
   ├─ Server exchanges code for token
   └─ Server creates user session

   Implementation:
   ├─ Use Passport.js + express-session
   ├─ Configure Google OAuth2 strategy
   ├─ Protect routes with middleware
   └─ Handle token refresh
```

### Pattern 4: "Architecture decision research"

```
Task: Should we use microservices or monolith?

1. Discovery:
   - Microservices patterns (Netflix, Amazon)
   - Monolith best practices
   - Trade-offs and patterns
   - Real-world case studies

2. Fetch:
   WebFetch("https://martinfowler.com/articles/microservices", "Microservices")
   WebFetch("enterprise doc", "Monolith vs Microservices")
   WebFetch("case study", "When to use each")

3. Synthesis:
   Monolith:
   ├─ Better for: Startups, <10 services, shared domain
   ├─ Advantages: Simpler, easier monitoring, easier deployment
   └─ Disadvantages: Scaling limits, tight coupling

   Microservices:
   ├─ Better for: Large teams, independent services, scaling
   ├─ Advantages: Scalability, independent deployment, tech diversity
   └─ Disadvantages: Complexity, distributed systems challenges, ops burden

   Recommendation:
   └─ Start monolith, migrate if needed (not day 1)
```

## Context management

### Token budget

Each WebFetch costs ~200-500 tokens depending on page size.

Budget allocation:
```
Per research session: ~5,000 tokens
├─ WebFetch calls: 5-10 calls max
│  ├─ Each call: 200-500 tokens
│  └─ Total: 1,000-5,000 tokens
├─ Synthesis: 1,000-2,000 tokens
└─ Formatting results: 500-1,000 tokens
```

If approaching limit:
```
[ ] Have I fetched the most important sources?
[ ] Can I synthesize with what I have?
[ ] Should I defer less critical research?
```

### Avoiding context bloat

DO:
- ✅ Fetch focused URLs (documentation page, not homepage)
- ✅ Use specific prompts ("List API methods" not "Tell me everything")
- ✅ Limit to essential sources
- ✅ Summarize findings, don't dump raw content

DON'T:
- ❌ Fetch entire blogs or documentation sites
- ❌ Broad prompts ("Research X")
- ❌ Fetch 20 sources for simple questions
- ❌ Paste entire fetched content in response

## Synthesis formats

### Format 1: List of key concepts

```
## OAuth2 Components

- **Authorization Server:** Issues tokens (e.g., Google)
- **Resource Server:** Stores user data (e.g., Gmail API)
- **Client:** Your app requesting access
- **Grant Type:** How client obtains token
- **Scope:** Permissions being requested
```

### Format 2: Comparison table

```
| Aspect | REST | GraphQL |
|--------|------|---------|
| Query | Fixed endpoints | Flexible queries |
| Response | All fields | Requested fields only |
| Versioning | URL/header | None needed |
| Caching | HTTP caching | Complex |
| Real-time | Webhooks | Subscriptions |
```

### Format 3: Decision tree

```
Choose architecture:
├─ <50 engineers? → Monolith preferred
├─ 50-500 engineers? → Consider microservices
├─ 500+ engineers? → Microservices recommended
└─ Services independent? → Microservices advantageous
```

### Format 4: Implementation guide

```
## Implement OAuth2 in Node.js

1. **Setup**
   - npm install passport passport-oauth2 express-session

2. **Configure**
   - Register OAuth app (get client_id, client_secret)
   - Set redirect URI

3. **Implement**
   - Create Passport strategy
   - Attach to login route
   - Handle callback

4. **Test**
   - Click "Login"
   - Verify OAuth flow
   - Check token storage
```

## Quality checklist

Before delivering research:

```
[ ] Primary sources fetched (official docs, specs)?
[ ] Information current (check dates, versions)?
[ ] Synthesized clearly (not raw dumps)?
[ ] Key trade-offs identified?
[ ] Recommendations provided (if applicable)?
[ ] Sources cited (links to original)?
[ ] Scope bounded (relevant to task)?
[ ] Token budget respected?
```

## When to escalate to different agent

After research, recommend:

```
If research is about:
├─ Implementation → Route to Coder
├─ Architecture → Route to Architect
├─ Security → Route to Security
├─ Testing → Route to Tester
├─ Performance → Route to Data Scientist
└─ DevOps → Route to DevOps
```

Example:
```
Research: "How to implement rate limiting?"

Findings:
- Three approaches: Token bucket, sliding window, fixed window
- Token bucket most flexible
- Libraries: express-rate-limit, redis-rate-limit

Route to: Coder agent
Task: "Implement rate limiting using express-rate-limit,
       following token bucket pattern"
```

## Common mistakes

🚫 **Mistake 1: Fetching too many sources**
```
WRONG: WebFetch 20 different tutorials
RIGHT: WebFetch 2-3 official sources + 1 comparison
```

🚫 **Mistake 2: Dumping raw content**
```
WRONG: Copy-paste entire fetched documentation
RIGHT: Synthesize: "From the docs, key concepts are..."
```

🚫 **Mistake 3: Not citing sources**
```
WRONG: "GraphQL is a query language" (no source)
RIGHT: "Per graphql.org, GraphQL is a query language..."
```

🚫 **Mistake 4: Researching outdated sources**
```
WRONG: Fetch blog post from 2015
RIGHT: Check date first, prefer recent official docs
```

🚫 **Mistake 5: Trying to be exhaustive**
```
WRONG: "Let me research every authentication method"
RIGHT: "Let me research JWT vs OAuth2 for this use case"
```

## Performance tips

### Speed ranking:
1. **Official docs** — Most complete, up-to-date
2. **API specifications** — Authoritative, comprehensive
3. **Framework guides** — Well-maintained, current
4. **Case studies** — Real-world examples
5. **Blog posts** — Variable quality, often outdated

### Search strategy:
1. Start with official source
2. If insufficient, find 1 authoritative comparison
3. If still unclear, fetch 1 implementation example
4. Synthesize findings
5. Stop (don't keep searching)

### Timeboxing:
- Simple question: 1-2 sources, 5 minutes
- Medium question: 3-4 sources, 10 minutes
- Complex question: 5 sources max, 15 minutes
- If still unclear after 15 min → Escalate to specialist

## Integration with other skills

### With Anti-Loop Validator:
```
If you find yourself:
- WebFetch(doc1) → synthesis unclear
- WebFetch(doc2) → still unclear
- WebFetch(doc3) → same concepts repeated

⚠️ Loop detected: "Fetching similar sources repeatedly"
Action: Escalate to specialist with findings so far
```

### With Post-Change Validator:
```
After research, if implementing:
- Research complete
- Route findings to Coder
- Coder implements + verifies
- Post-change validator confirms
```

### With Triviality Detector:
```
If research task is trivial:
- Question: "What is X?" (answered in 1 doc)
- Triviality score: High
- Suggestion: Look up in docs manually, not full research
```

## Real examples

### Example 1: "Should we use TypeScript?"

```
Fetch:
- Official: typescriptlang.org
- Comparison: "TypeScript vs JavaScript trade-offs"

Synthesis:
Benefits:
├─ Type safety (catch errors early)
├─ Better IDE support (autocomplete, refactoring)
├─ Self-documenting code (types are docs)
└─ Scalability (large teams)

Trade-offs:
├─ Setup complexity (build step)
├─ Learning curve
├─ Build time overhead
└─ More verbose initially

Recommendation:
├─ YES for: Teams >5, long-term projects, complex domains
└─ NO for: Prototypes, solo projects, quick scripts

Result: Route to Architect for decision, Coder for setup
```

### Example 2: "How do we scale to 1M users?"

```
Fetch:
- Scaling fundamentals
- Database optimization
- Caching strategies
- Load balancing

Synthesis:
Phases:
├─ 0-10k: Single database sufficient
├─ 10k-100k: Add caching (Redis)
├─ 100k-1M: Database replication + load balancing
└─ 1M+: Sharding, microservices

Key strategies:
├─ Caching (Redis for session, data)
├─ Database optimization (indexes, queries)
├─ Load balancing (traffic distribution)
├─ CDN (static assets)
└─ Monitoring (detect bottlenecks)

Result: Route to DevOps + Architect for implementation plan
```

