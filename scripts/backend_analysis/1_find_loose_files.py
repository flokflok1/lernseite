#!/usr/bin/env python3
"""
Find Python files with 0 imports in backend/app/

Usage:
    cd /home/pascal/Lernsystem
    python3 scripts/backend_analysis/1_find_loose_files.py
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

def find_loose_files():
    print("=" * 70)
    print("  LOOSE FILES SCAN - backend/app/")
    print("=" * 70)
    print()
    
    # Navigate to project root
    project_root = Path(__file__).parent.parent.parent
    app_dir = project_root / "backend" / "app"
    
    if not app_dir.exists():
        print(f"❌ Error: {app_dir} not found!")
        return
    
    os.chdir(project_root / "backend")
    
    loose_files = []
    checked = 0
    
    print(f"📁 Scanning: {app_dir}")
    print()
    
    for py_file in app_dir.rglob("*.py"):
        # Skip __init__.py und __pycache__
        if py_file.name == "__init__.py" or "__pycache__" in str(py_file):
            continue
        
        checked += 1
        
        # Konvertiere zu Modul-Pfad
        rel_path = py_file.relative_to(project_root / "backend")
        module_path = str(rel_path.with_suffix("")).replace("/", ".")
        filename = py_file.stem
        
        # Suche nach Imports (verschiedene Varianten)
        patterns = [
            f'from {module_path} import',
            f'import {module_path}',
            f'from .{filename} import',
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
                # Filtere die Datei selbst raus
                imports = [line for line in result.stdout.split('\n') 
                          if line and str(py_file.name) not in line.split(':')[0]]
                import_count += len(imports)
            except Exception:
                pass
        
        if import_count == 0:
            try:
                lines = len(py_file.read_text().splitlines())
                size = py_file.stat().st_size
                modified = datetime.fromtimestamp(py_file.stat().st_mtime)
                
                loose_files.append({
                    'path': str(rel_path),
                    'lines': lines,
                    'size': size,
                    'modified': modified.strftime("%Y-%m-%d")
                })
            except Exception as e:
                print(f"⚠️  Warning: Could not read {py_file}: {e}")
    
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print(f"Files checked: {checked}")
    print(f"Loose files found: {len(loose_files)}")
    print()
    
    if loose_files:
        print("🔴 Files with 0 imports:\n")
        for file in sorted(loose_files, key=lambda x: x['lines']):
            size_info = f"{file['lines']} lines"
            if file['lines'] < 10:
                size_info = f"SMALL ({file['lines']} lines)"
            elif file['lines'] > 500:
                size_info = f"LARGE ({file['lines']} lines)"
            
            print(f"  📄 {file['path']}")
            print(f"     └─ {size_info} | {file['size']} bytes | Modified: {file['modified']}")
            print()
        
        # Export results
        output_file = project_root / "scripts" / "backend_analysis" / "loose_files_report.txt"
        with open(output_file, 'w') as f:
            f.write("LOOSE FILES REPORT\n")
            f.write("=" * 70 + "\n\n")
            for file in sorted(loose_files, key=lambda x: x['lines']):
                f.write(f"{file['path']}\n")
                f.write(f"  Lines: {file['lines']}\n")
                f.write(f"  Size: {file['size']} bytes\n")
                f.write(f"  Modified: {file['modified']}\n\n")
        
        print(f"📊 Report saved to: {output_file}")
    else:
        print("✅ No loose files found - backend/app/ is clean!")

if __name__ == "__main__":
    find_loose_files()
