/**
 * ChapterEditor Component Types
 * Type definitions for chapter editor functionality
 */

import type { AdminChapter, AdminLesson, AdminLearningMethod, LearningMethodType } from '@/infrastructure/api/clients/admin'
import type { LsxPanel } from '@/application/stores/modules/desktop'

export interface ChapterEditorProps {
  panel: LsxPanel
}

export interface ChapterEditorEmits {
  (e: 'close'): void
}

export interface ChapterForm {
  title: string
  description: string
  duration_minutes?: number
}

export interface VideoItem {
  title: string
  url: string
}

export interface MethodGroupStats {
  total: number
  active: number
  published: number
}

export interface DragState {
  draggedIndex: number | null
  targetIndex: number | null
}

export interface GroupInfo {
  name: string
  colors: {
    bg: string
    text: string
  }
  tier: string
}

export interface ChapterEditorState {
  chapter: AdminChapter | null
  lessons: AdminLesson[]
  loading: boolean
  loadingLessons: boolean
  loadingMethods: boolean
  error: string | null
  saveStatus: 'idle' | 'saving' | 'saved' | 'error'
  activeTab: 'info' | 'theory' | 'videos' | 'methods' | 'lessons'
  isGenerating: boolean
  theoryContent: string
  videos: VideoItem[]
  learningMethods: AdminLearningMethod[]
  methodTypes: LearningMethodType[]
  methodStats: Record<string, MethodGroupStats>
  dragState: DragState
  form: ChapterForm
}
