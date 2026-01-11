#!/usr/bin/env python3
"""Test all imports after Phase 8 refactoring"""

print("Testing Phase 8 imports...")
print("=" * 60)

# Test tokens package
try:
    from app.api.tokens import wallet, transactions, stats, admin
    print("✅ tokens package imports OK")
    print("   - wallet, transactions, stats, admin")
except Exception as e:
    print(f"❌ tokens package import FAILED: {e}")

# Test math package
try:
    from app.api.math import reference, calculator, sessions, interactive
    print("✅ math package imports OK")
    print("   - reference, calculator, sessions, interactive")
except Exception as e:
    print(f"❌ math package import FAILED: {e}")

# Test admin.content_management.courses package
try:
    from app.api.admin.content_management.courses import crud, chapters, lessons, exams, prompts, files
    print("✅ admin.content_management.courses package imports OK")
    print("   - crud, chapters, lessons, exams, prompts, files")
except Exception as e:
    print(f"❌ admin.content_management.courses package import FAILED: {e}")

# Test admin.ai_operations package (proxy to system_features/ai/)
try:
    from app.api.admin.ai_operations import jobs_bp, pricing_bp
    print("✅ admin.ai_operations package imports OK")
    print("   - jobs_bp, pricing_bp")
except Exception as e:
    print(f"❌ admin.ai_operations package import FAILED: {e}")

# Test admin.system_operations.system package
try:
    from app.api.admin.system_operations.system import settings
    print("✅ admin.system_operations.system package imports OK")
    print("   - settings")
except Exception as e:
    print(f"❌ admin.system_operations.system package import FAILED: {e}")

# Test main API package (blueprint is api_v1, not individual *_bp)
try:
    from app.api import api_v1
    print("✅ app.api package imports OK")
    print(f"   - api_v1 blueprint: {api_v1.name}")
except Exception as e:
    print(f"❌ app.api package import FAILED: {e}")

print("=" * 60)
print("\nImport test complete!")
