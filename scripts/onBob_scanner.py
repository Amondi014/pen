#!/usr/bin/env python3
"""
onBob — Universal Repository Scanner
=====================================
Scans ANY repository, zero hardcoded assumptions, zero mutations.

Usage:
    python scripts/onBob_scanner.py <repo_path> [--out <output_dir>] [--feature <name>]

Output (written to <output_dir>/atlas_data.json):
    A single self-contained JSON file the atlas viewer reads directly.
    Schema: { meta, pillars, edges, features_menu, features, health, blast_data, quest }
"""

import os
import re
import sys
import json
import subprocess
import argparse
from pathlib import Path
from collections import defaultdict

# ── Constants ────────────────────────────────────────────────────────────────

SKIP_DIRS = {
    '.git', '.svn', '.hg', 'node_modules', '__pycache__', '.venv', 'venv',
    '.env', 'env', 'dist', 'build', '.next', '.nuxt', 'target', 'bin', 'obj',
    '.idea', '.vscode', '.mypy_cache', '.pytest_cache', 'coverage', '.cache',
    'vendor', 'third_party', 'bower_components',
}
SKIP_EXTS = {
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib', '.exe',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.woff', '.woff2', '.ttf', '.eot',
    '.zip', '.tar', '.gz', '.7z', '.pdf', '.lock', '.sum',
    '.min.js', '.min.css', '.map',
}
PALETTE = [
    '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899',
    '#06B6D4', '#84CC16', '#F97316', '#EF4444', '#A855F7',
]
RGB_MAP = {
    '#3B82F6': '59,130,246',  '#10B981': '16,185,129',  '#8B5CF6': '139,92,246',
    '#F59E0B': '245,158,11',  '#EC4899': '236,72,153',  '#06B6D4': '6,182,212',
    '#84CC16': '132,204,22',  '#F97316': '249,115,22',  '#EF4444': '239,68,68',
    '#A855F7': '168,85,247',
}

# ── Pillar role definitions (keyword → role) ─────────────────────────────────

ROLE_DEFS = [
    {
        'id': 'ingress',
        'name': 'Ingress & API',
        'icon': '🌐',
        'keywords': ['api', 'route', 'router', 'controller', 'handler', 'endpoint',
                     'cli', 'cmd', 'command', 'http', 'grpc', 'graphql', 'rest',
                     'server', 'app', 'main', 'entry', 'web', 'gateway', 'proxy'],
        'mission': 'Handles all inbound requests, protocol routing, and entrypoint dispatch.',
        'team': '#team-backend',
    },
    {
        'id': 'auth',
        'name': 'Auth & Identity',
        'icon': '🔐',
        'keywords': ['auth', 'authz', 'authn', 'login', 'logout', 'token', 'jwt',
                     'oauth', 'session', 'permission', 'role', 'security', 'password',
                     'credential', 'identity', 'user', 'account', 'signup', 'register'],
        'mission': 'Manages authentication, authorization, tokens, and user identity.',
        'team': '#team-security',
    },
    {
        'id': 'core',
        'name': 'Core Engine',
        'icon': '⚙️',
        'keywords': ['service', 'logic', 'business', 'engine', 'process', 'pipeline',
                     'compute', 'calculate', 'transform', 'workflow', 'job', 'task',
                     'worker', 'queue', 'crud', 'domain', 'feature', 'use_case'],
        'mission': 'Orchestrates business logic, domain rules, and processing pipelines.',
        'team': '#team-backend',
    },
    {
        'id': 'data',
        'name': 'Data & Storage',
        'icon': '🗄️',
        'keywords': ['model', 'schema', 'db', 'database', 'repo', 'repository', 'store',
                     'migration', 'alembic', 'prisma', 'orm', 'sql', 'mongo', 'redis',
                     'cache', 'entity', 'record', 'table', 'collection', 'persist'],
        'mission': 'Owns all database models, migrations, queries, and persistence logic.',
        'team': '#team-platform',
    },
    {
        'id': 'frontend',
        'name': 'Frontend',
        'icon': '🖥️',
        'keywords': ['component', 'page', 'view', 'screen', 'ui', 'frontend', 'client',
                     'react', 'vue', 'angular', 'svelte', 'template', 'layout',
                     'hook', 'store', 'context', 'redux', 'pinia', 'tsx', 'jsx'],
        'mission': 'Delivers the user interface, client-side state, and API client integration.',
        'team': '#team-frontend',
    },
    {
        'id': 'infra',
        'name': 'Infra & Config',
        'icon': '🏗️',
        'keywords': ['config', 'setting', 'env', 'deploy', 'docker', 'k8s', 'helm',
                     'terraform', 'ci', 'cd', 'pipeline', 'makefile', 'script',
                     'util', 'helper', 'common', 'shared', 'lib', 'middleware'],
        'mission': 'Provides shared utilities, configuration, and deployment infrastructure.',
        'team': '#team-platform',
    },
]

