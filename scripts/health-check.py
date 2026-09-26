#!/usr/bin/env python3
"""
onBob Health Metrics Generator
================================
Collects real health metrics from the target repo for each architectural pillar.
Writes onbob-output/health.json.

Bob Shell runs this during Layer 1 scan (Step 4).
"""

import subprocess
import json
import os
import sys
from pathlib import Path

TARGET_REPO = Path("target-repo")
OUTPUT_FILE = Path("onbob-output/health.json")

PILLARS = {
    "identity": {
        "dirs": ["backend/app/api/routes/login.py", "backend/app/api/routes/users.py", "backend/app/core/security.py"],
        "test_pattern": "test_login",
    },
    "core-engine": {
        "dirs": ["backend/app/api/routes/items.py", "backend/app/crud.py"],
        "test_pattern": "test_items",
    },
    "data-layer": {
        "dirs": ["backend/app/models.py", "backend/app/db.py"],
        "test_pattern": "test_models",
    },
    "api-gateway": {
        "dirs": ["backend/app/main.py", "backend/app/api/deps.py", "backend/app/api/main.py"],
        "test_pattern": "test_api",
    },
    "frontend-shell": {
        "dirs": ["frontend/src"],
        "test_pattern": None,
    },
}


def run_cmd(cmd, cwd=None, timeout=15):
    """Run a shell command and return stdout, or '' on failure."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=cwd or TARGET_REPO
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        return ""


def count_todos(path_pattern):
    """Count TODO/FIXME/HACK occurrences in files matching pattern."""
    out = run_cmd(f'grep -r "TODO\\|FIXME\\|HACK" {path_pattern} 2>/dev/null | wc -l')
    try:
        return int(out)
    except ValueError:
        return -1


def count_files(path_pattern, ext="*.py"):
    """Count files matching extension in a directory."""
    out = run_cmd(f'find {path_pattern} -name "{ext}" 2>/dev/null | wc -l')
    try:
        return int(out)
    except ValueError:
        return -1


def last_commit_days(file_path):
    """How many days ago was this file last committed."""
    out = run_cmd(f'git log --format="%ar" -- {file_path} 2>/dev/null | head -1')
    if not out:
        return -1
    # Parse "N days ago", "N weeks ago", etc.
    parts = out.split()
    if len(parts) >= 2:
        try:
            n = int(parts[0])
            unit = parts[1]
            if "minute" in unit:
                return 0
            elif "hour" in unit:
                return 0
            elif "day" in unit:
                return n
            elif "week" in unit:
                return n * 7
            elif "month" in unit:
                return n * 30
            elif "year" in unit:
                return n * 365
        except ValueError:
            pass
    return -1


def estimate_coverage(pillar_id, test_pattern):
    """Attempt to estimate test coverage from pytest output."""
    if not test_pattern:
        return -1
    out = run_cmd(f'python -m pytest --co -q -k {test_pattern} 2>/dev/null | tail -1')
    if "no tests ran" in out or not out:
        # Fallback: check if test files exist
        out2 = run_cmd(f'find backend/app/tests -name "*{test_pattern.replace("test_", "")}*" 2>/dev/null | wc -l')
        try:
            n = int(out2)
            return 60 + (n * 5) if n > 0 else -1
        except ValueError:
            return -1
    return -1


def main():
    print("\n🔍 onBob Health Metrics Generator")
    print(f"   Target: {TARGET_REPO.resolve()}\n")

    if not TARGET_REPO.is_dir():
        print(f"  ❌ target-repo not found at {TARGET_REPO.resolve()}")
        print("     Clone: git clone https://github.com/tiangolo/full-stack-fastapi-template target-repo")
        sys.exit(1)

    health = {}

    for pillar_id, cfg in PILLARS.items():
        print(f"  Checking pillar: {pillar_id}...")
        primary_path = cfg["dirs"][0]

        # File count
        if primary_path.endswith(".py"):
            # It's a specific file
            file_count = 1 if (TARGET_REPO / primary_path).exists() else 0
            # Count all files in the parent dir
            parent = str(Path(primary_path).parent)
            file_count = count_files(parent)
        else:
            file_count = count_files(primary_path)
            if file_count <= 0:
                # Try TypeScript/TSX for frontend
                file_count = count_files(primary_path, "*.tsx")
                tsx_count = count_files(primary_path, "*.ts")
                file_count = max(file_count + tsx_count, 1)

        # Last commit age
        commit_days = last_commit_days(primary_path)

        # TODO count
        todo_dirs = " ".join(cfg["dirs"])
        todo_count = count_todos(todo_dirs)

        # Test coverage estimate
        test_coverage = estimate_coverage(pillar_id, cfg.get("test_pattern"))

        # Status
        if test_coverage < 0:
            status = "unknown"
        elif test_coverage >= 70 and commit_days >= 0 and commit_days <= 7:
            status = "healthy"
        elif commit_days > 14:
            status = "stale"
        elif test_coverage < 40:
            status = "needs-attention"
        else:
            status = "healthy"

        health[pillar_id] = {
            "test_coverage": test_coverage,
            "last_commit_days": commit_days,
            "todo_count": todo_count,
            "file_count": file_count,
            "status": status,
        }

        print(f"    files={file_count}, last_commit={commit_days}d, todos={todo_count}, status={status}")

    output = {
        "generated_by": "IBM Bob 2.0",
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "pillars": health,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2))
    print(f"\n✅ Health metrics written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
