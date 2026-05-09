#!/usr/bin/env python3
"""Repository analyzer unit tests."""

import os
import sys
import tempfile
from pathlib import Path

# Ensure project root is importable for tests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.repo_analyzer import analyze_repository, _collect_git_stats, _collect_code_stats


def test_collect_git_stats_not_git_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        stats = _collect_git_stats(Path(temp_dir))

        assert isinstance(stats, dict)
        assert stats["is_git_repo"] is False
        assert stats["commit_count"] == 0
        assert stats["contributors"] == 0
        assert stats["current_branch"] is None
        assert stats["latest_commit"]["hash"] == ""


def test_collect_code_stats_current_repo():
    root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    stats = _collect_code_stats(root)

    assert isinstance(stats, dict)
    assert stats["total_files"] > 0
    assert stats["total_lines"] >= 0
    assert stats["total_bytes"] >= 0
    assert "language_breakdown" in stats


def test_analyze_repository_main():
    result = analyze_repository()

    assert isinstance(result, dict)
    assert "repository_root" in result
    assert "code_stats" in result
    assert "git_stats" in result
    assert result["code_stats"]["total_files"] > 0
