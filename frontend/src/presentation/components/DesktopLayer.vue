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
import { computed, defineAsyncComponent, ref } from 'vue'
import { useWindowStore } from '@/application/stores/modules/desktop'
import type { WindowType } from '@/application/stores/modules/desktop'
import { SchemaFormComponent } from '@/presentation/components/base'
import { adminGetLearningMethodUISchema } from '@/infrastructure/api/admin/learning-methods.api'
import type { UISchema } from '@/infrastructure/utils/i18nResolver'
import WindowComponent from './WindowComponent.vue'
import Taskbar from './Taskbar.vue'

// Import window content components lazily - Migrated to feature-domain structure (Wave 3-5, 2026-01-11)
// AI Operations
const AdminAiStudioWindow = defineAsyncComponent(() => import('@/presentation/components/studio/ai/admin/studio/views/AiStudioProWindow.vue'))
const AdminAIKapitelGeneratorWindow = defineAsyncComponent(() => import('@/presentation/components/studio/ai/admin/authoring/views/KapitelGeneratorWindow.vue'))
const AdminAIJobWindow = defineAsyncComponent(() => import('@/presentation/components/studio/ai/admin/management/jobs/views/AIJobWindow.vue'))
const AdminModelSelectorWindow = defineAsyncComponent(() => import('@/presentation/components/studio/ai/admin/management/models/views/ModelSelectorWindow.vue'))
const AdminPromptBrowserWindow = defineAsyncComponent(() => import('@/presentation/components/studio/ai/admin/management/prompts/views/PromptBrowserWindow.vue'))

// Content Management - Courses
const AdminCourseCreateWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/courses/views/CourseCreateWindow.vue'))
const AdminCourseEditorWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/courses/views/CourseEditorWindow.vue'))
const AdminCourseFilesWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/courses/views/CourseFilesWindow.vue'))

// Content Management - Chapters
const AdminKapitelEditorWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/chapters/views/KapitelEditorWindow.vue'))
const AdminKapitelManagerWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/chapters/views/KapitelManagerWindow.vue'))
const AdminChapterPreviewWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/chapters/views/ChapterPreviewWindow.vue'))

// Content Management - Lessons
const AdminLessonEditorWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/lessons/views/LessonEditorWindow.vue'))
const AdminLessonPreviewWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/lessons/views/LessonPreviewWindow.vue'))

// Content Management - Learning Methods
const AdminLearningMethodEditorWindow = defineAsyncComponent(() => import('@/presentation/components/base/content/admin/learning-methods/views/LearningMethodEditorWindow.vue'))

// Assessment
const AdminExamManagerWindow = defineAsyncComponent(() => import('@/presentation/components/studio/assessment/admin/views/ExamManagerWindow.vue'))

// System Operations
const AdminFilePreviewWindow = defineAsyncComponent(() => import('@/presentation/components/base/system/admin/views/FilePreviewWindow.vue'))
const AdminWindowManagerWindow = defineAsyncComponent(() => import('@/presentation/components/base/system/admin/views/WindowManagerWindow.vue'))

/**
 * Schema cache for learning method forms
 * Maps learning method code (0-11) to fetched UISchema
 */
const schemaCache = ref<Record<number, UISchema>>({})

/**
 * Track which schemas are currently being fetched
 * Prevents duplicate API calls
 */
const loadingSchemas = ref<Set<number>>(new Set())

/**
 * Store errors from schema fetch operations
 * Maps learning method code to error message
 */
const schemaErrors = ref<Record<number, string>>({})

const windowStore = useWindowStore()

const visibleWindows = computed(() => windowStore.visibleWindows)
const activeWindowId = computed(() => windowStore.activeWindowId)

/**
 * Fetch and cache learning method UISchema
 *
 * Implements intelligent caching:
 * - Returns cached schema if available
 * - Prevents duplicate API calls via loadingSchemas tracking
 * - Stores errors for later retrieval
 *
 * @param code - Learning method code (0-11)
 * @returns Promise<UISchema | null> - Schema or null if error
 */