# ── File walker ──────────────────────────────────────────────────────────────

def walk_repo(root: Path) -> list[Path]:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in SKIP_EXTS or fname.startswith('.'):
                continue
            files.append(Path(dirpath) / fname)
    return files

# ── Project detection ────────────────────────────────────────────────────────

def detect_project(root: Path, files: list[Path]) -> dict:
    names = {f.name for f in files}
    rel_paths = [str(f.relative_to(root)).replace('\\', '/') for f in files]

    # Language detection by extension count
    ext_counts = defaultdict(int)
    for f in files:
        ext_counts[f.suffix.lower()] += 1

    lang_map = {
        '.py': 'Python', '.ts': 'TypeScript', '.tsx': 'TypeScript',
        '.js': 'JavaScript', '.jsx': 'JavaScript', '.go': 'Go',
        '.rs': 'Rust', '.java': 'Java', '.kt': 'Kotlin', '.rb': 'Ruby',
        '.php': 'PHP', '.cs': 'C#', '.cpp': 'C++', '.c': 'C',
        '.swift': 'Swift', '.dart': 'Dart', '.ex': 'Elixir', '.hs': 'Haskell',
    }
    lang_scores = defaultdict(int)
    for ext, count in ext_counts.items():
        if ext in lang_map:
            lang_scores[lang_map[ext]] += count
    primary_lang = max(lang_scores, key=lang_scores.get) if lang_scores else 'Unknown'
    all_langs = [k for k, _ in sorted(lang_scores.items(), key=lambda x: -x[1])][:3]

    # Framework / stack detection
    frameworks = []
    manifest_hints = {
        'pyproject.toml': 'Python Package', 'setup.py': 'Python Package',
        'package.json': 'Node.js', 'go.mod': 'Go Module',
        'Cargo.toml': 'Rust Crate', 'pom.xml': 'Maven (Java)',
        'build.gradle': 'Gradle (JVM)', 'composer.json': 'PHP (Composer)',
        'Gemfile': 'Ruby',
    }
    for mf, label in manifest_hints.items():
        if mf in names:
            frameworks.append(label)
            break

    # Deep framework hints from file content samples
    framework_patterns = {
        'FastAPI': ['from fastapi', 'FastAPI()', 'APIRouter'],
        'Django': ['from django', 'django.db', 'urlpatterns'],
        'Flask': ['from flask', 'Flask(__name__)', '@app.route'],
        'Express': ["require('express')", 'express()', 'app.listen'],
        'Next.js': ['next/router', 'getServerSideProps', 'next/app'],
        'React': ['from react', 'useState', 'useEffect', 'ReactDOM'],
        'Vue': ['createApp', 'defineComponent', '.vue'],
        'Spring': ['@SpringBootApplication', '@RestController', 'SpringApplication'],
        'Rails': ['ActiveRecord', 'ActionController', 'Rails.application'],
        'Gin': ['"github.com/gin-gonic/gin"', 'gin.Default()'],
        'Fiber': ['"github.com/gofiber/fiber"', 'fiber.New()'],
        'Axum': ['use axum', 'Router::new()', 'axum::'],
    }
    sample_content = ''
    for f in files[:60]:  # sample first 60 files
        try:
            sample_content += f.read_text(encoding='utf-8', errors='ignore')[:300]
        except Exception:
            pass

    detected_fw = []
    for fw, patterns in framework_patterns.items():
        if any(p in sample_content for p in patterns):
            detected_fw.append(fw)

    stack_label = ' · '.join(detected_fw[:3]) if detected_fw else (frameworks[0] if frameworks else primary_lang)

    # Entrypoint detection
    entrypoint_candidates = ['main.py', 'app.py', 'server.py', 'index.py',
                              'main.go', 'main.ts', 'index.ts', 'server.ts',
                              'index.js', 'server.js', 'app.js',
                              'main.rs', 'main.rb', 'main.java']
    entrypoint = next((p for p in rel_paths if Path(p).name in entrypoint_candidates), None)
    if not entrypoint:
        # fallback: shortest path that looks like an entrypoint
        candidates = [p for p in rel_paths if any(k in p.lower() for k in ['main', 'app', 'server', 'index'])]
        entrypoint = min(candidates, key=len) if candidates else (rel_paths[0] if rel_paths else 'unknown')

    # Database detection
    db_hints = {
        'PostgreSQL': ['postgresql', 'psycopg', 'asyncpg', 'pg'],
        'MySQL': ['mysql', 'mysqlclient', 'pymysql'],
        'SQLite': ['sqlite'],
        'MongoDB': ['mongodb', 'pymongo', 'mongoose'],
        'Redis': ['redis'],
        'DynamoDB': ['dynamodb', 'boto3'],
    }
    db_used = [db for db, hints in db_hints.items() if any(h in sample_content.lower() for h in hints)]

    return {
        'repo_name': root.name,
        'primary_lang': primary_lang,
        'all_langs': all_langs,
        'stack': stack_label,
        'frameworks': detected_fw,
        'file_count': len(files),
        'entrypoint': entrypoint,
        'databases': db_used,
    }

