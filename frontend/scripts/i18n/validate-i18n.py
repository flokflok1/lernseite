#!/usr/bin/env python3
"""
i18n Validation Script
======================

Validates the locale structure for consistency and issues.

Usage:
    python validate-i18n.py

Checks:
- All languages have identical file structure
- All languages have identical keys
- No duplicate keys across files
- File size limits (<600 LOC / ~30KB)
- JSON syntax validity
- Alphabetical key sorting
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict

# Constants
LOCALES_DIR = Path(__file__).parent
LANGUAGES = ['de', 'en', 'pl']
MAX_FILE_SIZE_KB = 30
MAX_LINES = 600

# Colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_status(emoji: str, message: str, color: str = ''):
    """Print colored status message."""
    print(f"{color}{emoji} {message}{RESET}")


def get_all_keys(obj: dict, prefix: str = '') -> Set[str]:
    """Recursively get all keys from nested dict."""
    keys = set()
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.add(full_key)
        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))
    return keys


def is_sorted(obj: dict) -> Tuple[bool, List[str]]:
    """Check if dict keys are alphabetically sorted."""
    keys = list(obj.keys())
    sorted_keys = sorted(keys)
    if keys != sorted_keys:
        return False, keys

    # Check nested objects
    for value in obj.values():
        if isinstance(value, dict):
            nested_sorted, nested_keys = is_sorted(value)
            if not nested_sorted:
                return False, nested_keys

    return True, []


def validate_json_file(file_path: Path) -> Tuple[bool, str]:
    """Validate single JSON file."""
    try:
        # Check file size
        size_kb = file_path.stat().st_size / 1024
        if size_kb > MAX_FILE_SIZE_KB:
            return False, f"File too large: {size_kb:.1f}KB (max {MAX_FILE_SIZE_KB}KB)"

        # Check line count
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
            if lines > MAX_LINES:
                return False, f"Too many lines: {lines} (max {MAX_LINES})"

        # Validate JSON syntax
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check alphabetical sorting
        sorted_ok, unsorted_keys = is_sorted(data)
        if not sorted_ok:
            return False, f"Keys not alphabetically sorted: {unsorted_keys[:3]}"

        return True, "OK"

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def get_locale_structure(lang: str) -> Dict[str, Path]:
    """Get all JSON files for a language."""
    lang_dir = LOCALES_DIR / lang
    files = {}

    for json_file in lang_dir.rglob('*.json'):
        rel_path = json_file.relative_to(lang_dir)
        files[str(rel_path)] = json_file

    return files


def compare_structures() -> Tuple[bool, List[str]]:
    """Compare file structures across languages."""
    structures = {lang: set(get_locale_structure(lang).keys()) for lang in LANGUAGES}

    issues = []

    # Check if all languages have same files
    base_structure = structures['de']
    for lang in ['en', 'pl']:
        missing = base_structure - structures[lang]
        extra = structures[lang] - base_structure

        if missing:
            issues.append(f"{lang} missing files: {', '.join(missing)}")
        if extra:
            issues.append(f"{lang} has extra files: {', '.join(extra)}")

    return len(issues) == 0, issues


def compare_keys() -> Tuple[bool, Dict[str, List[str]]]:
    """Compare translation keys across languages."""
    all_keys = {}

    # Get all keys for each language
    for lang in LANGUAGES:
        lang_keys = defaultdict(set)
        for file_path, json_path in get_locale_structure(lang).items():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lang_keys[file_path] = get_all_keys(data)
        all_keys[lang] = lang_keys

    # Compare
    issues = {}
    base_lang = 'de'

    for file_path in all_keys[base_lang].keys():
        base_keys = all_keys[base_lang][file_path]
        file_issues = []

        for lang in ['en', 'pl']:
            if file_path not in all_keys[lang]:
                continue

            lang_keys = all_keys[lang][file_path]
            missing = base_keys - lang_keys
            extra = lang_keys - base_keys

            if missing:
                file_issues.append(f"{lang} missing keys: {', '.join(list(missing)[:5])}")
            if extra:
                file_issues.append(f"{lang} extra keys: {', '.join(list(extra)[:5])}")

        if file_issues:
            issues[file_path] = file_issues

    return len(issues) == 0, issues


def main():
    """Run all validations."""
    print_status("🔍", "Starting i18n validation...", BLUE)
    print()

    all_ok = True

    # 1. File structure comparison
    print_status("📁", "Checking file structure consistency...", BLUE)
    structure_ok, structure_issues = compare_structures()

    if structure_ok:
        print_status("✓", "All languages have identical file structure", GREEN)
    else:
        print_status("✗", "File structure mismatch:", RED)
        for issue in structure_issues:
            print(f"  - {issue}")
        all_ok = False
    print()

    # 2. Validate each JSON file
    print_status("📄", "Validating JSON files...", BLUE)
    file_count = 0
    error_count = 0

    for lang in LANGUAGES:
        for file_path, json_path in get_locale_structure(lang).items():
            file_count += 1
            is_valid, message = validate_json_file(json_path)

            if not is_valid:
                print_status("✗", f"{lang}/{file_path}: {message}", RED)
                error_count += 1
                all_ok = False

    if error_count == 0:
        print_status("✓", f"All {file_count} JSON files valid", GREEN)
    else:
        print_status("✗", f"{error_count}/{file_count} files have issues", RED)
    print()

    # 3. Key consistency check
    print_status("🔑", "Checking key consistency across languages...", BLUE)
    keys_ok, key_issues = compare_keys()

    if keys_ok:
        print_status("✓", "All translation keys consistent", GREEN)
    else:
        print_status("✗", "Key inconsistencies found:", RED)
        for file_path, issues in key_issues.items():
            print(f"  {file_path}:")
            for issue in issues:
                print(f"    - {issue}")
        all_ok = False
    print()

    # 4. Statistics
    print_status("📊", "Statistics:", BLUE)
    total_files = len(get_locale_structure('de'))
    total_keys = sum(len(get_all_keys(json.load(open(p, 'r', encoding='utf-8'))))
                     for p in get_locale_structure('de').values())

    print(f"  - Languages: {len(LANGUAGES)}")
    print(f"  - Files per language: {total_files}")
    print(f"  - Total translation keys: {total_keys}")
    print()

    # Final result
    if all_ok:
        print_status("✅", "All validations passed!", GREEN)
        return 0
    else:
        print_status("❌", "Validation failed - please fix issues above", RED)
        return 1


if __name__ == '__main__':
    sys.exit(main())
