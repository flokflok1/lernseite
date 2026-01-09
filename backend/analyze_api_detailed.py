#!/usr/bin/env python3
"""
Detailed analysis of /app/api structure for ISO-compliant reorganization.
"""
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

def analyze_api_structure():
    api_path = Path("/home/pascal/Lernsystem/backend/app/api")

    # Analyze root files
    root_files = []
    for file in api_path.glob("*.py"):
        if file.name != "__init__.py":
            lines = len(file.read_text().splitlines())
            root_files.append({
                'name': file.name,
                'lines': lines,
                'size_kb': file.stat().st_size / 1024
            })

    # Sort by lines
    root_files.sort(key=lambda x: x['lines'], reverse=True)

    # Analyze existing subdirectories
    subdirs = []
    for subdir in api_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('_'):
            py_files = list(subdir.rglob("*.py"))
            total_lines = sum(len(f.read_text().splitlines()) for f in py_files)
            subdirs.append({
                'name': subdir.name,
                'files': len(py_files),
                'total_lines': total_lines
            })

    subdirs.sort(key=lambda x: x['files'], reverse=True)

    # Categorize root files by prefix
    categories = defaultdict(list)
    for file in root_files:
        name = file['name']
        if name.startswith('admin_'):
            # Further categorize admin files
            parts = name.replace('admin_', '').replace('.py', '').split('_')
            if len(parts) >= 2:
                category = f"admin.{parts[0]}"
            else:
                category = "admin.other"
            categories[category].append(file)
        elif '_' in name:
            prefix = name.split('_')[0]
            categories[prefix].append(file)
        else:
            categories['general'].append(file)

    # Print report
    print("=" * 100)
    print("API STRUCTURE DETAILED ANALYSIS - ISO-COMPLIANT REORGANIZATION")
    print("=" * 100)
    print()

    print("📊 OVERVIEW")
    print("-" * 100)
    print(f"Total root .py files: {len(root_files)}")
    print(f"Existing subdirectories: {len(subdirs)}")
    total_root_lines = sum(f['lines'] for f in root_files)
    print(f"Total lines in root files: {total_root_lines:,}")
    print()

    print("📁 EXISTING SUBDIRECTORIES (Already organized)")
    print("-" * 100)
    for subdir in subdirs:
        status = "✅ Well organized" if subdir['files'] > 3 else "⚠️  Small"
        print(f"  {subdir['name']:25s} {subdir['files']:2d} files, {subdir['total_lines']:5,} lines  {status}")
    print()

    print("📄 ROOT FILES BY SIZE (Top 15 - Need reorganization)")
    print("-" * 100)
    for i, file in enumerate(root_files[:15], 1):
        status = "🔴 >500" if file['lines'] > 500 else "🟡 >400" if file['lines'] > 400 else "⚠️  >300" if file['lines'] > 300 else "✓"
        print(f"  {i:2d}. {file['name']:40s} {file['lines']:4d} lines  {status}")
    print(f"  ... and {len(root_files) - 15} more files")
    print()

    print("🏷️  FILE CATEGORIZATION (By prefix/domain)")
    print("-" * 100)

    # Sort categories by number of files
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

    for category, files in sorted_categories:
        total_lines = sum(f['lines'] for f in files)
        print(f"\n  📦 {category.upper()}")
        print(f"     Files: {len(files)}, Total lines: {total_lines:,}")
        print("     " + "-" * 90)

        for file in files:
            status = "🔴" if file['lines'] > 500 else "🟡" if file['lines'] > 400 else "  "
            print(f"     {status} {file['name']:45s} {file['lines']:4d} lines")

    print()
    print("=" * 100)
    print("RECOMMENDATIONS")
    print("=" * 100)
    print()

    # Count admin files
    admin_categories = {k: v for k, v in categories.items() if k.startswith('admin.')}
    admin_file_count = sum(len(files) for files in admin_categories.values())

    print(f"🔴 HIGH PRIORITY:")
    print(f"   - Admin files to reorganize: {admin_file_count} files")
    print(f"   - Files >500 lines to split: {len([f for f in root_files if f['lines'] > 500])} files")
    print(f"   - Total root files to organize: {len(root_files)} files")
    print()

    print(f"✅ KEEP AS IS:")
    print(f"   - Existing subdirectories: {len(subdirs)} (already well organized)")
    print()

    return {
        'root_files': root_files,
        'subdirs': subdirs,
        'categories': dict(categories),
        'admin_file_count': admin_file_count
    }

if __name__ == "__main__":
    result = analyze_api_structure()
