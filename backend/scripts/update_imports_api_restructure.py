#!/usr/bin/env python3
"""
Import Update Script - API Complete Restructure
Updates imports after complete API reorganization (2026-01-08).

Changes:
- courses/ → user/courses/
- dashboard/ → user/dashboard/
- exams/ → user/exams/
- lessons/ → user/lessons/
- profile/ → user/profile/
- subscriptions/ → user/subscriptions/
- tokens/ → user/tokens/
- chapter_theory/ → user/chapters/
- categories/ → shared/categories/
- feedback/ → shared/feedback/
- media/ → shared/media/
- organisations/ → shared/organisations/
- users/ → shared/users/
- auth/ → core/auth/
- i18n/ → core/i18n/
- agents/ → system_features/agents/
- math/ → system_features/math/

Usage:
    python scripts/update_imports_api_restructure.py

Author: Claude Opus 4.5
Date: 2026-01-08
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Working directory
BACKEND_DIR = Path(__file__).parent.parent
APP_DIR = BACKEND_DIR / 'app'

# Import replacements (old pattern -> new pattern)
REPLACEMENTS = {
    # User APIs
    r'from app\.api\.courses import': 'from app.api.user.courses import',
    r'from app\.api\.courses\.': 'from app.api.user.courses.',
    r'from app\.api import courses': 'from app.api.user import courses',

    r'from app\.api\.dashboard import': 'from app.api.user.dashboard import',
    r'from app\.api\.dashboard\.': 'from app.api.user.dashboard.',
    r'from app\.api import dashboard': 'from app.api.user import dashboard',

    r'from app\.api\.exams import': 'from app.api.user.exams import',
    r'from app\.api\.exams\.': 'from app.api.user.exams.',
    r'from app\.api import exams': 'from app.api.user import exams',

    r'from app\.api\.lessons import': 'from app.api.user.lessons import',
    r'from app\.api\.lessons\.': 'from app.api.user.lessons.',
    r'from app\.api import lessons': 'from app.api.user import lessons',

    r'from app\.api\.profile import': 'from app.api.user.profile import',
    r'from app\.api\.profile\.': 'from app.api.user.profile.',
    r'from app\.api import profile': 'from app.api.user import profile',

    r'from app\.api\.subscriptions import': 'from app.api.user.subscriptions import',
    r'from app\.api\.subscriptions\.': 'from app.api.user.subscriptions.',
    r'from app\.api import subscriptions': 'from app.api.user import subscriptions',

    r'from app\.api\.tokens import': 'from app.api.user.tokens import',
    r'from app\.api\.tokens\.': 'from app.api.user.tokens.',
    r'from app\.api import tokens': 'from app.api.user import tokens',

    # Chapter theory → user/chapters
    r'from app\.api\.chapter_theory import': 'from app.api.user.chapters import',
    r'from app\.api\.chapter_theory\.': 'from app.api.user.chapters.',
    r'from app\.api import chapter_theory': 'from app.api.user import chapters',

    # Shared APIs
    r'from app\.api\.categories import': 'from app.api.shared.categories import',
    r'from app\.api\.categories\.': 'from app.api.shared.categories.',
    r'from app\.api import categories': 'from app.api.shared import categories',

    r'from app\.api\.feedback import': 'from app.api.shared.feedback import',
    r'from app\.api\.feedback\.': 'from app.api.shared.feedback.',
    r'from app\.api import feedback': 'from app.api.shared import feedback',

    r'from app\.api\.media import': 'from app.api.shared.media import',
    r'from app\.api\.media\.': 'from app.api.shared.media.',
    r'from app\.api import media': 'from app.api.shared import media',

    r'from app\.api\.organisations import': 'from app.api.shared.organisations import',
    r'from app\.api\.organisations\.': 'from app.api.shared.organisations.',
    r'from app\.api import organisations': 'from app.api.shared import organisations',

    r'from app\.api\.users import': 'from app.api.shared.users import',
    r'from app\.api\.users\.': 'from app.api.shared.users.',
    r'from app\.api import users': 'from app.api.shared import users',

    # Core APIs
    r'from app\.api\.auth import': 'from app.api.core.auth import',
    r'from app\.api\.auth\.': 'from app.api.core.auth.',
    r'from app\.api import auth': 'from app.api.core import auth',

    r'from app\.api\.i18n import': 'from app.api.core.i18n import',
    r'from app\.api\.i18n\.': 'from app.api.core.i18n.',
    r'from app\.api import i18n': 'from app.api.core import i18n',

    # System Features
    r'from app\.api\.agents import': 'from app.api.system_features.agents import',
    r'from app\.api\.agents\.': 'from app.api.system_features.agents.',
    r'from app\.api import agents': 'from app.api.system_features import agents',

    r'from app\.api\.math import': 'from app.api.system_features.math import',
    r'from app\.api\.math\.': 'from app.api.system_features.math.',
    r'from app\.api import math': 'from app.api.system_features import math',
}


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in directory."""
    return list(directory.rglob("*.py"))


