#!/bin/bash
# Wave 4: Update imports from admin/ai-operations & user/ai to ai/ (and exams to assessment/)

set -e

echo "🔄 Updating imports for Wave 4: AI Domain"

# Find all Vue and TypeScript files
find src -type f \( -name "*.vue" -o -name "*.ts" \) -print0 | while IFS= read -r -d '' file; do
  
  # Skip if file doesn't exist or is in node_modules
  [[ ! -f "$file" ]] && continue
  [[ "$file" =~ node_modules ]] && continue
  
  # Create backup
  cp "$file" "$file.tmp"
  
  # SPECIAL CASE: Exam settings → assessment domain
  sed -i "s|from '@/components/admin/ai-operations/settings/exams|from '@/components/assessment/admin/settings/exams|g" "$file.tmp"
  
  # Admin AI operations → ai/admin
  sed -i "s|from '@/components/admin/ai-operations/authoring|from '@/components/ai/admin/authoring|g" "$file.tmp"
  sed -i "s|from '@/components/admin/ai-operations/management|from '@/components/ai/admin/management|g" "$file.tmp"
  sed -i "s|from '@/components/admin/ai-operations/settings|from '@/components/ai/admin/settings|g" "$file.tmp"
  sed -i "s|from '@/components/admin/ai-operations/studio|from '@/components/ai/admin/studio|g" "$file.tmp"
  sed -i "s|from '@/components/admin/ai-operations|from '@/components/ai/admin|g" "$file.tmp"
  
  # User AI → ai/user
  sed -i "s|from '@/components/user/ai/chat|from '@/components/ai/user/chat|g" "$file.tmp"
  sed -i "s|from '@/components/user/ai/quiz-generation|from '@/components/ai/user/quiz-generation|g" "$file.tmp"
  sed -i "s|from '@/components/user/ai/tutor|from '@/components/ai/user/tutor|g" "$file.tmp"
  sed -i "s|from '@/components/user/ai|from '@/components/ai/user|g" "$file.tmp"
  
  # Check if file changed
  if ! cmp -s "$file" "$file.tmp"; then
    mv "$file.tmp" "$file"
    echo "  ✓ Updated: $file"
  else
    rm "$file.tmp"
  fi
done

echo "✅ Wave 4 import updates complete!"
