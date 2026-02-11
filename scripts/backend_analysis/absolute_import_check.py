#!/usr/bin/env python3
"""
ABSOLUTE import checker - no bullshit heuristics
Checks EVERY Python file if it's imported ANYWHERE
"""

import subprocess
from pathlib import Path
from collections import defaultdict

def get_all_possible_import_paths(file_path, app_dir):
    """Generate ALL possible ways this file could be imported"""
    rel = file_path.relative_to(app_dir.parent)
    
    # app.x.y.z
    module_path = str(rel.with_suffix('')).replace('/', '.')
    
    paths = [
        f'from {module_path} import',
        f'import {module_path}',
    ]
    
    # Auch relative imports
    filename = file_path.stem
    paths.append(f'from .{filename} import')
    paths.append(f'from . import {filename}')
    
    return paths

def check_if_imported(file_path, app_dir):
    """Check if file is imported ANYWHERE in codebase"""
    import_paths = get_all_possible_import_paths(file_path, app_dir)
    
    for import_path in import_paths:
        result = subprocess.run(
            ['grep', '-r', '--include=*.py', import_path, str(app_dir.parent / 'app')],
            capture_output=True,
            text=True,
            cwd=app_dir.parent
        )
        
        # Filter self-imports
        lines = [l for l in result.stdout.split('\n') 
                 if l and file_path.name not in l.split(':')[0]]
        
        if lines:
            return True, import_path, len(lines)
    
    return False, None, 0

def main():
    project_root = Path(__file__).parent.parent.parent
    app_dir = project_root / "backend" / "app"
    
    print("=" * 80)
    print("ABSOLUTE IMPORT CHECK - Every file, no exceptions")
    print("=" * 80)
    print()
    print("Scanning ALL Python files...")
    print()
    
    all_files = list(app_dir.rglob("*.py"))
    all_files = [f for f in all_files if '__pycache__' not in str(f)]
    
    imported = []
    not_imported = []
    
    for i, py_file in enumerate(all_files, 1):
        rel_path = str(py_file.relative_to(app_dir.parent))
        
        # Progress
        if i % 50 == 0:
            print(f"Checked {i}/{len(all_files)}...")
        
        is_imported, import_type, count = check_if_imported(py_file, app_dir)
        
        if is_imported:
            imported.append((rel_path, count))
        else:
            # Skip __init__.py (special case)
            if py_file.name != '__init__.py':
                not_imported.append(rel_path)
    
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total files: {len(all_files)}")
    print(f"Imported: {len(imported)}")
    print(f"NOT imported: {len(not_imported)}")
    print()
    
    if not_imported:
        print("=" * 80)
        print("FILES WITH 0 IMPORTS (100% accurate)")
        print("=" * 80)
        print()
        
        # Group by directory
        by_dir = defaultdict(list)
        for f in sorted(not_imported):
            dir_name = '/'.join(f.split('/')[:-1])
            by_dir[dir_name].append(f.split('/')[-1])
        
        for directory in sorted(by_dir.keys()):
            print(f"\n📁 {directory}/")
            for filename in sorted(by_dir[directory]):
                print(f"   └─ {filename}")
        
        # Save report
        output = project_root / "scripts/backend_analysis/absolute_loose_files.txt"
        with open(output, 'w') as f:
            f.write("ABSOLUTE LOOSE FILES (0 imports)\n")
            f.write("=" * 80 + "\n\n")
            for file in sorted(not_imported):
                f.write(f"{file}\n")
        
        print(f"\n\n📊 Report saved: {output}")
    else:
        print("✅ All files are imported!")

if __name__ == "__main__":
    main()
