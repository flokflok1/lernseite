<!--
  LSX Desktop Layer

  Main desktop rendering layer that manages all floating features.
  Renders panel components based on panel type and manages taskbar.

  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="lsx-desktop-layer">
    <!-- Main Content (router-view slot) -->
    <div class="lsx-desktop-content">
      <slot />
    </div>

    <!-- Floating Panels -->
    <PanelComponent
      v-for="panel in visiblePanels"
      :key="panel.id"
      :panel="panel"
      :isActive="panel.id === activePanelId"
      @close="handleClose"
      @minimize="handleMinimize"
      @maximize="handleMaximize"
      @focus="handleFocus"
      @drag="handleDrag"
      @resize="handleResize"
    >
      <!-- Dynamic Panel Content based on type -->
      <component
        :is="resolvePanelComponent(panel.type)"
        :panel="panel"
        @close="handleClose(panel.id)"
      />
    </PanelComponent>

    <!-- Taskbar (fixed position) -->
    <Taskbar />
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { usePanelStore } from '@/application/stores/modules/desktop'
import type { PanelType } from '@/application/stores/modules/desktop'
import PanelComponent from './PanelComponent.vue'
import Taskbar from './Taskbar.vue'

// Import panel content components lazily - Migrated to feature-domain structure (Wave 3-5, 2026-01-11)
// AI Operations
const AdminAiEditorPanel = defineAsyncComponent(() => import('@/presentation/components/studio/ai/panel/studio/views/AiEditorPanel.vue'))
const AdminAIKapitelGeneratorPanel = defineAsyncComponent(() => import('@/presentation/components/studio/ai/panel/authoring/views/KapitelGeneratorPanel.vue'))
const AdminAIJobPanel = defineAsyncComponent(() => import('@/presentation/components/studio/ai/panel/management/jobs/views/AIJobPanel.vue'))
const AdminModelSelectorPanel = defineAsyncComponent(() => import('@/presentation/components/studio/ai/panel/management/models/views/ModelSelectorPanel.vue'))
const AdminPromptBrowserPanel = defineAsyncComponent(() => import('@/presentation/components/studio/ai/panel/management/prompts/views/PromptBrowserPanel.vue'))

// Content Management - Courses
const AdminCourseCreatePanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/courses/views/CourseCreatePanel.vue'))
const AdminCourseEditorPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/courses/views/CourseEditorPanel.vue'))
const AdminCourseListEditorPanel = defineAsyncComponent(() => import('@/presentation/components/panel/panels/courses/CourseListEditorPanel.vue'))
const AdminCourseFilesPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/courses/views/CourseFilesPanel.vue'))

// Content Management - Chapters
const AdminKapitelEditorPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/chapters/views/KapitelEditorPanel.vue'))
const AdminKapitelManagerPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/chapters/views/KapitelManagerPanel.vue'))
const AdminChapterPreviewPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/chapters/views/ChapterPreviewPanel.vue'))

// Content Management - Lessons
const AdminLessonEditorPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/lessons/views/LessonEditorPanel.vue'))
const AdminLessonPreviewPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/lessons/views/LessonPreviewPanel.vue'))

// Content Management - Learning Methods
const AdminLearningMethodEditorPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/content/panel/learning-methods/views/LearningMethodEditorPanel.vue'))

// Assessment
const AdminExamManagerPanel = defineAsyncComponent(() => import('@/presentation/components/studio/assessment/panel/views/ExamManagerPanel.vue'))

// System Operations
const AdminFilePreviewPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/system/panel/views/FilePreviewPanel.vue'))
const AdminPanelManagerPanel = defineAsyncComponent(() => import('@/presentation/components/shared/ui/system/panel/views/PanelManagerPanel.vue'))
const AdminUserGroupManagementPanel = defineAsyncComponent(() => import('@/presentation/components/panel/panels/groups/AdminUserGroupManagementPanel.vue'))