# Structural directory names that appear in many repos but don't signal a pillar
_STRUCTURAL_DIRS = {'app', 'src', 'lib', 'pkg', 'internal', 'main', 'server',
                    'backend', 'frontend', 'api', 'tests', 'test', 'core', 'base'}

# ── Pillar clustering ────────────────────────────────────────────────────────

def cluster_pillars(root: Path, files: list[Path]) -> list[dict]:
    rel_files = [f.relative_to(root) for f in files]

    # Score each file against each role
    role_files = defaultdict(list)
    unmatched = []

    for rf in rel_files:
        path_str = str(rf).lower().replace('\\', '/')
        all_parts = path_str.replace('.', '/').split('/')
        # Filename stem gets double weight; structural dirs get 0 weight
        fname_stem = rf.stem.lower()  # e.g. "security", "login", "crud"
        dir_parts = [p for p in all_parts[:-1] if p not in _STRUCTURAL_DIRS and len(p) > 1]
        scored_parts = dir_parts + [fname_stem, fname_stem]  # filename counted twice

        best_role = None
        best_score = 0
        for role in ROLE_DEFS:
            score = sum(1 for k in role['keywords'] if any(k in p for p in scored_parts))
            if score > best_score:
                best_score = score
                best_role = role['id']
        if best_role and best_score > 0:
            role_files[best_role].append(str(rf).replace('\\', '/'))
        else:
            unmatched.append(str(rf).replace('\\', '/'))

    # Build pillar list — only emit roles that matched files
    pillars = []
    color_idx = 0
    used_role_ids = set()

    for role in ROLE_DEFS:
        matched = role_files.get(role['id'], [])
        if not matched:
            continue
        color = PALETTE[color_idx % len(PALETTE)]
        pillars.append({
            'id': role['id'],
            'name': role['name'],
            'icon': role['icon'],
            'mission': role['mission'],
            'team': role['team'],
            'color': color,
            'rgb': RGB_MAP.get(color, '59,130,246'),
            'files': sorted(matched)[:6],       # top 6 most representative
            'all_files': sorted(matched),
            'depends_on': [],
            'dependents': [],
        })
        used_role_ids.add(role['id'])
        color_idx += 1

    # If nothing matched at all — create one catch-all pillar
    if not pillars:
        all_rel = [str(rf).replace('\\', '/') for rf in rel_files]
        pillars.append({
            'id': 'codebase', 'name': root.name, 'icon': '📁',
            'mission': 'Full codebase — run a deeper scan for pillar breakdown.',
            'team': '#team-all', 'color': PALETTE[0], 'rgb': RGB_MAP[PALETTE[0]],
            'files': all_rel[:6], 'all_files': all_rel,
            'depends_on': [], 'dependents': [],
        })
        return pillars

    # Infer dependency edges from import analysis
    _infer_pillar_deps(root, pillars)

    return pillars

# ── Import-based edge detection ──────────────────────────────────────────────

