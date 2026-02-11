
#!/bin/bash

echo "════════════════════════════════════════════════════════"
echo "  LEGACY BRIDGE MIGRATION SCAN"
echo "════════════════════════════════════════════════════════"
echo ""

cd backend

# Liste aller Legacy Bridges
bridges=(
  "ai_adapter"
  "ai_job_service"
  "audit_service"
  "content_translation_service"
  "course_authoring_service"
  "course_ai_settings_service"
  "feature_configuration_service"
  "feature_configuration_ab_test"
  "feature_configuration_rollout"
  "file_context_service"
  "i18n_service"
  "math_toolkit_service"
  "permission_service"
  "prompt_resolver"
  "tts_service"
)

for bridge in "${bridges[@]}"; do
  echo "─────────────────────────────────────────────────────────"
  echo "🔍 $bridge"
  echo "─────────────────────────────────────────────────────────"
  
  # Finde Usages (ohne legacy_bridges selbst)
  usages=$(grep -r "from app.application.services.$bridge import" app/ --include="*.py" 2>/dev/null | grep -v "_legacy_bridges" | wc -l)
  
  if [ $usages -gt 0 ]; then
    echo "📊 Usages: $usages"
    grep -r "from app.application.services.$bridge import" app/ --include="*.py" 2>/dev/null | grep -v "_legacy_bridges"
  else
    echo "📊 Usages: 0 (UNUSED!)"
  fi
  
  # Suche moderne Alternative
  echo ""
  echo "🔎 Searching for modern equivalent..."
  
  # Entferne _service suffix für Suche
  base_name=$(echo "$bridge" | sed 's/_service$//' | sed 's/_adapter$//')
  
  # Suche in application/services/
  modern=$(find app/application/services -name "*${base_name}*.py" -type f 2>/dev/null | grep -v legacy | grep -v __pycache__)
  
  if [ ! -z "$modern" ]; then
    echo "✅ Found modern service:"
    echo "   $modern"
  else
    echo "❓ No obvious modern equivalent found"
  fi
  
  echo ""
done

echo "════════════════════════════════════════════════════════"
echo "  SCAN COMPLETE"
echo "════════════════════════════════════════════════════════"
