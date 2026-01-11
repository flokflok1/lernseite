#!/bin/bash
# Wave 1 Import Update Script
# Updates all imports for components moved from /base/ to feature domains

echo "🔄 Wave 1: Updating import paths..."
echo ""

# Counter for updated files
UPDATED=0

# Find all .vue, .ts, .tsx files
find src -type f \( -name "*.vue" -o -name "*.ts" -o -name "*.tsx" \) -print0 | while IFS= read -r -d '' file; do
  CHANGED=0
  
  # Create temp file
  cp "$file" "$file.tmp"
  
  # Wave 1: Base cleanup - Lessons to learning/methods/
  sed -i "s|from '@/components/base/lessons/TextLesson'|from '@/components/learning/methods'|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/VideoLesson'|from '@/components/learning/methods'|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/AiLesson'|from '@/components/learning/methods'|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/OralExplanationLesson'|from '@/components/learning/methods'|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/WhiteboardTutorLesson'|from '@/components/learning/methods'|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/MethodExecutionPanel'|from '@/components/learning/methods'|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/DetailedSteps'|from '@/components/learning/methods'|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/MathTaskModal'|from '@/components/learning/methods'|g" "$file.tmp"
  
  # Quiz components
  sed -i "s|from '@/components/base/lessons/quiz|from '@/components/learning/methods/quiz|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/QuizLesson'|from '@/components/learning/methods'|g" "$file.tmp"
  sed -i "s|from '@/components/base/lessons/QuizResult'|from '@/components/learning/methods'|g" "$file.tmp"
  
  # Method execution
  sed -i "s|from '@/components/base/lessons/method-execution|from '@/components/learning/methods/method-execution|g" "$file.tmp"
  
  # Widgets to dashboard/widgets/
  sed -i "s|from '@/components/base/widgets/CoursesProgressWidget'|from '@/components/dashboard/widgets'|g" "$file.tmp"
  sed -i "s|from '@/components/base/widgets/EnrolledCoursesWidget'|from '@/components/dashboard/widgets'|g" "$file.tmp"
  sed -i "s|from '@/components/base/widgets/WelcomeWidget'|from '@/components/dashboard/widgets'|g" "$file.tmp"
  sed -i "s|from '@/components/base/widgets/PlanTokensWidget'|from '@/components/dashboard/widgets'|g" "$file.tmp"
  sed -i "s|from '@/components/base/widgets/OrgOverviewWidget'|from '@/components/dashboard/widgets'|g" "$file.tmp"
  sed -i "s|from '@/components/base/widgets/ProfileSummaryWidget'|from '@/components/dashboard/widgets'|g" "$file.tmp"
  sed -i "s|from '@/components/base/widgets'|from '@/components/dashboard/widgets'|g" "$file.tmp"
  
  # Charts to analytics/charts/
  sed -i "s|from '@/components/base/charts/AnalyticsKpiCard'|from '@/components/analytics/charts'|g" "$file.tmp"
  sed -i "s|from '@/components/base/charts/BarChart'|from '@/components/analytics/charts'|g" "$file.tmp"
  sed -i "s|from '@/components/base/charts/LineChart'|from '@/components/analytics/charts'|g" "$file.tmp"
  sed -i "s|from '@/components/base/charts'|from '@/components/analytics/charts'|g" "$file.tmp"
  
  # Application interface to layout/
  sed -i "s|from '@/components/base/application-interface/DesktopLayer'|from '@/components/layout'|g" "$file.tmp"
  sed -i "s|from '@/components/base/application-interface/WindowComponent'|from '@/components/layout'|g" "$file.tmp"
  sed -i "s|from '@/components/base/application-interface/Taskbar'|from '@/components/layout'|g" "$file.tmp"
  sed -i "s|from '@/components/base/application-interface/MiniPreview'|from '@/components/layout'|g" "$file.tmp"
  sed -i "s|from '@/components/base/application-interface'|from '@/components/layout'|g" "$file.tmp"
  
  # Layout to layout/
  sed -i "s|from '@/components/base/layout/Footer'|from '@/components/layout'|g" "$file.tmp"
  sed -i "s|from '@/components/base/layout/ProtectedContent'|from '@/components/layout'|g" "$file.tmp"
  sed -i "s|from '@/components/base/layout'|from '@/components/layout'|g" "$file.tmp"
  
  # Dialogs to system/shared/dialogs/
  sed -i "s|from '@/components/base/dialogs/DeleteConfirmModal'|from '@/components/system/shared/dialogs'|g" "$file.tmp"
  sed -i "s|from '@/components/base/dialogs/DialogManager'|from '@/components/system/shared/dialogs'|g" "$file.tmp"
  sed -i "s|from '@/components/base/dialogs/TaskManagerModal'|from '@/components/system/shared/dialogs'|g" "$file.tmp"
  sed -i "s|from '@/components/base/dialogs'|from '@/components/system/shared/dialogs'|g" "$file.tmp"
  
  # Ads to layout/ads/
  sed -i "s|from '@/components/base/ads/AdSlot'|from '@/components/layout/ads'|g" "$file.tmp"
  sed -i "s|from '@/components/base/ads'|from '@/components/layout/ads'|g" "$file.tmp"
  
  # Audio to learning/audio/
  sed -i "s|from '@/components/base/audio/AudioRecorder'|from '@/components/learning/audio'|g" "$file.tmp"
  sed -i "s|from '@/components/base/audio'|from '@/components/learning/audio'|g" "$file.tmp"
  
  # i18n to layout/i18n/
  sed -i "s|from '@/components/base/i18n/LanguageSelector'|from '@/components/layout/i18n'|g" "$file.tmp"
  sed -i "s|from '@/components/base/i18n'|from '@/components/layout/i18n'|g" "$file.tmp"
  
  # Check if file changed
  if ! cmp -s "$file" "$file.tmp"; then
    mv "$file.tmp" "$file"
    UPDATED=$((UPDATED + 1))
    echo "✓ Updated: $file"
  else
    rm "$file.tmp"
  fi
done

echo ""
echo "✅ Import update complete!"
echo "📊 Files updated: $UPDATED"