// Learning Method Forms (12 Content-LMs: 00-11) - Updated 2026-01-11
// LM12-32 deleted (were System-Features, not Content-LMs)
const LearningMethodFormComponents: Record<number, ReturnType<typeof defineAsyncComponent>> = {
  0: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod00Form.vue')),
  1: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod01Form.vue')),
  2: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod02Form.vue')),
  3: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod03Form.vue')),
  4: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod04Form.vue')),
  5: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod05Form.vue')),
  6: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod06Form.vue')),
  7: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod07Form.vue')),
  8: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod08Form.vue')),
  9: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod09Form.vue')),
  10: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod10Form.vue')),
  11: defineAsyncComponent(() => import('@/presentation/components/learning/editor/forms/LearningMethod11Form.vue'))
}

const panelStore = usePanelStore()

const visiblePanels = computed(() => panelStore.visiblePanels)
const activePanelId = computed(() => panelStore.activePanelId)

/**
 * Resolve panel component based on type
 */
function resolvePanelComponent(type: PanelType) {
  // Handle learning method forms (12 Content-LMs: 0-11) via explicit mapping
  if (type.startsWith('learning-method-') && type.endsWith('-form')) {
    const codeStr = type.replace('learning-method-', '').replace('-form', '')
    const code = parseInt(codeStr, 10)
    if (!isNaN(code) && code >= 0 && code <= 11 && LearningMethodFormComponents[code]) {
      return LearningMethodFormComponents[code]
    }
  }

  switch (type) {
    case 'admin-course-create':
      return AdminCourseCreatePanel
    case 'admin-course-list-editor':
      return AdminCourseListEditorPanel
    case 'admin-course-editor':
      return AdminCourseEditorPanel
    case 'admin-kapitel-editor':  // Refactored: modules → chapters (2025-11-27)
      return AdminKapitelEditorPanel
    case 'admin-kapitel-manager':  // NEW: Kapitel Manager (2025-12-03)
      return AdminKapitelManagerPanel
    case 'admin-ai-kapitel-generator':  // NEW: AI Kapitel Generator (2025-11-27)
      return AdminAIKapitelGeneratorPanel
    case 'admin-ai-editor':  // Phase D4: KI-Authoring-Studio (2025-12-02)
      return AdminAiEditorPanel
    case 'admin-lesson-editor':
      return AdminLessonEditorPanel
    case 'admin-learning-method-editor':
      return AdminLearningMethodEditorPanel
    case 'admin-exam-manager':
      return AdminExamManagerPanel
    case 'admin-ai-job':
      return AdminAIJobPanel
    case 'admin-panel-manager':
      return AdminPanelManagerPanel
    case 'admin-prompt-browser':
      return AdminPromptBrowserPanel
    case 'admin-model-selector':
      return AdminModelSelectorPanel
    case 'admin-course-files':
      return AdminCourseFilesPanel
    case 'admin-file-preview':
      return AdminFilePreviewPanel
    case 'admin-lesson-preview':
      return AdminLessonPreviewPanel
    case 'admin-chapter-preview':
      return AdminChapterPreviewPanel
    case 'admin-user-group-management':
      return AdminUserGroupManagementPanel
    default:
      // Fallback: simple placeholder
      return {
        template: '<div class="p-4">Unknown panel type: {{ type }}</div>',
        props: ['panel']
      }
  }
}

/**
 * Handle panel close
 */
function handleClose(panelId: string): void {
  panelStore.closePanel(panelId)
}

/**
 * Handle panel minimize
 */
function handleMinimize(panelId: string): void {
  panelStore.minimizePanel(panelId)
}

/**
 * Handle panel maximize/restore
 */
function handleMaximize(panelId: string): void {
  panelStore.toggleMaximize(panelId)
}

/**
 * Handle panel focus
 */
function handleFocus(panelId: string): void {
  panelStore.focusPanel(panelId)
}

/**
 * Handle panel drag
 */
function handleDrag(panelId: string, position: { x: number; y: number }): void {
  panelStore.updatePanelPosition(panelId, position)
}

/**
 * Handle panel resize
 */
function handleResize(panelId: string, size: { width: number; height: number }): void {
  panelStore.updatePanelSize(panelId, size)
}
</script>

<style scoped>
.lsx-desktop-layer {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.lsx-desktop-content {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding-bottom: 56px; /* Space for fixed taskbar (48px + 8px gap) */
  box-sizing: border-box;
}
</style>
