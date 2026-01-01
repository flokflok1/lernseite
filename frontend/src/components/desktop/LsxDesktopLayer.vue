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
    <LsxDesktopWindow
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
    </LsxDesktopWindow>

    <!-- Taskbar (fixed position) -->
    <LsxTaskbar />
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useWindowStore } from '@/store/window.store'
import type { WindowType } from '@/store/window.store'
import LsxDesktopWindow from './LsxDesktopWindow.vue'
import LsxTaskbar from './LsxTaskbar.vue'

// Import window content components lazily
const AdminCourseCreateWindow = defineAsyncComponent(() => import('./windows/AdminCourseCreateWindow.vue'))
const AdminCourseEditorWindow = defineAsyncComponent(() => import('./windows/AdminCourseEditorWindow.vue'))
const AdminKapitelEditorWindow = defineAsyncComponent(() => import('./windows/AdminKapitelEditorWindow.vue'))  // Refactored: modules → chapters (2025-11-27)
const AdminKapitelManagerWindow = defineAsyncComponent(() => import('./windows/AdminKapitelManagerWindow.vue'))  // NEW: Kapitel Manager (2025-12-03)
const AdminAIKapitelGeneratorWindow = defineAsyncComponent(() => import('./windows/AdminAIKapitelGeneratorWindow.vue'))  // NEW: AI Kapitel Generator (2025-11-27)
const AdminAiStudioWindow = defineAsyncComponent(() => import('./windows/AdminAiStudioProWindow.vue'))  // Phase D4: KI-Authoring-Studio PRO (2025-12-11)
const AdminLessonEditorWindow = defineAsyncComponent(() => import('./windows/AdminLessonEditorWindow.vue'))
const AdminLearningMethodEditorWindow = defineAsyncComponent(() => import('./windows/AdminLearningMethodEditorWindow.vue'))  // Phase D3.4
const AdminExamManagerWindow = defineAsyncComponent(() => import('./windows/AdminExamManagerWindow.vue'))
const AdminAIJobWindow = defineAsyncComponent(() => import('./windows/AdminAIJobWindow.vue'))
const AdminWindowManagerWindow = defineAsyncComponent(() => import('./windows/AdminWindowManagerWindow.vue'))
const AdminPromptBrowserWindow = defineAsyncComponent(() => import('./windows/AdminPromptBrowserWindow.vue'))
const AdminModelSelectorWindow = defineAsyncComponent(() => import('./windows/AdminModelSelectorWindow.vue'))
const AdminCourseFilesWindow = defineAsyncComponent(() => import('./windows/AdminCourseFilesWindow.vue'))
const AdminFilePreviewWindow = defineAsyncComponent(() => import('./windows/AdminFilePreviewWindow.vue'))  // Phase D4: File Preview
const AdminLessonPreviewWindow = defineAsyncComponent(() => import('./windows/AdminLessonPreviewWindow.vue'))  // Phase D4: Lesson Preview
const AdminChapterPreviewWindow = defineAsyncComponent(() => import('./windows/AdminChapterPreviewWindow.vue'))  // Phase D4: Chapter Preview

// Learning Method Forms (33 Methoden: 00-32) - Explizite Imports für Vite
const LearningMethodFormComponents: Record<number, ReturnType<typeof defineAsyncComponent>> = {
  0: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod00Form.vue')),
  1: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod01Form.vue')),
  2: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod02Form.vue')),
  3: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod03Form.vue')),
  4: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod04Form.vue')),
  5: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod05Form.vue')),
  6: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod06Form.vue')),
  7: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod07Form.vue')),
  8: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod08Form.vue')),
  9: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod09Form.vue')),
  10: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod10Form.vue')),
  11: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod11Form.vue')),
  12: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod12Form.vue')),
  13: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod13Form.vue')),
  14: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod14Form.vue')),
  15: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod15Form.vue')),
  16: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod16Form.vue')),
  17: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod17Form.vue')),
  18: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod18Form.vue')),
  19: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod19Form.vue')),
  20: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod20Form.vue')),
  21: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod21Form.vue')),
  22: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod22Form.vue')),
  23: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod23Form.vue')),
  24: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod24Form.vue')),
  25: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod25Form.vue')),
  26: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod26Form.vue')),
  27: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod27Form.vue')),
  28: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod28Form.vue')),
  29: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod29Form.vue')),
  30: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod30Form.vue')),
  31: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod31Form.vue')),
  32: defineAsyncComponent(() => import('./windows/learning-methods/LearningMethod32Form.vue'))
}

const windowStore = useWindowStore()

const visibleWindows = computed(() => windowStore.visibleWindows)
const activeWindowId = computed(() => windowStore.activeWindowId)

/**
 * Resolve window component based on type
 */
function resolveWindowComponent(type: WindowType) {
  // Handle learning method forms (33 forms: 0-32) via explicit mapping
  if (type.startsWith('learning-method-') && type.endsWith('-form')) {
    const codeStr = type.replace('learning-method-', '').replace('-form', '')
    const code = parseInt(codeStr, 10)
    if (!isNaN(code) && code >= 0 && code <= 32 && LearningMethodFormComponents[code]) {
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
