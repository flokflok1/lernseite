#!/usr/bin/env python3
"""
Analyze backend folder structure to identify directories that need reorganization.
"""
import os
from pathlib import Path
from typing import Dict, List, Tuple

def analyze_directory(dir_path: Path) -> Dict:
    """Analyze a directory and return statistics."""
    py_files_root = list(dir_path.glob("*.py"))
    subdirs = [d for d in dir_path.iterdir() if d.is_dir() and not d.name.startswith('__')]

    # Count total lines in root .py files
    total_lines = 0
    large_files = []
    for py_file in py_files_root:
        try:
            lines = len(py_file.read_text().splitlines())
            total_lines += lines
            if lines > 500:
                large_files.append((py_file.name, lines))
        except:
            pass

    return {
        'path': str(dir_path),
        'name': dir_path.name,
        'py_files_count': len(py_files_root),
        'py_files': [f.name for f in py_files_root],
        'subdirs_count': len(subdirs),
        'subdirs': [d.name for d in subdirs],
        'total_lines': total_lines,
        'large_files': large_files
    }

def main():
    backend_path = Path("/home/pascal/Lernsystem/backend")
    app_path = backend_path / "app"

    # Analyze main directories
    dirs_to_check = [
        app_path / "api",
        app_path / "services",
        app_path / "models",
        app_path / "middleware",
        app_path / "ki",
        app_path / "gateway",
        app_path / "security",
        app_path / "monitoring",
        app_path / "sockets",
        app_path / "tasks",
        backend_path / "setup",
    ]

    results = []
    for dir_path in dirs_to_check:
        if dir_path.exists():
            result = analyze_directory(dir_path)
            results.append(result)

    # Sort by py_files_count descending
    results.sort(key=lambda x: x['py_files_count'], reverse=True)

    print("=" * 80)
    print("BACKEND STRUCTURE ANALYSIS")
    print("=" * 80)
    print()

    for result in results:
        print(f"📁 {result['name']}")
        print(f"   Path: {result['path']}")
        print(f"   .py files in root: {result['py_files_count']}")
        print(f"   Subdirectories: {result['subdirs_count']}")
        print(f"   Total lines (root .py): {result['total_lines']:,}")

        if result['large_files']:
            print(f"   ⚠️  Large files (>500 lines):")
            for fname, lines in result['large_files']:
                print(f"      - {fname}: {lines:,} lines")

        if result['py_files_count'] > 10:
            print(f"   🔴 NEEDS REORGANIZATION - Too many root .py files!")
        elif result['py_files_count'] > 5:
            print(f"   🟡 Consider reorganization")
        else:
            print(f"   ✅ Acceptable")

        if result['subdirs_count'] > 0:
            print(f"   Subdirs: {', '.join(result['subdirs'][:5])}")
            if len(result['subdirs']) > 5:
                print(f"            ... and {len(result['subdirs']) - 5} more")

        print()

    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    high_priority = [r for r in results if r['py_files_count'] > 10]
    medium_priority = [r for r in results if 5 < r['py_files_count'] <= 10]

    if high_priority:
        print("🔴 HIGH PRIORITY (>10 root .py files):")
        for r in high_priority:
            print(f"   - {r['name']}: {r['py_files_count']} files, {r['total_lines']:,} lines")
        print()

    if medium_priority:
        print("🟡 MEDIUM PRIORITY (5-10 root .py files):")
        for r in medium_priority:
            print(f"   - {r['name']}: {r['py_files_count']} files, {r['total_lines']:,} lines")
        print()

if __name__ == "__main__":
    main()
