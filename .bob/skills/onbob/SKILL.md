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
   - Bob copies `onbob-output/architecture-atlas.html` (the template) to the output path.
   - Bob inserts a `<script>` block **before the Architecture Data Engine script tag** that sets `window.__ONBOB_DATA__` to the freshly scanned repo's JSON (see Section 4 for the exact data contract).
   - The resulting file is fully self-contained and renders only the new repo's data — no previous repo data is present.
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
4. **DO NOT** edit `onbob-output/architecture-atlas.html` directly — it is the reusable template.
5. Output generated atlas files ONLY to `onbob-output/` (naming convention: `architecture-atlas.html` for the active run) or a user-designated documentation directory.

---

## 4. Atlas Generation — Data Injection Protocol

The template (`onbob-output/architecture-atlas.html`) contains **no hardcoded repo data**. It reads exclusively from `window.__ONBOB_DATA__`. When generating an atlas for a new repo, Bob **prepends** the following `<script>` block immediately before the `<!-- ─── Repo Data Injection Point -->` comment in the template:

```html
<script>
window.__ONBOB_DATA__ = {
  "org/repo-name": {
    repo_name: "org/repo-name",
    primary_lang: "Python / TypeScript / Go",
    file_count: 142,
    layers: [
      {
        id: "layer_api",
        tag: "API Gateway & Ingress",
        accent: "#38BDF8",
        cards: [
          { id: "pillar-id", name: "Display Name", icon: "🌐", desc: "Short description.", file: "path/to/file.py:12", pillar: "pillar-id" }
        ]
      }
      /* ... 3-5 more layers ... */
    ],
    pillars: [
      {
        id: "pillar-id",
        name: "Pillar Name",
        type: "api" | "logic" | "db" | "ui",
        icon: "🌐",
        mission: "One-sentence mission.",
        onboarding_mental_model: "How a newcomer should think about this pillar.",
        onboarding_invariant: "The one rule this pillar must never break.",
        reading_list: ["path/to/file.py:12"],
        color: "#38BDF8",
        team: "#team_name",
        files: ["path/to/file.py:12"],
        signature: "def entry_function(args)",
        symbols: [
          { name: "function_name()", sig: "def function_name(args) -> ReturnType", file: "path/to/file.py:12", snippet: "# code snippet" }
        ],
        code_snippet: "# representative code block",
        dependents: ["other-pillar-id"]
      }
      /* ... 3-5 total pillars ... */
    ],
    features_menu: [
      {
        id: "feature_id",
        num: "1",
        label: "1. Feature Name",
        color: "#38BDF8",
        arrowMarker: "url(#arrow-cyan)",
        path: ["pillar-id-1", "pillar-id-2", "pillar-id-3"],
        desc: "What this feature does end-to-end.",
        contract: "Input contract ➔ Output contract",
        invariants: "Business rules that must hold.",
        edge_steps: {
          "pillar-id-1->pillar-id-2": { step: 1, call: "① function_call()", desc: "What happens at this edge.", snippet: "code example" }
        }
      }
      /* ... 2-4 total features ... */
    ],
    notes: [
      {
        id: "note_1",
        type: "contract" | "adr" | "invariant",
        title: "Note Title",
        preview: "One-line summary shown on canvas.",
        targetNode: "pillar-id",
        file: "path/to/file.py:12",
        full_text: "Full note text shown in drawer."
      }
    ],
    traces: {
      feature_id: {
        title: "Trace Flow: Feature Name",
        steps: [
          { title: "Step Name", file: "path/to/file.py:12", desc: "What this step does." }
        ]
      }
    },
    blast: {
      "pillar-id": {
        title: "Pillar Name (path/to/file.py:line)",
        risk_score: 85,
        risk_level: "critical" | "high" | "medium",
        direct_breakage: ["Description of direct breakage"],
        downstream_impact: ["Downstream consequence"],
        db_integrity: ["Data integrity risk"],
        safety_tests: "test command to run",
        emergency_contacts: "#team-channel · @oncall-lead"
      }
    }
  }
};
</script>
```

**Key rules:**
- The top-level key of `window.__ONBOB_DATA__` is the repo slug (e.g. `"org/repo-name"`). This becomes the `<select>` option value in the dropdown.
- Every `pillar.id` referenced in `features_menu[].path`, `features_menu[].edge_steps`, `notes[].targetNode`, and `blast` keys must exist in `pillars[]`.
- If multiple repos are being compared, add additional top-level keys — the dropdown will show all of them.
- `layers[]` drive the left Blueprint panel; `pillars[]` drive the right Dependency Mesh graph.

---

## 5. Autonomous Scan Pipeline
To conserve token budget and maximize speed, Bob executes the fast, read-only analysis helper:

```bash
# Run lightweight AST scanner
python scripts/onBob_scanner.py . --feature "$FEATURE_NAME" --out .bob/atlas/atlas_data.json
```

Or Bob constructs the `window.__ONBOB_DATA__` payload inline (see Section 4) by reading manifests, source files, and import graphs directly.

---

## 6. Visual Atlas Rendering
The template file `onbob-output/architecture-atlas.html` contains all CSS, D3 physics, and rendering logic. Bob does not modify the template itself — it only injects `window.__ONBOB_DATA__` into the generated output file.

- Local preview: open the generated `architecture-atlas.html` directly in any modern browser.
- The repo selector dropdown is populated dynamically from the keys of `window.__ONBOB_DATA__` at page load.
- If opened without any injected data (e.g. as a blank template), the page shows a placeholder "example/repo — run /onBob to populate" state.
