#!/bin/bash
# Component Restructuring Script
# Reorganizes components from chaotic structure to Feature-Based DDD

set -e

COMP_DIR="/home/pascal/Lernsystem/frontend/src/presentation/components"
BACKUP_DIR="/home/pascal/Lernsystem/frontend/.component-backup-$(date +%Y%m%d_%H%M%S)"

echo "=== LernsystemX Component Restructuring ==="
echo "Source: $COMP_DIR"
echo "Backup: $BACKUP_DIR"
echo ""

# Create backup
echo "1. Creating backup..."
cp -r "$COMP_DIR" "$BACKUP_DIR"
echo "   Backup created at $BACKUP_DIR"

# Create new structure
echo "2. Creating new feature-based structure..."

# Main feature folders (keeping existing ones that are correct)
mkdir -p "$COMP_DIR/ai/admin/studio"
mkdir -p "$COMP_DIR/ai/admin/models"
mkdir -p "$COMP_DIR/ai/admin/prompts"
mkdir -p "$COMP_DIR/ai/user/tutor"
mkdir -p "$COMP_DIR/ai/shared"

mkdir -p "$COMP_DIR/content/admin/courses"
mkdir -p "$COMP_DIR/content/admin/chapters"
mkdir -p "$COMP_DIR/content/admin/lessons"
mkdir -p "$COMP_DIR/content/user"
mkdir -p "$COMP_DIR/content/shared"

mkdir -p "$COMP_DIR/learning/methods"
mkdir -p "$COMP_DIR/learning/execution"
mkdir -p "$COMP_DIR/learning/shared"

mkdir -p "$COMP_DIR/shared/ui"
mkdir -p "$COMP_DIR/shared/layout"
mkdir -p "$COMP_DIR/shared/windows"
mkdir -p "$COMP_DIR/shared/types"
mkdir -p "$COMP_DIR/shared/composables"

echo "   Feature folders created"

# Move loose .vue files to appropriate locations
echo "3. Moving loose Vue components..."

# AI/Tutor related
for f in TutorAvatar.vue TutorCompanion.vue TutorTab.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/ai/user/tutor/" && echo "   Moved $f -> ai/user/tutor/"
done

# AI/Models related
for f in ModelCard.vue ModelConfigCard.vue ModelSelector.vue ModelSelectorWindow.vue ModelsFilter.vue ModelsHeader.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/ai/admin/models/" && echo "   Moved $f -> ai/admin/models/"
done

# AI/Prompts related
for f in PromptBrowser.vue PromptEditor.vue PromptsTab.vue PromptTemplatesList.vue TestPromptModal.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/ai/admin/prompts/" && echo "   Moved $f -> ai/admin/prompts/"
done

# AI/Studio related
for f in SettingsTab.vue StatsTab.vue StatsOverview.vue SystemFeaturesTab.vue StructurePanel.vue WorkflowPanel.vue TeachingStepsPanel.vue TypesPanel.vue ScopeSelector.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/ai/admin/studio/" && echo "   Moved $f -> ai/admin/studio/"
done

# AI/Providers
for f in ProviderGrid.vue ProviderRow.vue SyncResultBanner.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/ai/admin/models/" && echo "   Moved $f -> ai/admin/models/"
done

# Learning methods
for f in OralExplanationLesson.vue PeerInstruction.vue PeerReview.vue PracticalExamEngine.vue ProjectBasedLearning.vue ProjectPortfolio.vue TeamCase.vue SpeechToText.vue WhiteboardEngine.vue TimerWrapper.vue OnScreenCalculator.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/learning/methods/" && echo "   Moved $f -> learning/methods/"
done

# Preview components -> content
for f in PreviewAIJob.vue PreviewCourseCreate.vue PreviewCourseEditor.vue PreviewKapitelEditor.vue PreviewLessonEditor.vue MiniPreview.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/content/admin/courses/" && echo "   Moved $f -> content/admin/courses/"
done

# Profile related -> ai/admin/models (AI model profiles)
for f in ProfileEditor.vue ProfileList.vue ProfileSelector.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/ai/admin/models/" && echo "   Moved $f -> ai/admin/models/"
done

# Window/Desktop components -> shared/windows
for f in WindowComponent.vue WindowManagerWindow.vue Taskbar.vue; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/shared/windows/" && echo "   Moved $f -> shared/windows/"
done

# Move loose .ts files
echo "4. Moving loose TypeScript files..."

# Types
for f in action.types.ts course.types.ts file.types.ts lm.types.ts session.types.ts sync.types.ts theory.types.ts; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/shared/types/" && echo "   Moved $f -> shared/types/"
done

# Composables
for f in useAiStudioState.ts useChapterDetail.ts useChatManagement.ts useCourseDetail.ts useCourseManagement.ts useCourseOverview.ts useExplanationManager.ts useMethodExecution.ts useRolesManagement.ts useTabManagement.ts; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/shared/composables/" && echo "   Moved $f -> shared/composables/"
done

# Avatar related -> ai/user/tutor
for f in AnimationController.ts HumanAvatarBuilder.ts use3DAvatar.ts VRMAvatarLoader.ts; do
    [ -f "$COMP_DIR/$f" ] && mv "$COMP_DIR/$f" "$COMP_DIR/ai/user/tutor/" && echo "   Moved $f -> ai/user/tutor/"
done

echo "5. Consolidating existing folders..."

# Move base/* -> shared/ui/
if [ -d "$COMP_DIR/base" ]; then
    mv "$COMP_DIR/base"/* "$COMP_DIR/shared/ui/" 2>/dev/null || true
    rmdir "$COMP_DIR/base" 2>/dev/null || true
    echo "   Merged base/ -> shared/ui/"
fi

# Move layout/* -> shared/layout/
if [ -d "$COMP_DIR/layout" ] && [ -d "$COMP_DIR/shared/layout" ]; then
    mv "$COMP_DIR/layout"/* "$COMP_DIR/shared/layout/" 2>/dev/null || true
    rmdir "$COMP_DIR/layout" 2>/dev/null || true
    echo "   Merged layout/ -> shared/layout/"
fi

# Move core/* -> shared/ (core utilities)
if [ -d "$COMP_DIR/core" ]; then
    mkdir -p "$COMP_DIR/shared/core"
    mv "$COMP_DIR/core"/* "$COMP_DIR/shared/core/" 2>/dev/null || true
    rmdir "$COMP_DIR/core" 2>/dev/null || true
    echo "   Merged core/ -> shared/core/"
fi

# Merge features/ into appropriate feature folders or user-panel
if [ -d "$COMP_DIR/features" ]; then
    mkdir -p "$COMP_DIR/user-panel/features"
    mv "$COMP_DIR/features"/* "$COMP_DIR/user-panel/features/" 2>/dev/null || true
    rmdir "$COMP_DIR/features" 2>/dev/null || true
    echo "   Merged features/ -> user-panel/features/"
fi

# Keep these as-is (already correct feature names):
# - admin/ (but might need internal restructuring)
# - ai/
# - analytics/
# - assessment/
# - compliance/
# - content/
# - dashboard/
# - feature-flags/
# - gamification/
# - learning/
# - moderation/
# - security/
# - social/
# - system/
# - system-features/
# - user-panel/
# - users/

echo ""
echo "=== Restructuring Complete ==="
echo "Backup available at: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Update imports in affected files"
echo "2. Run: npm run build to check for errors"
echo "3. Fix any remaining import issues"
