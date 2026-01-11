<!--
  LSX Desktop Layer

  Main desktop rendering layer that manages all floating windows.
  Renders window components based on window type and manages taskbar.

  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="lsx-desktop-layer">
    <!-- Main Content (router-view slot) -->
    <div class="lsx-desktop-content">
      <slot />
    </div>

    <!-- Floating Windows -->
    <WindowComponent
      v-for="window in visibleWindows"
      :key="window.id"
      :window="window"
      :isActive="window.id === activeWindowId"
      @close="handleClose"
      @minimize="handleMinimize"
      @maximize="handleMaximize"
      @focus="handleFocus"
      @drag="handleDrag"
      @resize="handleResize"
    >
      <!-- Dynamic Window Content based on type -->
      <component
        :is="resolveWindowComponent(window.type)"
        :window="window"
        @close="handleClose(window.id)"
      />
    </WindowComponent>

    <!-- Taskbar (fixed position) -->
    <Taskbar />
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useWindowStore } from '@/store/window.store'
import type { WindowType } from '@/store/window.store'
import WindowComponent from './WindowComponent.vue'
import Taskbar from './Taskbar.vue'

// Import window content components lazily - Migrated to feature-domain structure (Wave 3-5, 2026-01-11)
// AI Operations
const AdminAiStudioWindow = defineAsyncComponent(() => import('@/components/ai/admin/studio/views/AiStudioProWindow.vue'))
const AdminAIKapitelGeneratorWindow = defineAsyncComponent(() => import('@/components/ai/admin/authoring/views/KapitelGeneratorWindow.vue'))
const AdminAIJobWindow = defineAsyncComponent(() => import('@/components/ai/admin/management/jobs/views/AIJobWindow.vue'))
const AdminModelSelectorWindow = defineAsyncComponent(() => import('@/components/ai/admin/management/models/views/ModelSelectorWindow.vue'))
const AdminPromptBrowserWindow = defineAsyncComponent(() => import('@/components/ai/admin/management/prompts/views/PromptBrowserWindow.vue'))

// Content Management - Courses
const AdminCourseCreateWindow = defineAsyncComponent(() => import('@/components/content/admin/courses/views/CourseCreateWindow.vue'))
const AdminCourseEditorWindow = defineAsyncComponent(() => import('@/components/content/admin/courses/views/CourseEditorWindow.vue'))
const AdminCourseFilesWindow = defineAsyncComponent(() => import('@/components/content/admin/courses/views/CourseFilesWindow.vue'))

// Content Management - Chapters
const AdminKapitelEditorWindow = defineAsyncComponent(() => import('@/components/content/admin/chapters/views/KapitelEditorWindow.vue'))
const AdminKapitelManagerWindow = defineAsyncComponent(() => import('@/components/content/admin/chapters/views/KapitelManagerWindow.vue'))
const AdminChapterPreviewWindow = defineAsyncComponent(() => import('@/components/content/admin/chapters/views/ChapterPreviewWindow.vue'))

// Content Management - Lessons
const AdminLessonEditorWindow = defineAsyncComponent(() => import('@/components/content/admin/lessons/views/LessonEditorWindow.vue'))
const AdminLessonPreviewWindow = defineAsyncComponent(() => import('@/components/content/admin/lessons/views/LessonPreviewWindow.vue'))

// Content Management - Learning Methods
const AdminLearningMethodEditorWindow = defineAsyncComponent(() => import('@/components/content/admin/learning-methods/views/LearningMethodEditorWindow.vue'))

// Assessment
const AdminExamManagerWindow = defineAsyncComponent(() => import('@/components/assessment/admin/views/ExamManagerWindow.vue'))

// System Operations
const AdminFilePreviewWindow = defineAsyncComponent(() => import('@/components/system/admin/views/FilePreviewWindow.vue'))
const AdminWindowManagerWindow = defineAsyncComponent(() => import('@/components/system/admin/views/WindowManagerWindow.vue'))

// Learning Method Forms (12 Content-LMs: 00-11) - Updated 2026-01-11
// LM12-32 deleted (were System-Features, not Content-LMs)
const LearningMethodFormComponents: Record<number, ReturnType<typeof defineAsyncComponent>> = {
  0: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod00Form.vue')),
  1: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod01Form.vue')),
  2: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod02Form.vue')),
  3: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod03Form.vue')),
  4: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod04Form.vue')),
  5: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod05Form.vue')),
  6: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod06Form.vue')),
  7: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod07Form.vue')),
  8: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod08Form.vue')),
  9: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod09Form.vue')),
  10: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod10Form.vue')),
  11: defineAsyncComponent(() => import('@/components/content/admin/learning-methods/forms/LearningMethod11Form.vue'))
}

const windowStore = useWindowStore()

const visibleWindows = computed(() => windowStore.visibleWindows)
const activeWindowId = computed(() => windowStore.activeWindowId)

/**
 * Resolve window component based on type
 */
function resolveWindowComponent(type: WindowType) {
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
      return AdminCourseCreateWindow
    case 'admin-course-editor':
      return AdminCourseEditorWindow
    case 'admin-kapitel-editor':  // Refactored: modules → chapters (2025-11-27)
      return AdminKapitelEditorWindow
    case 'admin-kapitel-manager':  // NEW: Kapitel Manager (2025-12-03)
      return AdminKapitelManagerWindow
    case 'admin-ai-kapitel-generator':  // NEW: AI Kapitel Generator (2025-11-27)
      return AdminAIKapitelGeneratorWindow
    case 'admin-ai-studio':  // Phase D4: KI-Authoring-Studio (2025-12-02)
      return AdminAiStudioWindow
    case 'admin-lesson-editor':
      return AdminLessonEditorWindow
    case 'admin-learning-method-editor':
      return AdminLearningMethodEditorWindow
    case 'admin-exam-manager':
      return AdminExamManagerWindow
    case 'admin-ai-job':
      return AdminAIJobWindow
    case 'admin-window-manager':
      return AdminWindowManagerWindow
    case 'admin-prompt-browser':
      return AdminPromptBrowserWindow
    case 'admin-model-selector':
      return AdminModelSelectorWindow
    case 'admin-course-files':
      return AdminCourseFilesWindow
    case 'admin-file-preview':
      return AdminFilePreviewWindow
    case 'admin-lesson-preview':
      return AdminLessonPreviewWindow
    case 'admin-chapter-preview':
      return AdminChapterPreviewWindow
    default:
      // Fallback: simple placeholder
      return {
        template: '<div class="p-4">Unknown window type: {{ type }}</div>',
        props: ['window']
      }
  }
}

/**
 * Handle window close
 */
function handleClose(windowId: string): void {
  windowStore.closeWindow(windowId)
}

/**
 * Handle window minimize
 */
function handleMinimize(windowId: string): void {
  windowStore.minimizeWindow(windowId)
}

/**
 * Handle window maximize/restore
 */
function handleMaximize(windowId: string): void {
  windowStore.toggleMaximize(windowId)
}

/**
 * Handle window focus
 */
function handleFocus(windowId: string): void {
  windowStore.focusWindow(windowId)
}

/**
 * Handle window drag
 */
function handleDrag(windowId: string, position: { x: number; y: number }): void {
  windowStore.updateWindowPosition(windowId, position)
}

/**
 * Handle window resize
 */
function handleResize(windowId: string, size: { width: number; height: number }): void {
  windowStore.updateWindowSize(windowId, size)
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
