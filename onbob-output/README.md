# onbob-output

This directory contains the generated **Architectural Atlas** produced by the `/onBob` skill.

## Main Deliverable

| File | Description |
|------|-------------|
| `architecture-atlas.html` | ⭐ Self-contained interactive atlas — open directly in any browser |

## How to Regenerate

1. Open IBM Bob with any target repository in your workspace
2. Type `/onBob`
3. Bob scans the repo, builds the data payload, and overwrites `architecture-atlas.html`

No server required. No build step. Just open the HTML file.

## Demo Target

The committed atlas was generated against the [DuckDB](https://github.com/duckdb/duckdb)
C++ monorepo (3,228 source files, 8 architectural pillars, 4 feature flows).

To regenerate against DuckDB:
```bash
git clone --depth=1 https://github.com/duckdb/duckdb
# Then in IBM Bob:
/onBob — target: duckdb/
```
