#!/usr/bin/env python3
"""
onBob Layer 2 — Mesh Builder
==============================
Reads pillars.json and the target repo's source files to discover
cross-pillar import/call relationships, then writes edges.json.

Bob Shell runs this during Layer 2 mesh analysis.
"""

import json
import re
import subprocess
from pathlib import Path

TARGET_REPO = Path("target-repo")
PILLARS_FILE = Path("onbob-output/pillars.json")
EDGES_OUTPUT = Path("onbob-output/edges.json")

# Color scheme for edge types
EDGE_COLORS = {
    "http": "#3B82F6",      # blue — animated
    "database": "#10B981",  # green — static
    "auth": "#8B5CF6",      # purple — animated
    "import": "#F59E0B",    # amber — static
}


def run_grep(pattern, path, flags="rn"):
    """Run grep and return list of matching lines."""
    cmd = f"grep -{flags} '{pattern}' {path} 2>/dev/null | head -20"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                timeout=10, cwd=TARGET_REPO)
        return [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    except Exception:
        return []


def detect_edges(pillars):
    """Discover edges by grepping for cross-pillar import patterns."""
    edges = []
    edge_id = 0

    def make_edge(src, tgt, protocol, label, edge_type):
        nonlocal edge_id
        edge_id += 1
        return {
            "id": f"edge_{src.replace('-', '_')}_to_{tgt.replace('-', '_')}_{edge_id}",
            "source": src,
            "target": tgt,
            "protocol": protocol,
            "label": label,
            "color": EDGE_COLORS.get(edge_type, "#94a3b8"),
            "animated": edge_type in ("http", "auth"),
            "type": edge_type,
        }

    # Check frontend → api-gateway (HTTP)
    frontend_api_calls = run_grep("/api/v1", "frontend/src/")
    if frontend_api_calls:
        edges.append(make_edge("frontend-shell", "api-gateway",
                               "REST", "HTTP requests via OpenAPI client", "http"))

    # Check api-gateway → identity (auth routing)
    login_imports = run_grep("from app.api.routes.login import", "backend/app/api/")
    login_includes = run_grep("router.include_router", "backend/app/api/main.py")
    if login_imports or login_includes:
        edges.append(make_edge("api-gateway", "identity",
                               "REST", "POST /api/v1/login/access-token", "http"))

    # Check api-gateway → core-engine
    items_imports = run_grep("from app.api.routes.items import", "backend/app/api/")
    items_includes = run_grep("items", "backend/app/api/main.py")
    if items_imports or items_includes:
        edges.append(make_edge("api-gateway", "core-engine",
                               "REST", "GET/POST /api/v1/items/", "http"))

    # Check identity → data-layer (DB queries)
    security_db = run_grep("from app.crud import", "backend/app/api/routes/login.py")
    security_models = run_grep("from app.models import", "backend/app/core/security.py")
    if security_db or security_models:
        edges.append(make_edge("identity", "data-layer",
                               "SQLModel", "SELECT users WHERE email = ?", "database"))

    # Check core-engine → data-layer (DB queries)
    crud_db = run_grep("from app.models import", "backend/app/crud.py")
    items_crud = run_grep("from app.crud import", "backend/app/api/routes/items.py")
    if crud_db or items_crud:
        edges.append(make_edge("core-engine", "data-layer",
                               "SQLModel", "SELECT items WHERE owner_id = ?", "database"))

    # Check auth dependency injection
    deps_auth = run_grep("from app.core.security import", "backend/app/api/deps.py")
    if deps_auth:
        edges.append(make_edge("api-gateway", "identity",
                               "DI", "get_current_user() via deps.py", "auth"))

    # Deduplicate by source+target
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["source"], e["target"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return unique_edges[:8]  # MAX 8 edges per spec


def build_features_menu():
    """Build the features menu for Layer 3 CTA."""
    return [
        {
            "id": "auth_login",
            "label": "🔐 User Authentication",
            "description": "JWT login flow — POST /api/v1/login/access-token",
            "pillar_id": "identity",
            "exec_card_id": "auth_login",
        },
        {
            "id": "items_list",
            "label": "📦 List Items",
            "description": "Paginated items — GET /api/v1/items/",
            "pillar_id": "core-engine",
            "exec_card_id": "items_list",
        },
        {
            "id": "user_me",
            "label": "👤 Get Current User",
            "description": "Profile from JWT — GET /api/v1/users/me",
            "pillar_id": "identity",
            "exec_card_id": "user_me",
        },
    ]


def main():
    print("\n🕸️  onBob Layer 2 — Mesh Builder")
    print(f"   Target repo: {TARGET_REPO.resolve()}\n")

    if not PILLARS_FILE.exists():
        print(f"  ❌ {PILLARS_FILE} not found — run Layer 1 scan first")
        return

    data = json.loads(PILLARS_FILE.read_text())
    pillars = data.get("pillars", [])
    print(f"  Loaded {len(pillars)} pillars from pillars.json")

    if not TARGET_REPO.is_dir():
        print(f"  ⚠️  target-repo not found — using pre-seeded edges")
        edges = []
    else:
        print("  Scanning for cross-pillar connections...")
        edges = detect_edges(pillars)

    # Fall back to pre-seeded edges if none detected
    if not edges:
        print("  ℹ️  No live edges detected — loading pre-seeded edges")
        if EDGES_OUTPUT.exists():
            existing = json.loads(EDGES_OUTPUT.read_text())
            edges = existing.get("edges", [])
        else:
            print("  ❌ No pre-seeded edges.json found either")
            edges = []

    print(f"  Found {len(edges)} inter-pillar connections")

    output = {
        "generated_by": "IBM Bob 2.0",
        "target_repo": "tiangolo/full-stack-fastapi-template",
        "edges": edges,
        "features_menu": build_features_menu(),
    }

    EDGES_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    EDGES_OUTPUT.write_text(json.dumps(output, indent=2))
    print(f"\n✅ edges.json written to {EDGES_OUTPUT}")

    # Print Layer 3 CTA
    print("\n" + "─" * 50)
    print("✅ onBob Layer 2 Complete — Mesh mapped.")
    print(f"\nFound {len(edges)} connections between {len(pillars)} architectural pillars.")
    print("""
🔍 LAYER 3 READY — Which feature would you like to explore in-depth?

  1. 🔐 User Authentication — POST /api/v1/login/access-token
     Traces: Route Handler → Password Check → JWT Sign → Response

  2. 📦 List Items — GET /api/v1/items/
     Traces: Auth Middleware → Route Handler → DB Query → Pagination

  3. 👤 Get Current User — GET /api/v1/users/me
     Traces: JWT Decode → Dependency Injection → User Model

Reply with the NUMBER of the feature to run a live execution trace.
""")


if __name__ == "__main__":
    main()
