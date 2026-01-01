/**
 * Course Authoring API
 *
 * API calls for KI-Kurs-Builder chat-based course authoring.
 * Phase D4 - KI-Kurs-Builder
 */

import http from './http'

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

// API Functions

/**
 * Create a new course authoring session
 */
export async function createSession(courseId: string, modelProfile?: string) {
  const response = await http.post('/admin/course-authoring/sessions', {
    course_id: courseId,
    model_profile: modelProfile || 'anthropic-claude-sonnet'
  })
  return response.data
}

/**
 * Get session details
 */
export async function getSession(sessionId: string) {
  const response = await http.get(`/admin/course-authoring/sessions/${sessionId}`)
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
  }
) {
  const response = await http.post(`/admin/course-authoring/sessions/${sessionId}/chat`, {
    message,
    mode: options?.mode,
    file_ids: options?.file_ids || []
  })
  return response.data
}

/**
 * Finalize session and create real course content
 */
export async function finalizeSession(sessionId: string) {
  const response = await http.post(`/admin/course-authoring/sessions/${sessionId}/finalize`)
  return response.data
}

/**
 * Archive (soft delete) session
 */
export async function archiveSession(sessionId: string) {
  const response = await http.delete(`/admin/course-authoring/sessions/${sessionId}`)
  return response.data
}

/**
 * List sessions for a course
 */
export async function listSessions(courseId: string, status?: string) {
  const params = new URLSearchParams()
  if (status) params.append('status', status)

  const url = `/admin/course-authoring/courses/${courseId}/sessions` +
    (params.toString() ? `?${params.toString()}` : '')

  const response = await http.get(url)
  return response.data
}

/**
 * Get available method types
 */
export async function getMethodTypes() {
  const response = await http.get('/admin/course-authoring/method-types')
  return response.data
}

export default {
  createSession,
  getSession,
  sendChatMessage,
  finalizeSession,
  archiveSession,
  listSessions,
  getMethodTypes
}