def find_import_issues(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Find import issues in a file.

    Returns:
        List of (line_number, old_line, new_line) tuples
    """
    if not file_path.exists():
        return []

    issues = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        for old_pattern, new_import in REPLACEMENTS.items():
            if re.search(old_pattern, line):
                new_line = re.sub(old_pattern, new_import, line)
                if new_line != line:  # Only if actually changed
                    issues.append((i, line.strip(), new_line.strip()))

    return issues


def fix_imports_in_file(file_path: Path) -> int:
    """
    Fix imports in a file.

    Returns:
        Number of replacements made
    """
    if not file_path.exists():
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replacements_made = 0

    for old_pattern, new_import in REPLACEMENTS.items():
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_import, content)
            replacements_made += content.count(new_import) - original_content.count(new_import)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return replacements_made


def main():
    """Main function."""
    print("=" * 80)
    print("API Complete Restructure: Import Update Script")
    print("=" * 80)
    print()

    # Find all Python files
    print("Finding Python files...")
    python_files = find_python_files(APP_DIR)
    print(f"Found {len(python_files)} Python files")
    print()

    # Phase 1: Detection
    print("Phase 1: Detecting import issues...")
    print("-" * 80)

    total_issues = 0
    files_with_issues: Dict[Path, List[Tuple[int, str, str]]] = {}

    for file_path in python_files:
        issues = find_import_issues(file_path)
        if issues:
            files_with_issues[file_path] = issues
            total_issues += len(issues)

    if total_issues == 0:
        print("\n✓ No import issues found!")
        return

    print(f"\nFound {total_issues} import issue(s) in {len(files_with_issues)} file(s)")
    print()

    # Show first 10 files with issues
    print("Sample issues (first 10 files):")
    for i, (file_path, issues) in enumerate(list(files_with_issues.items())[:10]):
        rel_path = file_path.relative_to(BACKEND_DIR)
        print(f"\n{i+1}. {rel_path} ({len(issues)} issue(s))")
        for line_num, old_line, new_line in issues[:3]:  # Show first 3 issues per file
            print(f"   Line {line_num}:")
            print(f"     OLD: {old_line}")
            print(f"     NEW: {new_line}")
        if len(issues) > 3:
            print(f"   ... and {len(issues) - 3} more")

    if len(files_with_issues) > 10:
        print(f"\n... and {len(files_with_issues) - 10} more files")

    print()

    # Phase 2: Fix
    response = input("Proceed with fixes? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    print()
    print("Phase 2: Fixing imports...")
    print("-" * 80)

    total_files_fixed = 0
    total_replacements = 0

    for file_path in files_with_issues.keys():
        replacements = fix_imports_in_file(file_path)
        if replacements > 0:
            total_files_fixed += 1
            total_replacements += replacements
            rel_path = file_path.relative_to(BACKEND_DIR)
            print(f"✓ {rel_path}: {replacements} replacement(s)")

    print()
    print("=" * 80)
    print(f"Complete: {total_files_fixed} file(s) updated, {total_replacements} import(s) fixed")
    print("=" * 80)


if __name__ == '__main__':
    main()
