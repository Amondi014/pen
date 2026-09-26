---
description: "onBob: Scan any repository and generate a self-contained Architectural Atlas — interactive HTML viewer with pillar mesh, execution traces, health badges, onboarding quest, and blast radius simulator."
---

# /onBob — Architectural Atlas Generator

> **IBM Bob 2.0 Hackathon Submission**
> One command. Any codebase. Interactive architecture map in under 5 minutes.

---

## Invocation

```
/onBob                        # Full scan — map entire repo
/onBob [feature]              # Surgical trace — focus on one feature
```

---

## What Bob Does

When `/onBob` is triggered, Bob executes the following pipeline **autonomously**:

### Step 1 — Pre-flight
```bash
python scripts/preflight.py
```
Checks Python version, required libs (no external deps needed), and confirms the workspace is readable.

### Step 2 — Scan & Generate `atlas_data.json`
```bash
python scripts/onBob_scanner.py . --out onbob-output
```
Or for a specific sub-folder / cloned target repo:
```bash
python scripts/onBob_scanner.py target-repo --out onbob-output
```

This single command writes `onbob-output/atlas_data.json` containing:
- **Pillars** — codebase clustered into 4–6 architectural domains via keyword + import analysis
- **Edges** — directed dependency graph between pillars
- **Features menu** — Stage 2 "Which feature?" options
- **Execution traces** — static file:line trace per feature (Layer 3)
- **Health metrics** — test coverage, commit freshness, TODO count per pillar
- **Blast radius** — impact simulation per pillar
- **Onboarding quest** — structured learning path generated from the codebase

### Step 3 — Serve the Atlas
```bash
python -m http.server 3000 --directory onbob-output
```
Open: http://localhost:3000/architecture-atlas.html

The atlas is a **zero-dependency, self-contained HTML file** that reads `atlas_data.json` at boot.
It requires an HTTP server (not `file://`) due to the `fetch()` call.

---

## STRICT CONSTRAINTS

1. **Read-Only** — never modify, delete, or commit any file in the target repo
2. **Max 200 files read** per scan — scanner already enforces this
3. **Output only to `onbob-output/`** — never write to the target repo itself
4. **If the app is not running** — scanner still works (static analysis only); Layer 3 traces use pre-seeded fallbacks

---

## Stage 2 CTA — "Which Feature?"

After the atlas renders, Bob prints this menu in chat (pulled from `atlas_data.json`):

```
[onBob] Scan complete.

  Repo    : full-stack-fastapi-template
  Stack   : FastAPI · TypeScript
  Pillars : 6     Edges: 8     Traces: 6
  Atlas   : http://localhost:3000/architecture-atlas.html

Which feature would you like to trace in depth?

  1. Request Lifecycle — inbound request -> routing -> response
  2. Authentication Flow — login -> token issue -> session
  3. Core Business Logic — domain logic -> data transform
  4. Data Persistence — query -> ORM -> database write
  5. Client Data Fetch — UI action -> API call -> render

Reply with a number, or type: /onBob [feature keyword]
```

---

## Layer 3 — Feature Trace (Branch B)

```
/onBob auth
```

Bob reads `onbob-output/atlas_data.json`, finds all features matching "auth", opens the trace drawer in the atlas, and prints the execution flow to chat with clickable `file:line` references.

---

## Output Files

| File | Description |
|------|-------------|
| `onbob-output/atlas_data.json` | Single source of truth — all scanner output |
| `onbob-output/architecture-atlas.html` | Interactive viewer (reads atlas_data.json) |
| `onbob-output/AGENTS.md` *(legacy)* | Human-readable repo index |

---

## Target Repo Demo

```bash
git clone --depth=1 https://github.com/tiangolo/full-stack-fastapi-template target-repo
python scripts/onBob_scanner.py target-repo --out onbob-output
python -m http.server 3000 --directory onbob-output
# -> http://localhost:3000/architecture-atlas.html
```

This repo (~30k stars, FastAPI + React, PostgreSQL) produces:
- 6 architectural pillars (Ingress, Auth, Core, Data, Frontend, Infra)
- 8 dependency edges
- 6 feature execution traces
- Full health + quest + blast radius data
