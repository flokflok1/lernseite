#!/bin/bash
echo "════════════════════════════════════════════════════════"
echo "  LEGACY BRIDGE MIGRATION VERIFICATION"
echo "════════════════════════════════════════════════════════"
echo ""

cd backend

echo "🔍 Checking for old import patterns..."
echo ""

OLD_IMPORTS=0

# Check alte Imports
patterns=("ai_adapter" "ai_job_service" "audit_service" "tts_service" "i18n_service" "permission_service")

for pattern in "${patterns[@]}"; do
  count=$(grep -r "from app.application.services.$pattern import" app/ 2>/dev/null | wc -l)
  if [ $count -gt 0 ]; then
    echo "❌ $pattern: $count remaining"
    OLD_IMPORTS=$((OLD_IMPORTS + count))
  else
    echo "✅ $pattern: migrated"
  fi
done

echo ""
echo "🔍 Checking new imports..."
echo ""

NEW_IMPORTS=0
NEW_IMPORTS=$((NEW_IMPORTS + $(grep -r "from app.application.services.ai.adapter import" app/ 2>/dev/null | wc -l)))
NEW_IMPORTS=$((NEW_IMPORTS + $(grep -r "from app.application.services.system.audit.service import" app/ 2>/dev/null | wc -l)))

echo "✅ New organized imports found: $NEW_IMPORTS"

echo ""
echo "════════════════════════════════════════════════════════"
if [ $OLD_IMPORTS -eq 0 ]; then
  echo "✅ ✅ ✅  MIGRATION COMPLETE!"
else
  echo "⚠️  $OLD_IMPORTS old imports remaining"
fi
echo "════════════════════════════════════════════════════════"
