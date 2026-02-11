#!/usr/bin/env python3
"""
Find duplicate code in backend/app/

Usage:
    cd /home/pascal/Lernsystem
    python3 scripts/backend_analysis/2_find_duplicates.py
"""

import hashlib
from pathlib import Path
from collections import defaultdict

def find_duplicates():
    print("=" * 70)
    print("  DUPLICATE CODE SCAN - backend/app/")
    print("=" * 70)
    print()
    
    project_root = Path(__file__).parent.parent.parent
    app_dir = project_root / "backend" / "app"
    
    if not app_dir.exists():
        print(f"❌ Error: {app_dir} not found!")
        return
    
    # Dict: hash -> list of files
    file_hashes = defaultdict(list)
    function_hashes = defaultdict(list)
    
    checked = 0
    
    print(f"📁 Scanning: {app_dir}")
    print()
    
    for py_file in app_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        checked += 1
        
        try:
            content = py_file.read_text()
            
            # 1. Vollständige Datei-Duplikate
            file_hash = hashlib.md5(content.encode()).hexdigest()
            rel_path = str(py_file.relative_to(project_root / "backend"))
            file_hashes[file_hash].append(rel_path)
            
            # 2. Funktions-Duplikate (einfache Heuristik)
            lines = content.split('\n')
            current_function = []
            function_name = None
            
            for line in lines:
                if line.strip().startswith('def '):
                    # Speichere vorherige Funktion
                    if current_function and function_name:
                        func_content = '\n'.join(current_function)
                        if len(func_content) > 100:  # Nur Funktionen >100 chars
                            func_hash = hashlib.md5(func_content.encode()).hexdigest()
                            function_hashes[func_hash].append((rel_path, function_name))
                    
                    # Starte neue Funktion
                    function_name = line.split('def ')[1].split('(')[0]
                    current_function = [line]
                elif current_function:
                    current_function.append(line)
            
        except Exception as e:
            print(f"⚠️  Warning: Could not read {py_file}: {e}")
    
    # Finde Duplikate
    duplicate_files = {h: files for h, files in file_hashes.items() if len(files) > 1}
    duplicate_functions = {h: funcs for h, funcs in function_hashes.items() if len(funcs) > 1}
    
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print(f"Files checked: {checked}")
    print(f"Duplicate files: {len(duplicate_files)}")
    print(f"Duplicate functions: {len(duplicate_functions)}")
    print()
    
    if duplicate_files:
        print("🔴 DUPLICATE FILES (100% identical):\n")
        for hash_val, files in duplicate_files.items():
            print(f"  Group (hash: {hash_val[:8]}):")
            for file in files:
                print(f"    - {file}")
            print()
    
    if duplicate_functions:
        print("🟡 DUPLICATE FUNCTIONS (>100 chars, identical):\n")
        count = 0
        for hash_val, funcs in duplicate_functions.items():
            if count >= 10:  # Limit output
                print(f"  ... and {len(duplicate_functions) - 10} more duplicate function groups")
                break
            print(f"  Function Group:")
            for file, func_name in funcs:
                print(f"    - {func_name}() in {file}")
            print()
            count += 1
    
    if not duplicate_files and not duplicate_functions:
        print("✅ No duplicates found - backend/app/ is clean!")
    
    # Save report
    output_file = project_root / "scripts" / "backend_analysis" / "duplicates_report.txt"
    with open(output_file, 'w') as f:
        f.write("DUPLICATE CODE REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        if duplicate_files:
            f.write("DUPLICATE FILES:\n\n")
            for hash_val, files in duplicate_files.items():
                f.write(f"Group (hash: {hash_val}):\n")
                for file in files:
                    f.write(f"  - {file}\n")
                f.write("\n")
        
        if duplicate_functions:
            f.write("DUPLICATE FUNCTIONS:\n\n")
            for hash_val, funcs in duplicate_functions.items():
                f.write("Function Group:\n")
                for file, func_name in funcs:
                    f.write(f"  - {func_name}() in {file}\n")
                f.write("\n")
    
    print(f"📊 Report saved to: {output_file}")

if __name__ == "__main__":
    find_duplicates()
