#!/usr/bin/env python3
"""
Find large/complex files that violate G01 rule (>500 LOC)

Usage:
    cd /home/pascal/Lernsystem
    python3 scripts/backend_analysis/3_check_complexity.py
"""

from pathlib import Path

def check_complexity():
    print("=" * 70)
    print("  COMPLEXITY CHECK - backend/app/ (G01 Rule: max 500 LOC)")
    print("=" * 70)
    print()
    
    project_root = Path(__file__).parent.parent.parent
    app_dir = project_root / "backend" / "app"
    
    if not app_dir.exists():
        print(f"❌ Error: {app_dir} not found!")
        return
    
    violations = []
    checked = 0
    
    for py_file in app_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        checked += 1
        
        try:
            lines = py_file.read_text().splitlines()
            loc = len(lines)
            
            if loc > 500:
                rel_path = str(py_file.relative_to(project_root / "backend"))
                violations.append({
                    'path': rel_path,
                    'lines': loc,
                    'overage': loc - 500
                })
        except Exception as e:
            print(f"⚠️  Warning: Could not read {py_file}: {e}")
    
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print(f"Files checked: {checked}")
    print(f"G01 violations (>500 LOC): {len(violations)}")
    print()
    
    if violations:
        print("🔴 FILES EXCEEDING 500 LOC:\n")
        for file in sorted(violations, key=lambda x: x['lines'], reverse=True):
            print(f"  📄 {file['path']}")
            print(f"     └─ {file['lines']} lines (+{file['overage']} over limit)")
            print()
        
        # Save report
        output_file = project_root / "scripts" / "backend_analysis" / "complexity_report.txt"
        with open(output_file, 'w') as f:
            f.write("COMPLEXITY REPORT (G01 Violations)\n")
            f.write("=" * 70 + "\n\n")
            for file in sorted(violations, key=lambda x: x['lines'], reverse=True):
                f.write(f"{file['path']}\n")
                f.write(f"  Lines: {file['lines']} (+{file['overage']} over limit)\n\n")
        
        print(f"📊 Report saved to: {output_file}")
    else:
        print("✅ No G01 violations - all files under 500 LOC!")

if __name__ == "__main__":
    check_complexity()
