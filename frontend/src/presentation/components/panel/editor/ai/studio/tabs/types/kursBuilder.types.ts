/**
 * Shared types for the KursBuilder tab composables.
 *
 * @module studio/tabs/composables/kursBuilder.types
 */

export interface Course {
  course_id: string
  title: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  operations?: string[]
  error?: boolean
}

export interface CourseFile {
  id: string
  name: string
  type: string
  size: number
  parsed: boolean
  url?: string
}

export interface Session {
  session_id: string
  course_id: string
  status: 'active' | 'finalized' | 'archived'
  draft_structure: DraftStructure
  chat_history: ChatMessage[]
  total_tokens_used: number
}

export interface DraftStructure {
  chapters?: Chapter[]
  activity_log?: any[]
}

export interface Chapter {
  id: string
  title: string
  description?: string
  lessons?: Lesson[]
}

export interface Lesson {
  id: string
  title: string
  description?: string
  content?: any
  duration_minutes?: number
  methods?: { id: string; type: string; title?: string }[]
}

export interface QuickAction {
  action_id: string
  action_key: string
  label: string
  icon: string
  prompt_template: string
  mode?: string
  color?: string
}

export interface SelectedContext {
  type: 'chapter' | 'lesson' | 'method'
  id: string
  title: string
  data: Chapter | Lesson | null
  parentChapter?: Chapter
}

export interface PendingAction {
  type: 'create' | 'update' | 'delete'
  entity: 'chapter' | 'lesson' | 'method' | 'quiz'
  actionKey: string
  generatedData: any
  previewText: string
  parentChapter?: Chapter
  session_id?: string
}
