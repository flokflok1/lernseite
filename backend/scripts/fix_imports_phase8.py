#!/usr/bin/env python3
"""
Import Migration Script - Phase 9 (2026-01-08)
Fixes imports after ISO/DDD refactoring.

Changes:
- Phase 8a-8c: tokens/, math/ packages created
- Phase 9: ISO/DDD compliant parallel structure (Frontend ↔ Backend)
  - admin.courses → admin.content_management.courses
  - admin.ai → admin.ai_operations (proxy to system_features/ai/)
  - admin.users → admin.user_management (proxy to users/admin/)
  - admin.system → admin.system_operations

Usage:
    python scripts/fix_imports_phase8.py

Author: Claude Opus 4.5
Date: 2026-01-08
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Working directory
BACKEND_DIR = Path(__file__).parent.parent
APP_DIR = BACKEND_DIR / 'app'

# Import replacements (old pattern -> new pattern)
REPLACEMENTS = {
    # Admin courses → content_management
    r'from app\.api\.admin\.courses import':
        'from app.api.admin.content_management.courses import',

    # Admin AI → ai_operations (proxy to system_features/ai/)
    r'from app\.api\.admin\.ai import':
        'from app.api.admin.ai_operations import',

    # Admin users → user_management (proxy to users/admin/)
    r'from app\.api\.admin\.users import':
        'from app.api.admin.user_management import',

    # Admin system → system_operations
    r'from app\.api\.admin\.system import':
        'from app.api.admin.system_operations.system import',
}

# Files to check (relative to BACKEND_DIR)
FILES_TO_CHECK = [
    'app/api/admin/ai/studio/core.py',
    'app/api/admin/__init__.py',
]


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
            replacements_made += 1

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return replacements_made

    return 0


def main():
    """Main function."""
    print("=" * 80)
    print("Phase 8f: Import Migration Script")
    print("=" * 80)
    print()

    total_issues = 0
    total_files_fixed = 0

    # Phase 1: Detection
    print("Phase 1: Detecting import issues...")
    print("-" * 80)

    for file_rel in FILES_TO_CHECK:
        file_path = BACKEND_DIR / file_rel
        issues = find_import_issues(file_path)

        if issues:
            total_issues += len(issues)
            print(f"\n{file_rel}:")
            for line_num, old_line, new_line in issues:
                print(f"  Line {line_num}:")
                print(f"    Old: {old_line}")
                print(f"    New: {new_line}")

    if total_issues == 0:
        print("\n✓ No import issues found!")
        return

    print()
    print(f"Found {total_issues} import issue(s) in {len(FILES_TO_CHECK)} file(s)")
    print()

    # Phase 2: Fix
    response = input("Proceed with fixes? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    print()
    print("Phase 2: Fixing imports...")
    print("-" * 80)

    for file_rel in FILES_TO_CHECK:
        file_path = BACKEND_DIR / file_rel
        replacements = fix_imports_in_file(file_path)

        if replacements > 0:
            total_files_fixed += 1
            print(f"✓ {file_rel}: {replacements} replacement(s)")

    print()
    print("=" * 80)
    print(f"Complete: {total_files_fixed} file(s) updated, {total_issues} import(s) fixed")
    print("=" * 80)


if __name__ == '__main__':
    main()
