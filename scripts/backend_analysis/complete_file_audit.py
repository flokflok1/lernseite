
#!/usr/bin/env python3
"""Complete file audit - categorize EVERY file"""

import os
from pathlib import Path
import subprocess
import re

def analyze_file(file_path, app_dir):
    """Determine file category and action"""
    rel_path = file_path.relative_to(app_dir.parent)
    
    # Read content
    try:
        content = file_path.read_text()
    except:
        return None, "unreadable"
    
    # Category checks
    is_init = file_path.name == "__init__.py"
    is_blueprint = bool(re.search(r'Blueprint\(|@\w+\.route\(|register_blueprint', content))
    is_model = '/models/' in str(file_path) or 'Base = declarative_base' in content or 'class.*\(Base\)' in content
    is_repository = '/repositories/' in str(file_path) or 'Repository' in file_path.name
    is_service = '/services/' in str(file_path) or 'Service' in file_path.name
    has_imports = bool(subprocess.run(
        ['grep', '-r', f'from {str(rel_path.with_suffix("")).replace("/", ".")} import', 
         str(app_dir.parent / 'app')],
        capture_output=True, text=True
    ).stdout.strip())
    
    # Decision logic
    if is_init:
        return "keep", "init_file"
    elif is_blueprint:
        return "keep", "blueprint"
    elif is_model:
        return "keep", "model"
    elif has_imports:
        return "keep", "imported"
    elif is_repository:
        return "archive", "unused_repository"
    elif is_service:
        return "archive", "unused_service"
    else:
        return "review", "unknown"

project_root = Path(__file__).parent.parent.parent
app_dir = project_root / "backend" / "app"

results = {
    'keep': [],
    'archive': [],
    'review': [],
}

for py_file in app_dir.rglob("*.py"):
    if "__pycache__" in str(py_file):
        continue
    
    action, reason = analyze_file(py_file, app_dir)
    if action:
        results[action].append((str(py_file.relative_to(project_root / "backend")), reason))

print("=" * 70)
print("COMPLETE FILE AUDIT")
print("=" * 70)
print()

for action, files in results.items():
    print(f"\n{action.upper()} ({len(files)} files):")
    for f, reason in sorted(files)[:20]:
        print(f"  {reason:20} {f}")
    if len(files) > 20:
        print(f"  ... and {len(files) - 20} more")

print(f"\n\nTotal: {sum(len(f) for f in results.values())} files")
