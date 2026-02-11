#!/usr/bin/env python3
"""
Advanced Loose Files Scanner - Filters Blueprint Routes, Barrel Exports, Setup Files

Usage:
    cd /home/pascal/Lernsystem
    python3 scripts/backend_analysis/1_find_loose_files_advanced.py
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

def is_blueprint_file(file_path):
    """Check if file defines or uses Flask Blueprint"""
    try:
        content = file_path.read_text()
        patterns = [
            r'Blueprint\(',
            r'@.*\.route\(',
            r'register_blueprint',
        ]
        return any(re.search(pattern, content) for pattern in patterns)
    except:
        return False

def is_barrel_export(file_path, app_dir):
    """Check if file is exported via __init__.py"""
    try:
        parent_init = file_path.parent / "__init__.py"
        if not parent_init.exists():
            return False
        
        content = parent_init.read_text()
        filename = file_path.stem
        
        # Check for various export patterns
        patterns = [
            rf'from \.{filename} import',
            rf'from \.{filename}\.',
            rf'import \.{filename}',
        ]
        return any(re.search(pattern, content) for pattern in patterns)
    except:
        return False

def is_setup_file(file_path):
    """Check if it's a setup/bootstrap file"""
    path_str = str(file_path)
    setup_indicators = [
        '/setup/',
        '/core/bootstrap/',
        'routes_',
        '__main__.py',
        'wsgi.py',
    ]
    return any(indicator in path_str for indicator in setup_indicators)

def is_model_file(file_path):
    """Check if it's a domain model (might be used by ORM)"""
    return '/domain/models/' in str(file_path) or '/models.py' in str(file_path)

def find_loose_files_advanced():
    print("=" * 70)
    print("  ADVANCED LOOSE FILES SCAN - backend/app/")
    print("=" * 70)
    print()
    
    project_root = Path(__file__).parent.parent.parent
    app_dir = project_root / "backend" / "app"
    
    if not app_dir.exists():
        print(f"❌ Error: {app_dir} not found!")
        return
    
    os.chdir(project_root / "backend")
    
    print("🔍 Scanning with advanced filtering...")
    print()
    
    true_loose = []
    filtered = {
        'blueprint': [],
        'barrel_export': [],
        'setup': [],
        'model': [],
    }
    
    checked = 0
    
    for py_file in app_dir.rglob("*.py"):
        if py_file.name == "__init__.py" or "__pycache__" in str(py_file):
            continue
        
        checked += 1
        rel_path = py_file.relative_to(project_root / "backend")
        module_path = str(rel_path.with_suffix("")).replace("/", ".")
        
        # Search for imports
        patterns = [
            f'from {module_path} import',
            f'import {module_path}',
        ]
        
        import_count = 0
        for pattern in patterns:
            try:
                result = subprocess.run(
                    ['grep', '-r', pattern, 'app/', '--include=*.py'],
                    capture_output=True,
                    text=True,
                    cwd=project_root / "backend"
                )
                imports = [line for line in result.stdout.split('\n') 
                          if line and str(py_file.name) not in line.split(':')[0]]
                import_count += len(imports)
            except:
                pass
        
        if import_count == 0:
            # Categorize
            if is_blueprint_file(py_file):
                filtered['blueprint'].append(str(rel_path))
            elif is_barrel_export(py_file, app_dir):
                filtered['barrel_export'].append(str(rel_path))
            elif is_setup_file(py_file):
                filtered['setup'].append(str(rel_path))
            elif is_model_file(py_file):
                filtered['model'].append(str(rel_path))
            else:
                # True loose file
                try:
                    lines = len(py_file.read_text().splitlines())
                    size = py_file.stat().st_size
                    modified = datetime.fromtimestamp(py_file.stat().st_mtime)
                    
                    true_loose.append({
                        'path': str(rel_path),
                        'lines': lines,
                        'size': size,
                        'modified': modified.strftime("%Y-%m-%d")
                    })
                except:
                    pass
    
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print(f"Files checked: {checked}")
    print()
    print(f"🔴 True loose files: {len(true_loose)}")
    print(f"🟡 Filtered (Blueprint): {len(filtered['blueprint'])}")
    print(f"🟡 Filtered (Barrel Export): {len(filtered['barrel_export'])}")
    print(f"🟡 Filtered (Setup Files): {len(filtered['setup'])}")
    print(f"🟡 Filtered (Model Files): {len(filtered['model'])}")
    print()
    
    if true_loose:
        print("🔴 TRUE LOOSE FILES (High confidence dead code):\n")
        for file in sorted(true_loose, key=lambda x: x['lines']):
            print(f"  📄 {file['path']}")
            print(f"     └─ {file['lines']} lines | Modified: {file['modified']}")
            print()
        
        # Save report
        output_file = project_root / "scripts" / "backend_analysis" / "true_loose_files.txt"
        with open(output_file, 'w') as f:
            f.write("TRUE LOOSE FILES (Dead Code Candidates)\n")
            f.write("=" * 70 + "\n\n")
            for file in sorted(true_loose, key=lambda x: x['lines']):
                f.write(f"{file['path']}\n")
                f.write(f"  Lines: {file['lines']}\n")
                f.write(f"  Modified: {file['modified']}\n\n")
        
        print(f"📊 Report saved to: {output_file}")
    else:
        print("✅ No true loose files found!")
    
    # Show filtered summary
    print("\n" + "=" * 70)
    print("  FILTERED FILES (Active but no direct imports)")
    print("=" * 70)
    
    for category, files in filtered.items():
        if files:
            print(f"\n{category.upper()} ({len(files)} files):")
            for f in files[:5]:
                print(f"  ✓ {f}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")

if __name__ == "__main__":
    find_loose_files_advanced()