def _infer_pillar_deps(root: Path, pillars: list[dict]):
    """Read a sample of source files to detect cross-pillar imports."""
    # Build a map: file → pillar_id
    file_to_pillar = {}
    for p in pillars:
        for f in p['all_files']:
            file_to_pillar[f] = p['id']

    import_re = re.compile(
        r'(?:^|\n)\s*(?:import|from|require|use|include)\s+["\']?([^\s"\';\n{(]+)',
        re.MULTILINE
    )

    dep_edges = defaultdict(set)  # (src_pillar, dst_pillar)

    for pillar in pillars:
        for fpath in pillar['all_files'][:8]:  # limit per pillar to keep it fast
            full = root / fpath
            try:
                content = full.read_text(encoding='utf-8', errors='ignore')[:3000]
            except Exception:
                continue
            for m in import_re.finditer(content):
                token = m.group(1).lower().replace('\\', '/').strip('./')
                # Find which pillar this import token maps to
                for other in pillars:
                    if other['id'] == pillar['id']:
                        continue
                    # Match if any keyword of the other pillar appears in the import token
                    role_def = next((r for r in ROLE_DEFS if r['id'] == other['id']), None)
                    if role_def and any(k in token for k in role_def['keywords'][:5]):
                        dep_edges[(pillar['id'], other['id'])].add(token)

    # Write back into pillars
    pid_to_pillar = {p['id']: p for p in pillars}
    for (src, dst) in dep_edges:
        sp = pid_to_pillar.get(src)
        dp = pid_to_pillar.get(dst)
        if sp and dp:
            if dst not in sp['depends_on']:
                sp['depends_on'].append(dst)
            if src not in dp['dependents']:
                dp['dependents'].append(src)

# ── Edge (mesh) generation ────────────────────────────────────────────────────

def build_edges(pillars: list[dict]) -> list[dict]:
    edges = []
    eid = 0
    pid_map = {p['id']: p for p in pillars}

    for p in pillars:
        for dep_id in p['depends_on']:
            dep = pid_map.get(dep_id)
            if not dep:
                continue
            eid += 1
            # Guess protocol from pillar roles
            is_db = dep['id'] in ('data', 'storage')
            is_auth = dep['id'] in ('auth', 'identity')
            edges.append({
                'id': f'edge_{eid}',
                'source': p['id'],
                'target': dep_id,
                'protocol': 'SQLModel/ORM' if is_db else ('JWT/OAuth2' if is_auth else 'Internal Call'),
                'label': f"{p['name']} → {dep['name']}",
                'color': '#10B981' if is_db else ('#8B5CF6' if is_auth else '#3B82F6'),
                'animated': not is_db,
                'type': 'database' if is_db else ('auth' if is_auth else 'http'),
            })

    return edges

# ── Features menu ─────────────────────────────────────────────────────────────

def build_features_menu(pillars: list[dict], project: dict) -> list[dict]:
    """Generate a features menu dynamically from pillar roles present."""
    feature_templates = {
        'auth':     {'icon': '🔐', 'label': 'Authentication Flow',   'desc': 'Trace login → token issue → session validation.'},
        'ingress':  {'icon': '🌐', 'label': 'Request Lifecycle',      'desc': 'Trace inbound request → routing → response dispatch.'},
        'core':     {'icon': '⚙️',  'label': 'Core Business Logic',    'desc': 'Trace domain logic → data transformation → result.'},
        'data':     {'icon': '🗄️', 'label': 'Data Persistence Layer', 'desc': 'Trace query → ORM model → database write → response.'},
        'frontend': {'icon': '🖥️', 'label': 'Client Data Fetch',      'desc': 'Trace UI action → API call → state update → render.'},
        'infra':    {'icon': '🏗️', 'label': 'Infrastructure Setup',   'desc': 'Trace config load → middleware → app bootstrap.'},
    }
    menu = []
    for i, p in enumerate(pillars):
        tmpl = feature_templates.get(p['id'], {
            'icon': p['icon'],
            'label': f"{p['name']} Feature",
            'desc': p['mission'],
        })
        menu.append({
            'id': f"feat_{p['id']}",
            'num': str(i + 1),
            'label': f"{tmpl['icon']} {tmpl['label']}",
            'desc': tmpl['desc'],
            'pillar_id': p['id'],
        })
    return menu

# ── Execution trace generation ────────────────────────────────────────────────

