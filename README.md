# onBob — Architectural Atlas
### IBM Bob 2.0 Hackathon Submission

> **"While everyone else reads code to understand the app, interns using onBob click the app to understand the code."**

[![IBM Bob 2.0](https://img.shields.io/badge/IBM%20Bob-2.0-7c3aed)](https://www.ibm.com)
[![Target Repo](https://img.shields.io/badge/target-tiangolo%2Ffull--stack--fastapi--template-blue)](https://github.com/tiangolo/full-stack-fastapi-template)
[![Read-Only](https://img.shields.io/badge/mode-read--only-green)](.)
[![License: MIT](https://img.shields.io/badge/license-MIT-orange)](.)

---

## What is onBob?

**onBob** is an IBM Bob 2.0 agent workflow that automatically generates an **Architectural Atlas** for any codebase — a self-contained interactive HTML file that maps a running application's UI to its backend architectural pillars, bidirectionally.

**The Problem it Solves:**
New developers spend 2–4 weeks just comprehending unfamiliar codebases. Existing documentation is manually maintained and always out of date. onBob inverts this: instead of reading code to understand the app, you click the app to understand the code.

---

## Quick Start

```bash
# 1. Clone the target repo
git clone https://github.com/tiangolo/full-stack-fastapi-template target-repo
cd target-repo && docker compose up -d

# 2. Open the atlas (no server needed)
open onbob-output/architecture-atlas.html
# OR serve it:
python -m http.server 3000 --directory onbob-output
```

Open `http://localhost:3000/architecture-atlas.html` in your browser.

---

## How It Works — The 3 Layers

### Layer 1: Repository Scan
Bob reads the target codebase (MAX 25 files, read-only), clusters files into **5 architectural pillars**, and generates:
- `onbob-output/pillars.json` — pillar definitions
- `onbob-output/health.json` — test coverage, commit age, TODOs
- `onbob-output/quest.json` — structured onboarding checklist
- `onbob-output/AGENTS.md` — repo index for Layer 3

```
# Bob Prompt (paste into Bob chat):
Execute the onBob Layer 1 scan using the skill defined in .bob/commands/scan.md
Target repository: target-repo/
Output directory: onbob-output/
```

### Layer 2: Dependency Mesh
Bob analyzes cross-pillar import/call relationships and maps them as animated connection edges:
- `onbob-output/edges.json` — directed connection graph
- Presents the **"Which feature?" CTA** for Layer 3

```
# Bob Prompt:
Execute the onBob Layer 2 mesh analysis using .bob/commands/mesh.md
```

### Layer 3: Live Execution Trace
Bob runs real `curl` commands against the live app and traces execution through source files with exact `file:line` mapping:
- `onbob-output/execution-cards.json` — feature execution traces

```
# Bob Prompt:
Execute the onBob Layer 3 feature trace using the skill defined in .bob/commands/trace.md
```

---

## The Architectural Atlas

Open `onbob-output/architecture-atlas.html` — a **100% self-contained HTML file** that works in any browser with zero setup.

### Features:
- **🏛️ Blueprint View** — Interactive layered architecture diagram
- **🕸️ L2 Dependency Mesh** — Animated edge graph with REST/DB connection types
- **⚡ Layer 3 Execution Traces** — Real curl output + file:line step-by-step traces
- **🏥 Health Badges** — Test coverage, commit age, TODO count per pillar
- **🎯 Onboarding Quest** — Structured Day 1 / Week 1 / Month 1 learning path
- **💥 Blast Radius Simulator** — Simulate what breaks if any pillar is modified
- **↔️ Bidirectional Navigation** — Click UI → find code, click pillar → find UI

### Target Repository
The default atlas targets **`tiangolo/full-stack-fastapi-template`** (~30k ⭐):

| Pillar | Files | Team |
|--------|-------|------|
| 🔐 Identity | login.py, security.py, users.py | #team-backend |
| ⚙️ Core Engine | items.py, crud.py | #team-backend |
| 🗄️ Data Layer | models.py, db.py, alembic/ | #team-platform |
| 🌐 API Gateway | main.py, deps.py, api/main.py | #team-backend |
| 🖥️ Frontend Shell | main.tsx, router.tsx, client/ | #team-frontend |

---

## Repository Structure

```
onbob/
├── README.md                          ← This file
├── AGENTS.md                          ← Bob-generated repo execution index
│
├── .bob/
│   ├── commands/
│   │   ├── scan.md                    ← Layer 1: repo scanner skill
│   │   ├── mesh.md                    ← Layer 2: dependency mesh skill
│   │   └── trace.md                   ← Layer 3: execution tracer skill
│   └── evidence/                      ← Screenshot evidence (hackathon requirement)
│
├── onbob-output/                      ← ALL generated artifacts
│   ├── architecture-atlas.html        ← THE MAIN DELIVERABLE ⭐
│   ├── pillars.json                   ← Layer 1: architectural pillars
│   ├── edges.json                     ← Layer 2: dependency mesh
│   ├── execution-cards.json           ← Layer 3: feature traces
│   ├── health.json                    ← Health metrics per pillar
│   ├── quest.json                     ← Onboarding quest checklist
│   ├── atlas_data.json                ← Aggregated scan metadata (repo stats, pillar/edge counts)
│   ├── preflight-result.json          ← Pre-flight check output (generated by scripts/preflight.py)
│   └── screenshots/                   ← App screenshots (Playwright or fallback)
│
├── scripts/
│   ├── preflight.py                   ← Pre-flight environment checker
│   ├── capture-screenshots.py         ← Playwright screenshot capture
│   ├── health-check.py                ← Health metrics collector
│   ├── mesh-builder.py                ← Layer 2 import analyzer
│   └── onBob_scanner.py               ← Main repo scanner (generic)
│
└── target-repo/                       ← Clone of tiangolo/full-stack-fastapi-template
```

---

## Bob Prompts (Copy-Paste Ready)

### Demo Run Prompt
```
Run the complete onBob workflow on the target repository:

Step 1: Read the repository structure
Step 2: Confirm pillars.json and execution-cards.json exist in onbob-output/
Step 3: Open onbob-output/architecture-atlas.html in the default browser using Bob Shell:
  python -m http.server 3000 --directory onbob-output
Step 4: Print a summary of what was generated:
  - Number of architectural pillars mapped
  - Number of execution traces captured
  - Estimated time for a developer to understand this architecture manually vs. with onBob
```

---

## Hackathon Evidence

Screenshots of Bob sessions are required and stored in `.bob/evidence/`:
- `layer1-bob-session.png` — Layer 1 scan completion
- `layer3-bob-session.png` — Layer 3 trace completion
- `demo-bob-session.png` — Full demo run

---

## Business Impact

| Metric | Without onBob | With onBob |
|--------|--------------|------------|
| Time to first PR | 14 days | 3 days |
| Architecture comprehension | 2 weeks reading | 4 minutes |
| Documentation freshness | Manually maintained | Auto-regenerated |
| Tool setup required | Confluence + Notion + Slack | Zero |
| Bob Coins consumed | — | ~15 coins |

---

## Tech Stack

- **IBM Bob 2.0** — Agent runtime (scan, trace, shell execution)
- **Python 3.8+** — Scanner scripts
- **Playwright** — Optional screenshot capture
- **Vanilla HTML/CSS/JS** — Zero-dependency atlas viewer
- **Target**: FastAPI (Python) + React (TypeScript) + PostgreSQL

---

*Built for the IBM Bob 2.0 Hackathon · Powered by IBM Bob*
