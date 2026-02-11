#!/usr/bin/env python3
"""
Run all backend analysis scripts

Usage:
    cd /home/pascal/Lernsystem
    python3 scripts/backend_analysis/run_all.py
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_name, description):
    print("\n" + "=" * 70)
    print(f"  Running: {description}")
    print("=" * 70 + "\n")
    
    script_path = Path(__file__).parent / script_name
    result = subprocess.run([sys.executable, str(script_path)])
    
    return result.returncode == 0

def main():
    print("=" * 70)
    print("  BACKEND ANALYSIS - FULL SCAN")
    print("=" * 70)
    
    scripts = [
        ("1_find_loose_files.py", "Loose Files (0 imports)"),
        ("2_find_duplicates.py", "Duplicate Code"),
        ("3_check_complexity.py", "Complexity (G01 violations)"),
    ]
    
    results = {}
    
    for script, description in scripts:
        success = run_script(script, description)
        results[description] = "✅ PASS" if success else "❌ FAIL"
    
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    
    for description, result in results.items():
        print(f"{result}  {description}")
    
    print("\n📊 All reports saved to: scripts/backend_analysis/")

if __name__ == "__main__":
    main()
