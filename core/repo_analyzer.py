#!/usr/bin/env python3
"""Repository analysis utility for GavatCore.

Provides lightweight stats for source tree and git metadata.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def _is_git_repo(root_path: Path) -> bool:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        return completed.returncode == 0 and completed.stdout.strip() == "true"
    except Exception:
        return False


def _run_git_command(root_path: Path, args: list) -> Optional[str]:
    try:
        completed = subprocess.run(
            ["git"] + args,
            cwd=root_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        if completed.returncode != 0:
            return None
        return completed.stdout.strip()
    except Exception:
        return None


def _collect_git_stats(root_path: Path) -> Dict[str, Any]:
    if not _is_git_repo(root_path):
        return {
            "is_git_repo": False,
            "commit_count": 0,
            "contributors": 0,
            "current_branch": None,
            "latest_commit": {
                "hash": "",
                "author": "",
                "date": "",
            },
            "top_contributors": [],
        }

    commit_count = _run_git_command(root_path, ["rev-list", "--all", "--count"]) or "0"
    current_branch = _run_git_command(root_path, ["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    last_commit_hash = _run_git_command(root_path, ["rev-parse", "HEAD"]) or ""
    last_commit_author = _run_git_command(root_path, ["log", "-1", "--pretty=format:%an"]) or ""
    last_commit_date = _run_git_command(root_path, ["log", "-1", "--pretty=format:%ci"]) or ""

    contributors_raw = _run_git_command(root_path, ["shortlog", "-sn", "--all"]) or ""
    contributors = []
    for line in contributors_raw.splitlines():
        try:
            count_str, name = line.strip().split("\t", 1)
            contributors.append({"name": name.strip(), "commits": int(count_str.strip())})
        except Exception:
            continue

    contributors_count = len(contributors)

    return {
        "is_git_repo": True,
        "commit_count": int(commit_count) if str(commit_count).isdigit() else 0,
        "contributors": contributors_count,
        "current_branch": current_branch,
        "latest_commit": {
            "hash": last_commit_hash,
            "author": last_commit_author,
            "date": last_commit_date,
        },
        "top_contributors": contributors[:10],
    }


def _guess_language(extension: str) -> str:
    ext_map = {
        "py": "Python",
        "md": "Markdown",
        "ipynb": "Jupyter Notebook",
        "json": "JSON",
        "yaml": "YAML",
        "yml": "YAML",
        "js": "JavaScript",
        "ts": "TypeScript",
        "sh": "Shell",
        "css": "CSS",
        "html": "HTML",
        "csv": "CSV",
        "txt": "Text",

    }
    return ext_map.get(extension.lower(), "Other")


def _collect_code_stats(root_path: Path) -> Dict[str, Any]:
    total_files = 0
    total_lines = 0
    total_bytes = 0
    language_stats: Dict[str, Dict[str, int]] = {}

    for dirpath, _, filenames in os.walk(root_path):
        if ".git" in dirpath:
            continue

        for filename in filenames:
            path = Path(dirpath) / filename
            if not path.is_file():
                continue

            total_files += 1
            try:
                size = path.stat().st_size
            except Exception:
                size = 0
            total_bytes += size

            ext = path.suffix.lstrip(".")
            lang = _guess_language(ext)
            lines = 0
            try:
                with path.open("rb") as f:
                    for _ in f:
                        lines += 1
            except Exception:
                lines = 0

            total_lines += lines

            if lang not in language_stats:
                language_stats[lang] = {"files": 0, "lines": 0, "bytes": 0}

            language_stats[lang]["files"] += 1
            language_stats[lang]["lines"] += lines
            language_stats[lang]["bytes"] += size

    return {
        "total_files": total_files,
        "total_lines": total_lines,
        "total_bytes": total_bytes,
        "language_breakdown": language_stats,
    }


def analyze_repository(root_path: Optional[str] = None) -> Dict[str, Any]:
    root = Path(root_path or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Repository root path not found: {root}")

    code_stats = _collect_code_stats(root)
    git_stats = _collect_git_stats(root)

    return {
        "repository_root": str(root),
        "code_stats": code_stats,
        "git_stats": git_stats,
    }
