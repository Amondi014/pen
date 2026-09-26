#!/usr/bin/env python3
"""
onBob Pre-flight Checker
========================
Run FIRST before any Bob scan to verify the environment is ready.
Executed by Bob Shell as Step 0 of the scan workflow.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

REQUIRED_DIRS = [
    "target-repo",
    "onbob-output",
    "scripts",
]

def check(label, ok, detail=""):
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status}  {label}", f"-- {detail}" if detail else "")
    return ok

def main():
    print("\n============================================")
    print("  onBob Pre-Flight Checker")
    print("  IBM Bob 2.0 Hackathon")
    print("============================================\n")

    results = {}

    # 1. Python version
    py_ok = sys.version_info >= (3, 8)
    results["python"] = check("Python 3.8+", py_ok, sys.version.split()[0])

    # 2. Required directories
    for d in REQUIRED_DIRS:
        exists = Path(d).is_dir()
        results[f"dir_{d}"] = check(f"Directory: {d}/", exists, "found" if exists else "MISSING -- create it")

    # 3. onbob-output writable
    out_dir = Path("onbob-output")
    out_dir.mkdir(exist_ok=True)
    writable = os.access(out_dir, os.W_OK)
    results["output_writable"] = check("onbob-output/ is writable", writable)

    # 4. target-repo has key files
    target = Path("target-repo")
    if target.is_dir():
        has_main = (target / "backend/app/main.py").exists()
        has_compose = any((target / f).exists() for f in ["docker-compose.yml", "docker-compose.yaml"])
        results["target_main"] = check("target-repo/backend/app/main.py", has_main,
                                       "FastAPI entry point found" if has_main else "Not found -- wrong repo?")
        results["target_compose"] = check("target-repo/docker-compose.yml", has_compose,
                                          "Docker Compose found" if has_compose else "Not found")
    else:
        print("  [WARN] target-repo/ not found -- clone tiangolo/full-stack-fastapi-template first")
        print("         git clone https://github.com/tiangolo/full-stack-fastapi-template target-repo")

    # 5. Check if app is running (optional)
    app_running = False
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:8000/docs", timeout=2)
        app_running = True
    except Exception:
        pass
    results["app_running"] = check("FastAPI app running at :8000", app_running,
                                   "Live traces available" if app_running else
                                   "Not running -- Layer 3 will use pre-captured data")

    # 6. curl available
    try:
        subprocess.run(["curl", "--version"], capture_output=True, timeout=5)
        curl_ok = True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        curl_ok = False
    results["curl"] = check("curl available", curl_ok, "required for Layer 3 traces")

    # 7. Playwright (optional for screenshots)
    try:
        import playwright  # noqa: F401
        pw_ok = True
    except ImportError:
        pw_ok = False
    results["playwright"] = check("playwright available (optional)", pw_ok,
                                  "installed" if pw_ok else "not installed -- screenshot fallback will be used")

    # Summary
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    critical_pass = results.get("python", False) and results.get("output_writable", False)

    print(f"\n{'--' * 22}")
    print(f"  Pre-flight: {passed}/{total} checks passed")
    if critical_pass:
        print("  [OK] Critical checks passed -- Bob can proceed\n")
    else:
        print("  [FAIL] Critical checks failed -- resolve above issues before running Bob\n")
        sys.exit(1)

    # Write result to output dir for Bob to read
    result_file = Path("onbob-output/preflight-result.json")
    result_file.write_text(json.dumps({
        "passed": passed,
        "total": total,
        "critical_pass": critical_pass,
        "app_running": app_running,
        "checks": {k: ("pass" if v else "fail") for k, v in results.items()}
    }, indent=2))
    print(f"  Results written to {result_file}")


if __name__ == "__main__":
    main()
