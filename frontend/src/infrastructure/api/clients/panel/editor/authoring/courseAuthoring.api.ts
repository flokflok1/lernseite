/**
 * Course Authoring API
 *
 * API calls for KI-Kurs-Builder chat-based course authoring.
 * Phase D4 - KI-Kurs-Builder
 */

import http from '@/infrastructure/api/http'

// Types
export interface CourseAuthoringSession {
  session_id: string
  course_id: string
  course_title?: string
  status: 'active' | 'finalized' | 'archived'
  model_profile: string
  draft_structure: DraftStructure
  chat_history: ChatMessage[]
  total_tokens_used: number
  total_operations: number
  created_at?: string
  updated_at?: string
  finalized_at?: string
}

export interface DraftStructure {
  chapters?: DraftChapter[]
}

export interface DraftChapter {
  id: string
  title: string
  description?: string
  order_index?: number
  lessons?: DraftLesson[]
}

export interface DraftLesson {
  id: string
  title: string
  description?: string
  order_index?: number
  methods?: DraftMethod[]
}

export interface DraftMethod {
  id: string
  type: string
  title?: string
  data?: Record<string, unknown>
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  operations?: string[]
  error?: boolean
}

export interface MethodType {
  type: string
  name: string
  description: string
  icon: string
  lm_type: number
}

export interface AvailableProvider {
  provider_name: string
  display_name: string
  models: AvailableModel[]
}

export interface AvailableModel {
  model_id: number
  model_name: string
  display_name: string
  is_default: boolean
  context_window?: number
  cost_level?: string
}

// API Functions

/**
 * Create a new course authoring session
 */
export async function createSession(
  courseId: string,
  options?: { modelProfile?: string; providerName?: string; modelName?: string }
) {
  const response = await http.post('/course-editor/ai/sessions', {
    course_id: courseId,
    model_profile: options?.modelProfile || 'anthropic-claude-sonnet',
    provider_name: options?.providerName,
    model_name: options?.modelName,
  })
  return response.data
}

/**
 * Get session details
 */
export async function getSession(sessionId: string) {
  const response = await http.get(`/course-editor/ai/sessions/${sessionId}`)
  return response.data
}

/**
 * Send chat message and get AI response
 */
export async function sendChatMessage(
  sessionId: string,
  message: string,
  options?: {
    mode?: string
    file_ids?: string[]
    focus_chapter_id?: string
    focus_lesson_id?: string
    quality_level?: string
  }
) {
  const response = await http.post(`/course-editor/ai/sessions/${sessionId}/chat`, {
    message,
    mode: options?.mode,
    file_ids: options?.file_ids || [],
    focus_chapter_id: options?.focus_chapter_id,
    focus_lesson_id: options?.focus_lesson_id,
    quality_level: options?.quality_level,
  })
  return response.data
}

/**
 * Finalize session and create real course content
 */
export async function finalizeSession(sessionId: string) {
  const response = await http.post(`/course-editor/ai/sessions/${sessionId}/finalize`)
  return response.data
}

/**
 * Archive (soft delete) session
 */
export async function archiveSession(sessionId: string) {
  const response = await http.delete(`/course-editor/ai/sessions/${sessionId}`)
  return response.data
}

/**
 * List sessions for a course
 */
export async function listSessions(courseId: string, status?: string) {
  const params = new URLSearchParams()
  if (status) params.append('status', status)

  const url = `/course-editor/ai/courses/${courseId}/sessions` +
    (params.toString() ? `?${params.toString()}` : '')

  const response = await http.get(url)
  return response.data
}

/**
 * Get available method types
 */
export async function getMethodTypes() {
  const response = await http.get('/course-editor/ai/method-types')
  return response.data
}

/**
 * Get active providers with their active chat models
 */
export async function getAvailableModels(): Promise<AvailableProvider[]> {
  const response = await http.get('/course-editor/ai/available-models')
  return response.data?.data?.providers ?? []
}

export default {
  createSession,
  getSession,
  sendChatMessage,
  finalizeSession,
  archiveSession,
  listSessions,
  getMethodTypes,
  getAvailableModels,
}
