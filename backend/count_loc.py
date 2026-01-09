#!/usr/bin/env python3
"""Quick LOC counter for split verification."""

import sys
from pathlib import Path

files = [
    # prompts/registry
    "app/ki/prompts/registry/__init__.py",
    "app/ki/prompts/registry/core.py",
    "app/ki/prompts/registry/db_override.py",
    "app/ki/prompts/registry/retrieval.py",
    "app/ki/prompts/registry/initialization.py",
    # prompts/ai_studio
    "app/ki/prompts/ai_studio/__init__.py",
    "app/ki/prompts/ai_studio/_base.py",
    "app/ki/prompts/ai_studio/source.py",
    "app/ki/prompts/ai_studio/theory.py",
    "app/ki/prompts/ai_studio/lessons.py",
    "app/ki/prompts/ai_studio/methods.py",
    "app/ki/prompts/ai_studio/review.py",
    "app/ki/prompts/ai_studio/finalize.py",
    # slots
    "app/ki/slots/__init__.py",
    "app/ki/slots/requirements.py",
    "app/ki/slots/validation.py",
    "app/ki/slots/mapping.py",
    "app/ki/slots/capabilities.py",
]

print("=" * 80)
print("LOC Count - KI Service Layer Splits")
print("=" * 80)

totals = {}
grand_total = 0

for rel_path in files:
    path = Path(rel_path)
    if not path.exists():
        print(f"❌ {rel_path:55s} NOT FOUND")
        continue

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    loc = len(lines)
    grand_total += loc

    # Group by package
    parts = rel_path.split('/')
    if len(parts) >= 4:
        package = f"{parts[2]}/{parts[3]}"
    else:
        package = parts[2] if len(parts) > 2 else "unknown"

    totals[package] = totals.get(package, 0) + loc

    status = "✅" if loc <= 500 else "❌"
    print(f"{status} {rel_path:55s} {loc:4d} LOC")

print("\n" + "=" * 80)
print("Summary by Package")
print("=" * 80)

for package, loc in sorted(totals.items()):
    print(f"  {package:35s} {loc:5d} LOC")

print(f"\n  {'TOTAL':35s} {grand_total:5d} LOC")
print("=" * 80)

# Check for violations
violations = [f for f in files if Path(f).exists() and len(open(f).readlines()) > 500]
if violations:
    print(f"\n❌ {len(violations)} file(s) exceed 500 LOC limit")
    sys.exit(1)
else:
    print("\n✅ All files within 500 LOC limit")
    sys.exit(0)
