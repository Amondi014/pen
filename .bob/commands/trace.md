---
description: "Layer 3: Execute live feature traces via Bob Shell and generate execution-cards.json for the onBob atlas."
---

# onBob Layer 3 — Feature Execution Tracer

You are the onBob Layer 3 tracing agent. Your job is to run live API calls against the target app and trace the execution path through source code.

## STRICT CONSTRAINTS:
- Read the cached `onbob-output/AGENTS.md` FIRST. Do not re-scan the repo.
- Run MAX 5 curl commands total.
- For each command, read only the specific files mentioned in AGENTS.md — not the whole codebase.
- Write all output to `onbob-output/execution-cards.json`

## Step 0: Check App is Running
```bash
curl -s http://localhost:8000/api/v1/health 2>/dev/null || \
curl -s http://localhost:8000/docs 2>/dev/null | grep -o "FastAPI" || \
echo "App not running — using pre-captured output"
```
If app is not running: USE PRE-CAPTURED OUTPUT from the existing execution-cards.json. Do not fail.

## Step 1: Execute Auth Flow
```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")
echo "Token: ${TOKEN:0:50}..."

# Get current user
curl -s http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# List items
curl -s "http://localhost:8000/api/v1/items/?skip=0&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

## Step 2: Trace Each Feature Through Source Code
For each successful curl response:
1. Read the route handler file (from AGENTS.md)
2. Identify the exact function name and line number
3. Identify all function calls within that handler
4. Follow each call to its source file and line number
5. Stop tracing at database calls (don't go into SQLModel internals)

## Step 3: Write execution-cards.json
Write using the exact schema from the pre-seeded version. Replace placeholder data with real:
- Real HTTP responses (or pre-captured if app offline)
- Real file paths and line numbers from the source code
- Real function names

The schema for each feature card:
```json
{
  "id": "feature_id",
  "pillar_id": "pillar_id",
  "title": "Feature Title",
  "description": "One sentence description",
  "command": "curl command string",
  "output": "JSON response string",
  "http_status": "200 OK",
  "captured_at": "ISO timestamp",
  "execution_flow": [
    {
      "step": 1,
      "label": "Step Label",
      "file": "path/to/file.py",
      "line": 42,
      "function": "function_name()",
      "description": "What this step does"
    }
  ]
}
```

## Required Features to Trace:
1. **auth_login** — POST /api/v1/login/access-token
   - Route: backend/app/api/routes/login.py:24 → login_access_token()
   - Logic: backend/app/crud.py:17 → get_user_by_email()
   - Security: backend/app/core/security.py:38 → verify_password()
   - Token: backend/app/core/security.py:52 → create_access_token()

2. **items_list** — GET /api/v1/items/
   - Middleware: backend/app/api/deps.py:42 → get_current_user()
   - Route: backend/app/api/routes/items.py:31 → read_items()
   - DB: backend/app/crud.py:67 → get_items_by_owner()

3. **user_me** — GET /api/v1/users/me
   - DI: backend/app/api/deps.py:42 → get_current_active_user()
   - Route: backend/app/api/routes/users.py:18 → read_user_me()

## Output Confirmation
```
✅ onBob Layer 3 Complete
Execution cards generated:
- auth_login: [success/pre-captured]
- items_list: [success/pre-captured]
- user_me: [success/pre-captured]
File: onbob-output/execution-cards.json
```
