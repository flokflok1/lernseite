/**
 * Editor types for the manual course editor.
 *
 * Defines editor modes (beginner/advanced/expert) and their
 * feature visibility configurations.
 */

export type EditorMode = 'beginner' | 'advanced' | 'expert'

export interface EditorModeConfig {
  showMediaUpload: boolean
  showLessonSettings: boolean
  showPreview: boolean
  showAdvancedFormatting: boolean
  showCourseVisibility: boolean
  showPublish: boolean
}

export const EDITOR_MODE_CONFIGS: Record<EditorMode, EditorModeConfig> = {
  beginner: {
    showMediaUpload: false,
    showLessonSettings: false,
    showPreview: false,
    showAdvancedFormatting: false,
    showCourseVisibility: false,
    showPublish: false,
  },
  advanced: {
    showMediaUpload: true,
    showLessonSettings: true,
    showPreview: true,
    showAdvancedFormatting: true,
    showCourseVisibility: false,
    showPublish: false,
  },
  expert: {
    showMediaUpload: true,
    showLessonSettings: true,
    showPreview: true,
    showAdvancedFormatting: true,
    showCourseVisibility: true,
    showPublish: true,
  },
}

export type EditorTab =
  | 'content'
  | 'course-info'
  | 'media'
  | 'preview'
  | 'lesson-settings'
  | 'theory'
  | 'explanation'
