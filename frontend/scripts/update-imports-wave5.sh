#!/bin/bash
# Wave 5: Update imports for remaining domains

set -e

echo "🔄 Updating imports for Wave 5: Remaining Domains"

# Find all Vue and TypeScript files
find src -type f \( -name "*.vue" -o -name "*.ts" \) -print0 | while IFS= read -r -d '' file; do
  
  # Skip if file doesn't exist or is in node_modules
  [[ ! -f "$file" ]] && continue
  [[ "$file" =~ node_modules ]] && continue
  
  # Create backup
  cp "$file" "$file.tmp"
  
  # Dashboard: user/dashboard → dashboard/user
  sed -i "s|from '@/components/user/dashboard/DashboardWidgetsArea'|from '@/components/dashboard'|g" "$file.tmp"
  sed -i "s|from '@/components/user/dashboard/WidgetConfigPanel'|from '@/components/dashboard'|g" "$file.tmp"
  sed -i "s|from '@/components/user/dashboard|from '@/components/dashboard/user|g" "$file.tmp"
  
  # Analytics: user/analytics → analytics/user
  sed -i "s|from '@/components/user/analytics|from '@/components/analytics/user|g" "$file.tmp"
  
  # Assessment: admin/assessment → assessment/admin, user/exams → assessment/user
  sed -i "s|from '@/components/admin/assessment/exams|from '@/components/assessment/admin/exams|g" "$file.tmp"
  sed -i "s|from '@/components/admin/assessment/views|from '@/components/assessment/admin/views|g" "$file.tmp"
  sed -i "s|from '@/components/admin/assessment|from '@/components/assessment/admin|g" "$file.tmp"
  sed -i "s|from '@/components/user/exams|from '@/components/assessment/user|g" "$file.tmp"
  
  # Gamification: user/gamification → gamification
  sed -i "s|from '@/components/user/gamification|from '@/components/gamification|g" "$file.tmp"
  
  # Users: admin/user-management → users/admin
  sed -i "s|from '@/components/admin/user-management/roles|from '@/components/users/admin/roles|g" "$file.tmp"
  sed -i "s|from '@/components/admin/user-management|from '@/components/users/admin|g" "$file.tmp"
  
  # System: admin/system-operations → system/admin, admin/shared → system/shared
  sed -i "s|from '@/components/admin/system-operations/settings|from '@/components/system/admin/settings|g" "$file.tmp"
  sed -i "s|from '@/components/admin/system-operations/views|from '@/components/system/admin/views|g" "$file.tmp"
  sed -i "s|from '@/components/admin/system-operations/SystemStatus'|from '@/components/system'|g" "$file.tmp"
  sed -i "s|from '@/components/admin/system-operations|from '@/components/system/admin|g" "$file.tmp"
  sed -i "s|from '@/components/admin/shared/dialogs|from '@/components/system/shared/dialogs|g" "$file.tmp"
  sed -i "s|from '@/components/admin/shared/previews|from '@/components/system/shared/previews|g" "$file.tmp"
  sed -i "s|from '@/components/admin/shared/StatsCard'|from '@/components/system'|g" "$file.tmp"
  sed -i "s|from '@/components/admin/shared|from '@/components/system/shared|g" "$file.tmp"
  
  # System Features: user/system-features → system-features
  sed -i "s|from '@/components/user/system-features|from '@/components/system-features|g" "$file.tmp"
  
  # Check if file changed
  if ! cmp -s "$file" "$file.tmp"; then
    mv "$file.tmp" "$file"
    echo "  ✓ Updated: $file"
  else
    rm "$file.tmp"
  fi
done

echo "✅ Wave 5 import updates complete!"