def build_execution_traces(root: Path, pillars: list[dict], project: dict) -> list[dict]:
    """Build one execution trace card per pillar — using real file paths."""
    traces = []
    for p in pillars:
        steps = []
        for i, fpath in enumerate(p['files'][:4]):
            full = root / fpath
            # Try to find a real function name in the file
            fn_name = _extract_first_function(full)
            steps.append({
                'step': i + 1,
                'label': _step_label(fpath, i),
                'file': fpath,
                'line': _find_first_fn_line(full),
                'function': fn_name,
                'description': f"Discovered in {Path(fpath).name} via static analysis.",
            })
        if not steps:
            continue
        traces.append({
            'id': f'feat_{p["id"]}',
            'pillar_id': p['id'],
            'title': f"Trace: {p['name']}",
            'description': p['mission'],
            'command': _guess_test_command(p, project),
            'output': f'[Static analysis — run Bob Layer 3 for live output]',
            'http_status': 'READ-ONLY',
            'execution_flow': steps,
        })
    return traces

def _extract_first_function(path: Path) -> str:
    patterns = [
        re.compile(r'^(?:async\s+)?def\s+(\w+)', re.MULTILINE),   # Python
        re.compile(r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)', re.MULTILINE),  # JS/TS
        re.compile(r'^func\s+(\w+)', re.MULTILINE),                # Go
        re.compile(r'^\s*pub\s+fn\s+(\w+)', re.MULTILINE),         # Rust
        re.compile(r'^\s*(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(', re.MULTILINE),  # Java/C#
    ]
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')[:2000]
        for pat in patterns:
            m = pat.search(content)
            if m and m.group(1) not in ('if', 'for', 'while', 'return', 'class'):
                return f'{m.group(1)}()'
    except Exception:
        pass
    return f'{path.stem}()'

def _find_first_fn_line(path: Path) -> int:
    try:
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
        for i, line in enumerate(lines[:100], 1):
            if re.match(r'\s*(async\s+)?(def |func |function |pub fn )', line):
                return i
    except Exception:
        pass
    return 1

def _step_label(fpath: str, idx: int) -> str:
    labels = ['Entrypoint', 'Core Logic', 'Data Access', 'Response / Output']
    name = Path(fpath).stem.replace('_', ' ').replace('-', ' ').title()
    return f"{labels[idx] if idx < len(labels) else 'Step'}: {name}"

def _guess_test_command(p: dict, project: dict) -> str:
    lang = project.get('primary_lang', '')
    if lang == 'Python':
        test_path = next((f for f in p['all_files'] if 'test' in f.lower()), None)
        return f"pytest {test_path or 'tests/'} -v"
    if lang in ('TypeScript', 'JavaScript'):
        return 'npm test'
    if lang == 'Go':
        return 'go test ./...'
    if lang == 'Rust':
        return 'cargo test'
    if lang == 'Java':
        return 'mvn test'
    return f"# Run tests for {p['name']}"

# ── Health metrics ────────────────────────────────────────────────────────────

def collect_health(root: Path, pillars: list[dict]) -> dict:
    health = {}
    is_git = (root / '.git').is_dir()

    for p in pillars:
        file_count = len(p['all_files'])

        # TODO/FIXME count — grep across pillar files
        todo_count = 0
        for fpath in p['all_files']:
            try:
                content = (root / fpath).read_text(encoding='utf-8', errors='ignore')
                todo_count += len(re.findall(r'\b(TODO|FIXME|HACK|XXX)\b', content))
            except Exception:
                pass

        # Last commit age — git log on first file
        last_commit_days = -1
        if is_git and p['files']:
            try:
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%ar', '--', p['files'][0]],
                    capture_output=True, text=True, timeout=8, cwd=root
                )
                raw = result.stdout.strip()
                last_commit_days = _parse_relative_time(raw)
            except Exception:
                pass

        # Test file detection
        test_files = [f for f in p['all_files'] if 'test' in f.lower() or 'spec' in f.lower()]
        test_coverage = -1  # real coverage requires running pytest/jest — left for CI
        if test_files:
            # Rough proxy: ratio of test files to source files, scaled 0-100
            test_coverage = min(100, round(len(test_files) / max(file_count, 1) * 200))

        # Status heuristic
        if last_commit_days < 0:
            status = 'unknown'
        elif last_commit_days <= 7 and todo_count <= 10:
            status = 'healthy'
        elif last_commit_days > 30:
            status = 'stale'
        elif todo_count > 20:
            status = 'needs-attention'
        else:
            status = 'healthy'

        health[p['id']] = {
            'test_coverage': test_coverage,
            'last_commit_days': last_commit_days,
            'todo_count': todo_count,
            'file_count': file_count,
            'status': status,
            'test_files': len(test_files),
        }

    return health