async function fetchLearningMethodSchema(code: number): Promise<UISchema | null> {
  // Return cached schema if available
  if (schemaCache.value[code]) {
    return schemaCache.value[code]
  }

  // Prevent duplicate API calls if already loading
  if (loadingSchemas.value.has(code)) {
    // Wait for existing fetch to complete
    let attempts = 0
    while (loadingSchemas.value.has(code) && attempts < 100) {
      await new Promise(resolve => setTimeout(resolve, 50))
      attempts++
      // Check if now cached
      if (schemaCache.value[code]) {
        return schemaCache.value[code]
      }
    }
    // If error was stored, return null
    if (schemaErrors.value[code]) {
      return null
    }
    return schemaCache.value[code] || null
  }

  // Mark as loading
  loadingSchemas.value.add(code)

  try {
    // Fetch schema from API
    const schema = await adminGetLearningMethodUISchema(code)

    // Cache the schema
    schemaCache.value[code] = schema

    // Clear any previous error
    delete schemaErrors.value[code]

    return schema
  } catch (error) {
    // Store error message
    const errorMsg = error instanceof Error ? error.message : 'Unknown error fetching schema'
    schemaErrors.value[code] = errorMsg

    console.error(`Failed to fetch schema for learning method ${code}:`, error)

    return null
  } finally {
    // Mark as no longer loading
    loadingSchemas.value.delete(code)
  }
}

/**
 * Resolve window component based on type
 */
function resolveWindowComponent(type: WindowType) {
  // Handle learning method forms (12 Content-LMs: 0-11) with dynamic schema fetching
  if (type.startsWith('learning-method-') && type.endsWith('-form')) {
    const codeStr = type.replace('learning-method-', '').replace('-form', '')
    const code = parseInt(codeStr, 10)

    // Validate learning method code is numeric (no strict range check anymore)
    if (!isNaN(code) && code >= 0) {
      // Return wrapper component that handles schema fetching and rendering
      return defineAsyncComponent({
        loader: async () => {
          const schema = await fetchLearningMethodSchema(code)

          if (!schema) {
            // Return error component if schema fetch failed
            return {
              template: `
                <div class="p-4 bg-red-50 border border-red-200 rounded">
                  <p class="text-red-900 font-semibold">{{ $t('errors.formLoadFailed') }}</p>
                  <p class="text-red-700 text-sm mt-2">{{ error }}</p>
                </div>
              `,
              data() {
                return {
                  error: schemaErrors.value[code] || 'Unknown error'
                }
              }
            }
          }

          // Return SchemaFormComponent configured for this schema
          return {
            components: { SchemaFormComponent },
            template: `
              <SchemaFormComponent
                :schema="schema"
                :modelValue="formData"
                :showCancelButton="true"
                submitLabel="common.save"
                @update:modelValue="updateFormData"
                @submit="handleSubmit"
                @cancel="handleCancel"
              />
            `,
            props: ['window'],
            emits: ['close'],
            data() {
              return {
                schema: schema,
                formData: {}
              }
            },
            methods: {
              updateFormData(data: Record<string, any>) {
                this.formData = data
              },
              handleSubmit(data: Record<string, any>) {
                console.log('Learning method form submitted:', {
                  code,
                  data
                })
                // TODO: Task #10 - Submit to backend API
                this.$emit('close')
              },
              handleCancel() {
                this.$emit('close')
              }
            }
          }
        },

        loadingComponent: {
          template: `
            <div class="flex items-center justify-center p-12 min-h-[300px]">
              <div class="flex flex-col items-center gap-3">
                <div class="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full"></div>
                <p class="text-gray-600 text-sm">{{ $t('common.loading') }}</p>
              </div>
            </div>
          `
        },

        delay: 200,          // Show loading indicator after 200ms of waiting
        timeout: 10000       // Timeout if schema takes >10 seconds to load
      })
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
