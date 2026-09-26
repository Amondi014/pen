---
name: onbob
description: Onboarding tool
---

# /onBob — Autonomous Architecture Atlas & Visual Onboarding Skill

> **Skill Name:** `/onBob` *(capital B)*  
> **Author:** onBob Team (IBM Bob 2.0 Challenge)  
> **Execution Mode:** STRICT READ-ONLY (Zero code mutation, zero file modification in user repo)  
> **Target Audience:** Newcomers, open-source contributors, team members onboarding to unfamiliar, dense, or legacy codebases.

---

## 1. Skill Purpose & Core Philosophy
When a developer runs `/onBob` inside IBM Bob, Bob acts as an autonomous architectural cartographer. Without altering a single line of production code, Bob scans the current workspace, categorizes the entire repository into 4–6 Architectural Pillars, maps the dependency mesh, calculates breaking risk (Blast Radius), and renders an interactive, visually stunning Architectural Atlas (`architecture-atlas.html`).

---

## 2. Invocation Syntax & Intelligent Branching

Bob dynamically branches based on the user's prompt:

```bash
# Branch A: Exploratory Architecture Overview
/onBob

# Branch B: Surgical Feature Trace & Blast Radius
/onBob [feature_name_or_keyword]
```

### Branch A: Exploratory Invocation (`/onBob`)
1. **Workspace Scan (Read-Only):**
   - Bob inspects manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.).
   - Bob clusters directories into 4–6 Architectural Pillars (Ingress, Engine, Domain Models, Triggers, Storage/Egress).
   - Bob maps directed dependencies between pillars.
2. **Interactive Atlas Generation:**
   - Bob creates `architecture-atlas.html` in `.bob/atlas/` (or current directory) with the dynamic repository data contract (`window.__ONBOB_DATA__`).
3. **Stage 2 Follow-On Prompt in Chat:**
   - Bob outputs a concise, beautiful ASCII/Markdown summary in chat, followed by the **Stage 2 Interactive Question**:
   > *"I have mapped **[Repo Name]** into 5 core architectural pillars and launched your visual Architectural Atlas!*  
   > *Which feature would you like to explore in-depth?*  
   > 1. [Feature 1: Ingestion & Ingress]*  
   > 2. [Feature 2: Processing & Core Engine]*  
   > 3. [Feature 3: Anomaly & Trigger Detection]*  
   > 4. [Feature 4: State Persistence & Export]*  
   > *Reply with the number or feature name to view its exact execution trace!"*

### Branch B: Surgical Invocation (`/onBob [feature]`)
1. **Targeted Deep-Dive (Bypasses Stage 2 Prompt):**
   - Bob immediately searches for functions, routes, and modules matching `[feature]`.
   - Bob constructs the **3-tier execution flow**:
     - **Tier 1 (Ingress):** Entrypoint function & file line number.
     - **Tier 2 (Logic):** Core transformation/processing function & file line number.
     - **Tier 3 (State):** Persistence/serialization layer & file line number.
2. **Blast Radius Analysis (Big Idea 2):**
   - Bob calculates what breaks if this feature or its underlying function is changed or deleted.
   - Computes: Direct Dependents (Tier 1), Downstream Client Impacts, Data Integrity risks, and Safety Tests.
3. **Generates Atlas & Opens Feature Drawer:**
   - Emits the visual atlas with the feature drawer open and the Blast Radius ready to test.

---

## 3. Strict Read-Only Execution Protocol
Bob MUST adhere to the following safety constraints:
1. **DO NOT** modify, edit, reformat, or delete any source code files.
2. **DO NOT** run mutating git commands (`git checkout -b`, `git commit`, `git push`, `git rebase`).
3. **DO NOT** execute unvetted arbitrary scripts with side effects.
4. Output generated files ONLY to `.bob/atlas/` or user-designated documentation directories.

---

## 4. Autonomous Scan Pipeline (Bob Shell Execution)
To conserve token budget and maximize speed, Bob executes the fast, read-only analysis helper:

```bash
# Run lightweight AST scanner
python scripts/onBob_scanner.py . --feature "$FEATURE_NAME" --out .bob/atlas/atlas_data.json
```

Or Bob constructs the dynamic JSON payload inline using the standard **onBob Data Contract**:
```javascript
window.__ONBOB_DATA__ = {
  repo_name: "repo/name",
  primary_lang: "Python / TypeScript / Go",
  file_count: 142,
  pillars: [ /* 4-6 clustered pillars */ ],
  edges: [ /* directed dependencies between pillars */ ],
  features_menu: [ /* Stage 2 options */ ],
  features: [ /* execution trace cards */ ],
  blast_data: [ /* Big Idea 2 blast radius simulations */ ]
};
```

---

## 5. Visual Atlas Rendering
Bob verifies that `architecture-atlas.html` is up to date and provides the user with the direct preview link:
- Local preview: `architecture-atlas.html`
- Standalone HTML file: Open directly in any modern browser.
