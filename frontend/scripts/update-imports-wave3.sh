#!/bin/bash
# Wave 3: Update imports from admin/content-management & user/courses to content/

set -e

echo "🔄 Updating imports for Wave 3: Content Domain"

# Find all Vue and TypeScript files
find src -type f \( -name "*.vue" -o -name "*.ts" \) -print0 | while IFS= read -r -d '' file; do
  
  # Skip if file doesn't exist or is in node_modules
  [[ ! -f "$file" ]] && continue
  [[ "$file" =~ node_modules ]] && continue
  
  # Create backup
  cp "$file" "$file.tmp"
  
  # Admin content-management → content/admin
  sed -i "s|from '@/components/admin/content-management/categories|from '@/components/content/admin/categories|g" "$file.tmp"
  sed -i "s|from '@/components/admin/content-management/chapters|from '@/components/content/admin/chapters|g" "$file.tmp"
  sed -i "s|from '@/components/admin/content-management/courses|from '@/components/content/admin/courses|g" "$file.tmp"
  sed -i "s|from '@/components/admin/content-management/editor|from '@/components/content/admin/editor|g" "$file.tmp"
  sed -i "s|from '@/components/admin/content-management/learning-methods|from '@/components/content/admin/learning-methods|g" "$file.tmp"
  sed -i "s|from '@/components/admin/content-management/lessons|from '@/components/content/admin/lessons|g" "$file.tmp"
  sed -i "s|from '@/components/admin/content-management/shared|from '@/components/content/shared|g" "$file.tmp"
  
  # User courses → content/user/courses
  sed -i "s|from '@/components/user/courses/CourseCard|from '@/components/content/user/courses|g" "$file.tmp"
  sed -i "s|from '@/components/user/courses/EnrolledCourseCard|from '@/components/content/user/courses|g" "$file.tmp"
  sed -i "s|from '@/components/user/courses/overview|from '@/components/content/user/courses/overview|g" "$file.tmp"
  sed -i "s|from '@/components/user/courses|from '@/components/content/user/courses|g" "$file.tmp"
  
  # User chapters → content/user/chapters
  sed -i "s|from '@/components/user/chapters|from '@/components/content/user/chapters|g" "$file.tmp"
  
  # Check if file changed
  if ! cmp -s "$file" "$file.tmp"; then
    mv "$file.tmp" "$file"
    echo "  ✓ Updated: $file"
  else
    rm "$file.tmp"
  fi
done

echo "✅ Wave 3 import updates complete!"
