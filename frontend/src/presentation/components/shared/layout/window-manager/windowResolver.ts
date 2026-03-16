/**
 * Window Component Resolver
 *
 * Maps PanelType strings to lazy-loaded Vue components.
 * Shared between WindowManager.vue (in-panel rendering)
 * and PopoutPage.vue (pop-out rendering).
 */

import { defineAsyncComponent } from 'vue'

// LM registry loaded dynamically to avoid shared/ → panel/admin/ circular dependency
let _lmRegistryPromise: Promise<typeof import('@/presentation/components/panel/admin/learning-methods/editor/learning-methods.registry')> | null = null
function getLmRegistry() {
  if (!_lmRegistryPromise) {
    _lmRegistryPromise = import('@/presentation/components/panel/admin/learning-methods/editor/learning-methods.registry')
  }
  return _lmRegistryPromise
}

// AI Operations
const AdminAiEditorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/editor/ai/unified/UnifiedAIEditorWindow.vue'))
const AdminAIKapitelGeneratorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/editor/ai/authoring/views/KapitelGeneratorWindow.vue'))
const AdminAIJobWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/ai/management/jobs/views/AIJobWindow.vue'))
const AdminModelSelectorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/ai/management/models/views/ModelSelectorWindow.vue'))
const AdminPromptBrowserWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/ai/management/prompts/PromptBrowser.vue'))

// Content Management - Courses
const AdminCourseCreateWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/views/CourseCreateWindow.vue'))
const AdminCourseEditorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/views/CourseEditorWindow.vue'))
const AdminCourseFilesWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/views/CourseFilesWindow.vue'))

// Content Management - Chapters
const AdminKapitelManagerWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/chapters/views/KapitelManagerWindow.vue'))
const AdminChapterPreviewWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/chapters/views/ChapterPreviewWindow.vue'))

// Content Management - Lessons
const AdminLessonEditorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/lessons/views/LessonEditorWindow.vue'))
const AdminLessonPreviewWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/courses/lessons/views/LessonPreviewWindow.vue'))

// Assessment
const AdminExamManagerWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/assessment/exams/ExamManager.vue'))
const AdminPdfViewerWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/assessment/archive/PdfViewerWindow.vue'))

// System Operations
const AdminFilePreviewWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/system/views/FilePreviewWindow.vue'))
const AdminWindowManagerWindow = defineAsyncComponent(() => import('@/presentation/components/panel/admin/system/views/WindowManagerWindow.vue'))

// Editor Windows (Course Authoring - /editor route)
const EditorManualWindow = defineAsyncComponent(() => import('@/presentation/pages/panel/editor/manual/ManualEditorWindow.vue'))
const EditorAIEditorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/editor/ai/unified/UnifiedAIEditorWindow.vue'))
const ActivityEditorWindow = defineAsyncComponent(() => import('@/presentation/components/panel/editor/manual/activity-editors/ActivityEditorWindow.vue'))

// Exam Trainer Windows
const ExamAnlageWindow = defineAsyncComponent(() => import('@/presentation/components/panel/user/exam-trainer/anlagen/AnlagePanel.vue'))
const ExamScratchPadWindow = defineAsyncComponent(() => import('@/presentation/components/panel/user/exam-trainer/ScratchPad.vue'))

/**
 * Resolve window component based on type string.
 */
export function resolveWindowComponent(type: string) {
  // Handle learning method forms (12 Content-LMs: 0-11) via async registry
  if (type.startsWith('learning-method-') && type.endsWith('-form')) {
    const codeStr = type.replace('learning-method-', '').replace('-form', '')
    const code = parseInt(codeStr, 10)

    if (!isNaN(code) && code >= 0 && code <= 11) {
      return defineAsyncComponent(async () => {
        const { getLearningMethodForm } = await getLmRegistry()
        const form = getLearningMethodForm(code)
        if (form !== null) return form as any
        return {
          template: '<div class="p-4 text-center text-gray-500">{{ $t("common.not_implemented_lm", { code: lmCode }) }}</div>',
          props: ['window'],
          setup() { return { lmCode: code } }
        }
      })
    }
  }

  switch (type) {
    case 'admin-course-create':
      return AdminCourseCreateWindow
    case 'admin-course-editor':
      return AdminCourseEditorWindow
    case 'admin-kapitel-editor':
      return {
        template: '<div class="p-4">{{ $t("common.migrated_to_panel") }}</div>',
        props: ['window']
      }
    case 'admin-kapitel-manager':
      return AdminKapitelManagerWindow
    case 'admin-ai-kapitel-generator':
      return AdminAIKapitelGeneratorWindow
    case 'admin-ai-editor':
      return AdminAiEditorWindow
    case 'admin-lesson-editor':
      return AdminLessonEditorWindow
    case 'admin-learning-method-editor':
      return {
        template: '<div class="p-4">{{ $t("common.migrated_to_panel") }}</div>',
        props: ['window']
      }
    case 'admin-exam-manager':
      return AdminExamManagerWindow
    case 'admin-pdf-viewer':
      return AdminPdfViewerWindow
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
    case 'editor-manual':
      return EditorManualWindow
    case 'editor-ai-editor':
      return EditorAIEditorWindow
    case 'activity-editor':
      return ActivityEditorWindow
    case 'exam-trainer-anlage':
      return ExamAnlageWindow
    case 'exam-trainer-scratchpad':
      return ExamScratchPadWindow
    default:
      return {
        template: '<div class="p-4">{{ $t("common.unknown_window_type") }}</div>',
        props: ['window']
      }
  }
}
