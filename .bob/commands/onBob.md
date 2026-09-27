---
description: "onBob: Autonomously scan any repository and generate a self-contained Architectural Atlas — interactive HTML force-graph with pillar mesh, animated feature flows, execution traces, blast radius simulator, and keyboard shortcuts."
---

# /onBob — Architectural Atlas Generator

> **IBM Bob 2.0 Hackathon Submission**
> One command. Any codebase. Interactive architecture map in under 5 minutes.

---

## Invocation

```
/onBob                        # Full scan — map entire repo
/onBob — target: path/to/dir  # Scan a specific sub-directory or cloned repo
/onBob [feature keyword]      # Surgical trace — focus on one feature
```

---

## What Bob Does

Bob executes this pipeline **autonomously** and **read-only** using only native file tools.
No shell scripts. No external dependencies.

### Step 1 — Scan
Bob uses `glob`, `grep`, `list_files`, `read_file`, `GetSymbolsOverview`, and `FindSymbol`
to inspect the repository. No more than 200 files are read. Priority order:
1. Manifests / package files (identify language and framework)
2. Entry points (main, app, index, router)
3. Model / schema / migration files
4. Auth / security / middleware
5. Storage / database / ORM files
6. Key API route files

### Step 2 — Build `window.__ONBOB_DATA__`
Bob constructs the full data payload as a `<script>` block.
See `.bob/skills/onBob/SKILL.md` for the complete data contract schema.

### Step 3 — Inject & Write
Bob reads `.bob/template.html`, inserts the `window.__ONBOB_DATA__` script block immediately
**before** the `<!-- ─── Repo Data Injection Point -->` comment, and writes the output to:

```
onbob-output/architecture-atlas.html
```

The master template `.bob/template.html` is **never modified**.

---

## After Generation — Chat Summary

Bob prints this to chat after writing the file:

```
[onBob] Atlas generated → onbob-output/architecture-atlas.html

  Repo     : <repo-name>
  Language : <primary language(s)>
  Files    : <file count>
  Pillars  : N    Edges: N    Features: N

Open onbob-output/architecture-atlas.html in any browser — no server needed.

Which feature would you like to trace in depth?

  1. <Feature 1 label>
  2. <Feature 2 label>
  3. <Feature 3 label>

Reply with a number or /onBob [feature keyword]
```

---

## STRICT CONSTRAINTS

1. **Read-Only** — never modify, delete, or write any file inside the target repo
2. **Never edit `.bob/template.html`** — it is the reusable master template
3. **Output only to `onbob-output/`** — single output file only
4. **Max 200 files read** per scan — prioritise manifests, entrypoints, and router/model/storage files
5. **No shell scripts** — use only Bob native file tools
