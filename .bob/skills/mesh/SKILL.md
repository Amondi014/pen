---
name: mesh
description: >-
  Layer 2: Parse the target repo for inter-pillar connections using import
  analysis, then output edges.json and present the 'Which feature?' CTA to the
  user.
metadata:
  user-invocable: true
  disable-model-invocation: true
---

# onBob Layer 2 — Mesh Engine

You are the onBob Layer 2 mesh agent. Your job is to discover connections between architectural pillars and produce edges.json.

## STRICT CONSTRAINTS:
- Read `onbob-output/pillars.json` FIRST — do not re-scan the repo.
- Only trace connections BETWEEN pillars (not within the same pillar).
- Detect MAX 8 edges total. Quality over quantity.
- Run `scripts/mesh-builder.py` via Bob Shell if it exists.
- Write output to `onbob-output/edges.json`.

## Step 1: Read Pillar Context
Read `onbob-output/AGENTS.md` and `onbob-output/pillars.json`.
Note which files belong to which pillar.

## Step 2: Detect Cross-Pillar Connections
Run in Bob Shell:
```bash
cd target-repo
# Find imports between pillar directories
grep -rn "from app.api.deps import" backend/app/api/routes/ 2>/dev/null | head -10
grep -rn "from app.crud import" backend/app/api/routes/ 2>/dev/null | head -10
grep -rn "from app.core.security import" backend/app/ 2>/dev/null | head -10
grep -rn "from app.models import" backend/app/ 2>/dev/null | head -10
# Find HTTP calls from frontend
grep -rn "openapi" frontend/src/ 2>/dev/null | head -5
grep -rn "/api/v1" frontend/src/ 2>/dev/null | head -10
```

## Step 3: Classify Each Connection
For each connection found:
- **HTTP/REST**: Frontend calls backend API routes → color #3B82F6 (blue), animated: true
- **Database**: Route handlers call CRUD/models → color #10B981 (green), animated: false
- **Auth dependency**: Routes importing deps.py/security → color #8B5CF6 (purple), animated: true

## Step 4: Write edges.json
Use the exact schema from the pre-seeded version in `onbob-output/edges.json`.
Each edge needs: id, source (pillar_id), target (pillar_id), protocol, label (exact function/endpoint), color, animated, type.

Include a `features_menu` array with these 3 features:
- auth_login: POST /api/v1/login/access-token (pillar: identity)
- items_list: GET /api/v1/items/ (pillar: core-engine)
- user_me: GET /api/v1/users/me (pillar: identity)

## Step 5: Present the "Which Feature?" CTA
After writing edges.json, output this message in Bob chat:

```
✅ onBob Layer 2 Complete — Mesh mapped.

Found [N] connections between 5 architectural pillars.

🔍 LAYER 3 READY — Which feature would you like to explore in-depth?

  1. 🔐 User Authentication — POST /api/v1/login/access-token
     Traces: Route Handler → Password Check → JWT Sign → Response

  2. 📦 List Items — GET /api/v1/items/
     Traces: Auth Middleware → Route Handler → DB Query → Pagination

  3. 👤 Get Current User — GET /api/v1/users/me
     Traces: JWT Decode → Dependency Injection → User Model

Reply with the NUMBER of the feature to run a live execution trace.
```

Wait for user to reply with a number. Then execute the corresponding trace from `.bob/commands/trace.md`.
