
from __future__ import annotations

import collections
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "repos"

LANGUAGES = {
    ".java": "Java", ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".c": "C", ".h": "C", ".cpp": "C++", ".cc": "C++", ".hpp": "C++", ".cxx": "C++",
    ".cs": "C#", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".kt": "Kotlin", ".swift": "Swift", ".sql": "SQL", ".sh": "Shell",
    ".bat": "Batchfile", ".ps1": "PowerShell", ".r": "R", ".m": "MATLAB",
    ".ipynb": "Jupyter Notebook", ".vue": "Vue", ".svelte": "Svelte",
    ".xml": "XML", ".yml": "YAML", ".yaml": "YAML",
}

SKIP_DIRS = re.compile(
    r"(^|/)(\.git|__pycache__|node_modules|\.venv|venv|env|dist|build|bin|obj|"
    r"target|vendor|third_party|3rdparty|external|extern|lib|libs|deps|"
    r"dependencies|packages|bower_components)(/|$)",
    re.I,
)
SKIP_FILES = re.compile(
    r"(\.min\.(js|css)|\.pyc|\.class|\.jar|\.war|\.dll|\.so|\.exe|\.o|\.a|"
    r"\.lock|-lock\.json)$",
    re.I,
)

VENDORED = re.compile(r"(^|/)(sqlite3(ext)?\.[ch]|jquery[.-]|bootstrap([.-]|/)|"
                      r"popper|chart(\.min)?\.js)", re.I)

MAX_FILE_BYTES = 2_000_000

def bare_clone(full_name: str, refresh: bool = True) -> pathlib.Path | None:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{full_name.replace('/', '_')}.git"

    if path.exists():
        if refresh:
            subprocess.run(
                ["git", "-C", str(path), "fetch", "-q", "--all", "--prune"],
                capture_output=True, timeout=180,
            )
        return path

    r = subprocess.run(
        ["git", "clone", "-q", "--bare", "--filter=blob:none",
         f"https://github.com/{full_name}.git", str(path)],
        capture_output=True, text=True, timeout=300,
    )
    if r.returncode != 0:
        print(f"  no se pudo clonar {full_name}: {r.stderr.strip().splitlines()[-1:]}")
        return None
    return path

def _git(path: pathlib.Path, *args: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
    )
    return r.stdout if r.returncode == 0 else ""

def commits_by_email(path: pathlib.Path) -> dict[str, int]:
    out = _git(path, "log", "--format=%ae", "HEAD")
    return dict(collections.Counter(e.strip().lower() for e in out.splitlines() if e.strip()))

def commit_dates(path: pathlib.Path, emails: set[str] | None = None) -> tuple[str, str] | None:
    args = [
        "log", "--format=%ad|%ae", "--date=short", "HEAD",
        "--", ".", ":(exclude)*.md", ":(exclude)LICENSE", ":(exclude).gitignore",
    ]
    rows = []
    for line in _git(path, *args).splitlines():
        date, _, email = line.partition("|")
        if emails and email.strip().lower() not in emails:
            continue
        if date.strip():
            rows.append(date.strip())
    if not rows:
        return None
    return rows[-1], rows[0]

def language_bytes(path: pathlib.Path) -> dict[str, int]:
    totals: dict[str, int] = {}
    for line in _git(path, "ls-tree", "-r", "-l", "HEAD").splitlines():
        parts = line.split(None, 4)
        if len(parts) < 5 or parts[1] != "blob":
            continue
        size, name = parts[3], parts[4].strip()
        if not size.isdigit() or int(size) > MAX_FILE_BYTES:
            continue
        if SKIP_DIRS.search(name) or SKIP_FILES.search(name) or VENDORED.search(name):
            continue
        lang = LANGUAGES.get(pathlib.PurePosixPath(name).suffix.lower())
        if lang:
            totals[lang] = totals.get(lang, 0) + int(size)
    return totals

def survey(full_name: str, identities: set[str]) -> dict | None:
    path = bare_clone(full_name)
    if path is None:
        return None

    by_email = commits_by_email(path)
    mine = sum(n for e, n in by_email.items() if e in identities)
    span = commit_dates(path, identities) or commit_dates(path)
    if span is None:
        return None

    return {
        "repo": full_name,
        "url": f"https://github.com/{full_name}",
        "owner": full_name.split("/")[0],
        "name": full_name.split("/")[1],
        "mine": mine,
        "total": sum(by_email.values()),
        "people": len(by_email),
        "from": span[0],
        "to": span[1],
        "languages": language_bytes(path),
    }
