#!/usr/bin/env python3
"""
Verification script for KI Service Layer splits.

Checks:
1. All new files exist
2. Syntax is valid (py_compile)
3. LOC distribution
4. Import statements work
"""

import os
import sys
import py_compile
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent / "app" / "ki"

# Expected new files
NEW_FILES = {
    "prompts/__init__.py": 0,
    "prompts/registry/__init__.py": 0,
    "prompts/registry/core.py": 0,
    "prompts/registry/db_override.py": 0,
    "prompts/registry/retrieval.py": 0,
    "prompts/registry/initialization.py": 0,
    "prompts/ai_studio/__init__.py": 0,
    "prompts/ai_studio/_base.py": 0,
    "prompts/ai_studio/source.py": 0,
    "prompts/ai_studio/theory.py": 0,
    "prompts/ai_studio/lessons.py": 0,
    "prompts/ai_studio/methods.py": 0,
    "prompts/ai_studio/review.py": 0,
    "prompts/ai_studio/finalize.py": 0,
    "slots/__init__.py": 0,
    "slots/requirements.py": 0,
    "slots/validation.py": 0,
    "slots/mapping.py": 0,
    "slots/capabilities.py": 0,
}

def count_loc(file_path: Path) -> int:
    """Count lines of code in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Count non-empty, non-comment lines
        return len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    except Exception as e:
        print(f"ERROR counting LOC for {file_path}: {e}")
        return 0


def check_syntax(file_path: Path) -> bool:
    """Check if Python file has valid syntax."""
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"SYNTAX ERROR in {file_path}:")
        print(f"  {e}")
        return False


def main():
    print("=" * 80)
    print("KI Service Layer Split Verification")
    print("=" * 80)

    all_valid = True
    total_loc = 0

    print("\n1. FILE EXISTENCE & SYNTAX CHECK")
    print("-" * 80)

    for rel_path in NEW_FILES.keys():
        full_path = BASE_DIR / rel_path
        exists = full_path.exists()
        syntax_ok = check_syntax(full_path) if exists else False
        loc = count_loc(full_path) if exists else 0
        NEW_FILES[rel_path] = loc
        total_loc += loc

        status = "✅" if (exists and syntax_ok) else "❌"
        print(f"{status} {rel_path:50s} {loc:4d} LOC {'OK' if syntax_ok else 'FAIL'}")

        if not (exists and syntax_ok):
            all_valid = False

    print("\n2. LOC DISTRIBUTION BY PACKAGE")
    print("-" * 80)

    # Group by package
    packages = {}
    for rel_path, loc in NEW_FILES.items():
        package = rel_path.split("/")[0] + "/" + (rel_path.split("/")[1] if len(rel_path.split("/")) > 2 else "")
        packages[package] = packages.get(package, 0) + loc

    for package, loc in sorted(packages.items()):
        print(f"  {package:40s} {loc:4d} LOC")

    print(f"\n  {'TOTAL':40s} {total_loc:4d} LOC")

    print("\n3. MAX LOC PER FILE CHECK (limit: 500)")
    print("-" * 80)

    max_violations = []
    for rel_path, loc in NEW_FILES.items():
        if loc > 500:
            max_violations.append((rel_path, loc))
            print(f"❌ {rel_path:50s} {loc:4d} LOC (exceeds 500)")
            all_valid = False

    if not max_violations:
        print("✅ All files are within 500 LOC limit")

    print("\n4. IMPORT TEST")
    print("-" * 80)

    import_tests = [
        ("from app.ki.prompts.registry import PROMPT_REGISTRY", "prompts.registry"),
        ("from app.ki.prompts.ai_studio import init_ai_studio_prompts", "prompts.ai_studio"),
        ("from app.ki.slots import ALL_LM_CONFIGS", "slots"),
    ]

    for import_stmt, package_name in import_tests:
        try:
            exec(import_stmt)
            print(f"✅ {package_name:30s} imports OK")
        except Exception as e:
            print(f"❌ {package_name:30s} IMPORT FAILED: {e}")
            all_valid = False

    print("\n" + "=" * 80)
    if all_valid:
        print("✅ ALL CHECKS PASSED")
    else:
        print("❌ SOME CHECKS FAILED")
    print("=" * 80)

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
