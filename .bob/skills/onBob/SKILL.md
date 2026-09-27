---
name: onBob
description: >-
  onBob: Scan any repository and generate a self-contained Architectural Atlas —
  interactive HTML viewer with pillar mesh, execution traces, health badges,
  onboarding quest, and blast radius simulator.
metadata:
  user-invocable: true
  disable-model-invocation: true
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

When `/onBob` is triggered, Bob executes the following pipeline **autonomously** and **read-only**:

### Step 1 — Scan the workspace

Bob inspects the repository by reading manifests, source files, and import graphs directly using
native file tools (`read_file`, `grep`, `glob`, `list_files`). No external scripts are run.

Bob clusters the codebase into **4–6 Architectural Pillars** and maps the directed dependency
graph between them.

### Step 2 — Build `window.__ONBOB_DATA__`

Bob constructs the full data payload inline (see **Data Contract** below) as a `<script>` block:

```html
<script>
window.__ONBOB_DATA__ = {
  "org/repo-name": { /* pillars, layers, features, traces, blast, notes */ }
};
</script>
```

### Step 3 — Generate the Atlas

Bob reads the template at **`.bob/template.html`**, copies it to
`onbob-output/architecture-atlas.html`, and inserts the `window.__ONBOB_DATA__` script block
immediately **before** the `<!-- ─── Repo Data Injection Point -->` comment in the template.

The result is a fully self-contained, zero-dependency HTML file — open it directly in any
browser, no HTTP server required.

```
onbob-output/architecture-atlas.html   ← open this in a browser
```

---

## STRICT CONSTRAINTS

1. **Read-Only** — never modify, delete, or commit any file in the target repo
2. **Do not edit `.bob/template.html`** — it is the reusable master template; always write output to `onbob-output/`
3. **Output only to `onbob-output/`** — never write inside the target repo itself
4. **Max 200 files read** per scan — prioritise manifests, entrypoints, and router/model/storage files

---

## Data Contract — `window.__ONBOB_DATA__`

The top-level key is the repo slug (e.g. `"org/repo-name"`). The full shape:

```js
window.__ONBOB_DATA__ = {
  "org/repo-name": {
    repo_name: "org/repo-name",
    primary_lang: "Python / TypeScript",
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
      /* 3–5 layers total */
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
      /* 4–6 pillars total */
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
      /* 2–4 features total */
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
```

**Key rules:**
- Every `pillar.id` referenced in `features_menu[].path`, `edge_steps` keys, `notes[].targetNode`, and `blast` keys **must** exist in `pillars[]`.
- `layers[]` drive the left Blueprint panel; `pillars[]` drive the right Dependency Mesh graph.
- The arrowMarker values map to SVG marker IDs already defined in the template: `url(#arrow-cyan)`, `url(#arrow-violet)`, `url(#arrow-emerald)`, `url(#arrow-amber)`, `url(#arrow-rose)`.

---

## Stage 2 CTA — "Which Feature?"

After the atlas is written, Bob prints this summary in chat:

```
[onBob] Atlas generated → onbob-output/architecture-atlas.html

  Repo    : <repo-name>
  Stack   : <primary languages>
  Pillars : N     Edges: N     Features: N

Which feature would you like to trace in depth?

  1. <Feature 1 label>
  2. <Feature 2 label>
  3. <Feature 3 label>

Reply with a number or /onBob [feature keyword]
```

---

## Layer 3 — Feature Trace (Branch B / Surgical)

```
/onBob auth
```

Bob scans for functions, routes, and modules matching the keyword, constructs the 3-tier execution
flow (Ingress → Logic → State), computes Blast Radius, and regenerates the atlas with the matching
feature trace active. The chat output includes exact `file:line` references for each step.

---

## Output

| File | Description |
|------|-------------|
| `onbob-output/architecture-atlas.html` | Self-contained interactive atlas — open in any browser |

The template **`.bob/template.html`** is never modified. It is always the read-only source.
