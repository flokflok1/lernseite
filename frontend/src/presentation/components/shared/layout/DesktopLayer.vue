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
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { WindowType } from '@/application/stores/modules/ui/window.store'
import WindowComponent from './WindowComponent.vue'
import Taskbar from './Taskbar.vue'
import { LEARNING_METHOD_REGISTRY as _LEARNING_METHOD_REGISTRY, getLearningMethodForm } from '@/presentation/components/panel/admin/learning-methods/editor/learning-methods.registry'

// Import window content components lazily - Migrated to feature-domain structure (Wave 3-5, 2026-01-11)
// AI Operations
const AdminAiStudioWindow = defineAsyncComponent(() => import('@/presentation/components/panel/editor/ai/studio/views/AiStudioProWindow.vue'))
const AdminAIKapitelGeneratorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/editor/ai/authoring/views/KapitelGeneratorWindow.vue'))
const AdminAIJobWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/ai/management/jobs/views/AIJobWindow.vue'))
const AdminModelSelectorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/ai/management/models/views/ModelSelectorWindow.vue'))
const AdminPromptBrowserWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/ai/management/prompts/PromptBrowser.vue'))

// Content Management - Courses
const AdminCourseCreateWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/views/CourseCreateWindow.vue'))
const AdminCourseEditorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/views/CourseEditorWindow.vue'))
const AdminCourseFilesWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/views/CourseFilesWindow.vue'))

// Content Management - Chapters
// MIGRATED: KapitelEditorWindow deleted (Windows forbidden) - use KapitelEditorPanel (Panel-based)
const AdminKapitelManagerWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/chapters/views/KapitelManagerWindow.vue'))
const AdminChapterPreviewWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/chapters/views/ChapterPreviewWindow.vue'))

// Content Management - Lessons
const AdminLessonEditorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/lessons/views/LessonEditorWindow.vue'))
const AdminLessonPreviewWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/lessons/views/LessonPreviewWindow.vue'))

// Assessment
const AdminExamManagerWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/assessment/views/ExamManagerWindow.vue'))

// System Operations
const AdminFilePreviewWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/system/views/FilePreviewWindow.vue'))
const AdminWindowManagerWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/system/views/WindowManagerWindow.vue'))

// Editor Windows (Course Authoring - /editor route)
const EditorManualWindow = defineAsyncComponent(() => import('@/presentation/pages/panel/editor/manual/ManualEditorWindow.vue'))
const EditorAIStudioWindow = defineAsyncComponent(() => import('@/presentation/components/panel/editor/ai/AIEditorWindow.vue'))

const windowStore = useWindowStore()

const visibleWindows = computed(() => windowStore.visibleWindows)
const activeWindowId = computed(() => windowStore.activeWindowId)

/**
 * Resolve window component based on type
 */
function resolveWindowComponent(type: WindowType) {
  // Handle learning method forms (12 Content-LMs: 0-11) via registry
  if (type.startsWith('learning-method-') && type.endsWith('-form')) {
    const codeStr = type.replace('learning-method-', '').replace('-form', '')
    const code = parseInt(codeStr, 10)

    if (!isNaN(code) && code >= 0 && code <= 11) {
      const form = getLearningMethodForm(code)

      if (form !== null) {
        return form
      }

      // For unimplemented learning methods (e.g., LM07, LM09)
      return {
        template: '<div class="p-4 text-center text-gray-500">{{ $t("system.notImplemented") }} - LM{{ lmCode }}</div>',
        props: ['window'],
        setup() {
          return { lmCode: code }
        }
      }
    }
  }

  switch (type) {
    case 'admin-course-create':
      return AdminCourseCreateWindow
    case 'admin-course-editor':
      return AdminCourseEditorWindow
    case 'admin-kapitel-editor':  // MIGRATED: Use course-editor instead (all chapter editing handled there)
      // Window-based editor migrated to course-editor system with manual/AI modes
      return {
        template: '<div class="p-4">{{ $t("system.migrated.kapitelEditor") }}</div>',
        props: ['window']
      }
    case 'admin-kapitel-manager':  // NEW: Kapitel Manager (2025-12-03)
      return AdminKapitelManagerWindow
    case 'admin-ai-kapitel-generator':  // NEW: AI Kapitel Generator (2025-11-27)
      return AdminAIKapitelGeneratorWindow
    case 'admin-ai-studio':  // Phase D4: KI-Authoring-Studio (2025-12-02)
      return AdminAiStudioWindow
    case 'admin-lesson-editor':
      return AdminLessonEditorWindow
    case 'admin-learning-method-editor':
      // MIGRATED: Learning methods now use Panel-based system
      return {
        template: '<div class="p-4">Learning Method Editor migrated to Panel system</div>',
        props: ['window']
      }
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
    // Editor Windows (Course Authoring)
    case 'editor-manual':
      return EditorManualWindow
    case 'editor-ai-studio':
      return EditorAIStudioWindow
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
