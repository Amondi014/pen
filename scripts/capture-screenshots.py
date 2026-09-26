#!/usr/bin/env python3
"""
onBob Screenshot Capture
=========================
Captures screenshots of the running FastAPI + React app using Playwright.
Falls back to pre-built CSS mockup data if Playwright is unavailable or app is offline.

Bob Shell runs this during Layer 1 scan (Step 3).
"""

import sys
import json
import os
from pathlib import Path

OUTPUT_DIR = Path("onbob-output/screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

APP_URL = "http://localhost:5173"  # Vite dev server default
API_URL = "http://localhost:8000"

PAGES = [
    {"name": "dashboard", "path": "/", "wait": 2000},
    {"name": "login", "path": "/login", "wait": 1000},
    {"name": "items", "path": "/items", "wait": 2000},
]


def try_playwright_capture():
    """Attempt to capture real screenshots via Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ⚠️  Playwright not installed — run: pip install playwright && playwright install chromium")
        return False

    print("  📸 Playwright available — capturing live screenshots...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                ignore_https_errors=True
            )
            page = context.new_page()

            # Try login first to get a session
            try:
                page.goto(f"{APP_URL}/login", timeout=5000)
                page.wait_for_load_state("networkidle", timeout=5000)
                page.fill('input[type="email"]', "admin@example.com")
                page.fill('input[type="password"]', "changethis")
                page.click('button[type="submit"]')
                page.wait_for_url("**/", timeout=5000)
                print("  ✅ Logged in successfully")
            except Exception as e:
                print(f"  ⚠️  Login failed: {e} — capturing without auth")

            captured = []
            for pg in PAGES:
                try:
                    page.goto(f"{APP_URL}{pg['path']}", timeout=8000)
                    page.wait_for_timeout(pg["wait"])
                    out_path = OUTPUT_DIR / f"{pg['name']}.png"
                    page.screenshot(path=str(out_path), full_page=False)
                    captured.append(str(out_path))
                    print(f"  ✅ Captured: {out_path}")
                except Exception as e:
                    print(f"  ⚠️  Failed to capture {pg['name']}: {e}")

            browser.close()
            return len(captured) > 0

    except Exception as e:
        print(f"  ❌ Playwright error: {e}")
        return False


def write_fallback_metadata():
    """Write metadata indicating pre-built mockup should be used in the atlas."""
    meta = {
        "mode": "css-mockup",
        "note": "No live screenshots available. The atlas uses CSS-drawn app mockups.",
        "pages": [
            {"name": "dashboard", "description": "FastAPI Template Dashboard — Items list view"},
            {"name": "login", "description": "Login screen — admin@example.com / changethis"}
        ]
    }
    meta_path = OUTPUT_DIR / "screenshot-meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"  ℹ️  Fallback metadata written to {meta_path}")


def main():
    print("\n📸 onBob Screenshot Capture")
    print(f"   Target app: {APP_URL}")
    print(f"   Output dir: {OUTPUT_DIR}\n")

    # Check if app is running
    try:
        import urllib.request
        urllib.request.urlopen(f"{API_URL}/docs", timeout=3)
        app_running = True
        print("  ✅ App is running at", APP_URL)
    except Exception:
        app_running = False
        print("  ⚠️  App not detected at", APP_URL)
        print("       Run: cd target-repo && docker compose up -d")

    if app_running:
        captured = try_playwright_capture()
        if not captured:
            write_fallback_metadata()
    else:
        write_fallback_metadata()

    print("\n✅ Screenshot step complete")
    print(f"   Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