def _parse_relative_time(s: str) -> int:
    """Convert 'N days/weeks/months ago' → integer days. Returns -1 on failure."""
    if not s:
        return -1
    s = s.lower()
    try:
        n = int(re.search(r'\d+', s).group())
        if 'minute' in s or 'second' in s:
            return 0
        if 'hour' in s:
            return 0
        if 'day' in s:
            return n
        if 'week' in s:
            return n * 7
        if 'month' in s:
            return n * 30
        if 'year' in s:
            return n * 365
    except Exception:
        pass
    return -1

# ── Blast radius ──────────────────────────────────────────────────────────────

def build_blast_data(pillars: list[dict], health: dict) -> dict:
    blast = {}
    pid_map = {p['id']: p for p in pillars}

    for p in pillars:
        dependents = p.get('dependents', [])
        n_dep = len(dependents)
        h = health.get(p['id'], {})

        # Risk = base 50 + 10 per downstream dependent + penalty for low tests + stale
        base = 50 + n_dep * 12
        if h.get('test_coverage', -1) >= 0:
            base += max(0, 30 - h['test_coverage'] // 3)
        if h.get('status') == 'stale':
            base += 10
        risk_score = min(99, base)
        risk_level = 'critical' if risk_score >= 88 else 'high' if risk_score >= 72 else 'moderate'

        # Direct breakage: list which dependents break
        direct = [
            f"{dep_id}: callers of {p['name']} lose this dependency" for dep_id in dependents
        ] or [f"Internal callers of {p['name']} module break"]

        downstream = [
            f"All {n_dep} downstream pillar(s) affected" if n_dep else "No downstream pillars detected",
            f"{h.get('file_count', '?')} files become unreachable",
        ]

        db = ['No active transactions at risk'] if p['id'] not in ('data', 'infra') \
             else ['In-flight transactions may be uncommitted', 'Connection pool may exhaust']

        # Pick a test command
        test_files = [f for f in p['all_files'][:20] if 'test' in f.lower() or 'spec' in f.lower()]
        if test_files:
            safety = f"Run: pytest {test_files[0]}" if test_files[0].endswith('.py') else f"Run: npm test -- {test_files[0]}"
        else:
            safety = f"No test files found in {p['name']} — add coverage before changing"

        blast[p['id']] = {
            'title': p['name'],
            'pillar_id': p['id'],
            'risk_score': risk_score,
            'risk_level': risk_level,
            'direct_breakage': direct,
            'downstream_impact': downstream,
            'db_integrity': db,
            'safety_tests': safety,
            'emergency_contacts': p.get('team', '#team-all'),
        }

    return blast

# ── Onboarding quest ──────────────────────────────────────────────────────────

def build_quest(pillars: list[dict], project: dict) -> dict:
    lang = project.get('primary_lang', 'Python')
    repo = project.get('repo_name', 'this repo')
    ep = project.get('entrypoint', 'main')

    run_cmd = {
        'Python': 'docker compose up -d  # or: python -m uvicorn app:app',
        'TypeScript': 'npm install && npm run dev',
        'JavaScript': 'npm install && npm start',
        'Go': 'go run .',
        'Rust': 'cargo run',
        'Java': 'mvn spring-boot:run',
    }.get(lang, 'Follow README for run instructions')

    day1_tasks = [
        {'id': 'q_clone', 'text': f'Clone and start {repo}: {run_cmd}', 'pillar_id': pillars[0]['id'] if pillars else '', 'file_hint': ep},
        {'id': 'q_entry', 'text': f'Read the entrypoint: {ep}', 'pillar_id': pillars[0]['id'] if pillars else '', 'file_hint': ep},
        {'id': 'q_readme', 'text': 'Read README.md end-to-end', 'pillar_id': '', 'file_hint': 'README.md'},
    ]

    week1_tasks = []
    for p in pillars[:4]:
        week1_tasks.append({
            'id': f'q_{p["id"]}_read',
            'text': f'Read the {p["name"]} pillar: {", ".join(Path(f).name for f in p["files"][:2])}',
            'pillar_id': p['id'],
            'file_hint': p['files'][0] if p['files'] else '',
        })
    week1_tasks.append({
        'id': 'q_tests', 'text': 'Run the full test suite and understand coverage gaps',
        'pillar_id': '', 'file_hint': 'tests/',
    })

    month1_tasks = []
    for p in pillars[:2]:
        month1_tasks.append({
            'id': f'q_{p["id"]}_feat',
            'text': f'Add a small feature or fix to {p["name"]}',
            'pillar_id': p['id'],
            'file_hint': p['files'][0] if p['files'] else '',
        })
    month1_tasks.append({
        'id': 'q_pr', 'text': 'Open your first PR and get it reviewed',
        'pillar_id': '', 'file_hint': 'CONTRIBUTING.md',
    })

    return {
        'generated_by': 'IBM Bob 2.0',
        'title': f'{repo} Onboarding Quest',
        'estimated_hours': 6 + len(pillars),
        'phases': [
            {'id': 'day1',  'label': 'Day 1 — Get it Running',              'color': '#3B82F6', 'tasks': day1_tasks},
            {'id': 'week1', 'label': 'Week 1 — Understand the Architecture', 'color': '#10B981', 'tasks': week1_tasks},
            {'id': 'month1','label': 'Month 1 — Own a Feature',              'color': '#8B5CF6', 'tasks': month1_tasks},
        ],
    }

# ── Main ──────────────────────────────────────────────────────────────────────

def scan(repo_path_str: str, feature: str = None) -> dict:
    root = Path(repo_path_str).resolve()
    if not root.is_dir():
        raise ValueError(f"Repository path not found: {root}")

    print(f"  Scanning: {root}")
    files = walk_repo(root)
    print(f"  Found {len(files)} source files")

    project = detect_project(root, files)
    print(f"  Stack: {project['stack']}  |  Lang: {project['primary_lang']}")

    pillars = cluster_pillars(root, files)
    print(f"  Clustered into {len(pillars)} pillars: {[p['id'] for p in pillars]}")

    edges = build_edges(pillars)
    features_menu = build_features_menu(pillars, project)
    traces = build_execution_traces(root, pillars, project)
    health = collect_health(root, pillars)
    blast = build_blast_data(pillars, health)
    quest = build_quest(pillars, project)

    # Strip internal all_files key — not needed by viewer
    for p in pillars:
        p.pop('all_files', None)

    return {
        'generated_by': 'IBM Bob 2.0',
        'generated_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat().replace('+00:00','Z'),
        'repo_name': project['repo_name'],
        'repo_path': str(root),
        'stack': project['stack'],
        'primary_lang': project['primary_lang'],
        'all_langs': project['all_langs'],
        'file_count': project['file_count'],
        'entrypoint': project['entrypoint'],
        'databases': project['databases'],
        'pillar_count': len(pillars),
        'edge_count': len(edges),
        'trace_count': len(traces),
        'pillars': pillars,
        'edges': edges,
        'features_menu': features_menu,
        'features': traces,
        'health': health,
        'blast_data': blast,
        'quest': quest,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='onBob Universal Repository Scanner')
    parser.add_argument('repo_path', nargs='?', default='.', help='Path to repository root')
    parser.add_argument('--out', default='onbob-output', help='Output directory (default: onbob-output)')
    parser.add_argument('--feature', default=None, help='Focus on a specific feature name (Branch B)')
    args = parser.parse_args()

    print('\nonBob -- Universal Repository Scanner')
    print('   IBM Bob 2.0 | Read-Only Mode\n')

    try:
        data = scan(args.repo_path, args.feature)
    except ValueError as e:
        print(f'  ERROR: {e}')
        sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / 'atlas_data.json'
    out_file.write_text(json.dumps(data, indent=2), encoding='utf-8')

    print(f'\n[OK] Done')
    print(f'   Pillars : {data["pillar_count"]}')
    print(f'   Edges   : {data["edge_count"]}')
    print(f'   Traces  : {data["trace_count"]}')
    print(f'   Output  : {out_file}')
    print(f'\n   Open the atlas:')
    print(f'   python -m http.server 3000 --directory {args.out}')
    print(f'   -> http://localhost:3000/architecture-atlas.html')
