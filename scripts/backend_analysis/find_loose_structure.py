#!/usr/bin/env python3
"""Find directories with many .py files that should be reorganized into subdirectories"""

from pathlib import Path
from collections import defaultdict

def analyze_directory_structure():
    project_root = Path(__file__).parent.parent.parent
    app_dir = project_root / "backend" / "app"
    
    # Find all directories with Python files
    dir_files = defaultdict(list)
    
    for py_file in app_dir.rglob("*.py"):
        if '__pycache__' in str(py_file) or py_file.name == '__init__.py':
            continue
        
        parent = py_file.parent
        rel_parent = parent.relative_to(app_dir)
        dir_files[str(rel_parent)].append(py_file.name)
    
    print("=" * 80)
    print("DIRECTORIES WITH MULTIPLE FILES (Reorganization Candidates)")
    print("=" * 80)
    print()
    
    # Sort by file count
    sorted_dirs = sorted(dir_files.items(), key=lambda x: len(x[1]), reverse=True)
    
    reorganize_candidates = []
    
    for directory, files in sorted_dirs:
        if len(files) >= 3:  # 3+ files = candidate for reorganization
            print(f"\n📁 {directory}/ ({len(files)} files)")
            
            # Show first 10 files
            for f in sorted(files)[:10]:
                print(f"   └─ {f}")
            if len(files) > 10:
                print(f"   ... and {len(files) - 10} more")
            
            reorganize_candidates.append((directory, files))
    
    print("\n" + "=" * 80)
    print(f"Total directories needing reorganization: {len(reorganize_candidates)}")
    print("=" * 80)
    
    # Save detailed report
    output = project_root / "scripts/backend_analysis/reorganization_plan.txt"
    with open(output, 'w') as f:
        f.write("BACKEND REORGANIZATION CANDIDATES\n")
        f.write("=" * 80 + "\n\n")
        
        for directory, files in reorganize_candidates:
            f.write(f"\n{directory}/ ({len(files)} files)\n")
            f.write("-" * 80 + "\n")
            for file in sorted(files):
                f.write(f"  {file}\n")
    
    print(f"\n📊 Detailed report: {output}")

if __name__ == "__main__":
    analyze_directory_structure()
