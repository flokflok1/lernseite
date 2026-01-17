/**
 * LernsystemX - AI Editor API
 *
 * API endpoints for KI-Authoring-Editor:
 * - Session Management
 * - PDF Upload & Analysis
 * - Content Generation
 * - Templates
 *
 * Phase D4 - KI-Authoring-Editor
 */

import http from './http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export type SessionStatus = 'draft' | 'in_progress' | 'review' | 'completed' | 'cancelled'
export type SourceType = 'manual' | 'pdf' | 'url' | 'existing_chapter' | 'template'
export type VariantType = 'theory' | 'lesson' | 'method' | 'quiz' | 'summary' | 'full_chapter'
export type SessionStep = 'source_selection' | 'theory_generation' | 'lesson_generation' | 'method_generation' | 'quiz_generation' | 'review' | 'finalize'

export interface AIEditorSession {
  session_id: string
  user_id: string
  course_id: string
  chapter_id?: string | null
  session_name?: string | null
  status: SessionStatus
  source_type: SourceType
  source_data: Record<string, unknown>
  ai_config: Record<string, unknown>
  generated_theory?: Record<string, unknown> | null
  generated_lessons: unknown[]
  generated_methods: unknown[]
  current_step: string
  steps_completed: string[]
  started_at: string
  last_activity_at: string
  completed_at?: string | null
  created_at: string
  updated_at: string
  // Joined fields
  user_email?: string
  course_title?: string
  chapter_title?: string
}

export interface AIEditorSessionListItem {
  session_id: string
  session_name?: string | null
  course_id: string
  course_title?: string | null
  status: SessionStatus
  current_step: string
  source_type: SourceType
  last_activity_at: string
  created_at: string
}

export interface AIEditorVariant {
  variant_id: string
  session_id: string
  variant_type: VariantType
  variant_index: number
  content: Record<string, unknown>
  ai_provider?: string | null
  ai_model?: string | null
  is_selected: boolean
  user_rating?: number | null
  user_feedback?: string | null
  generation_duration_ms?: number | null
  created_at: string
}

export interface AIEditorSnapshot {
  snapshot_id: string
  session_id: string
  description?: string | null
  sequence_number: number
  is_current: boolean
  created_at: string
}

export interface AIEditorTemplate {
  template_id: string
  template_name: string
  template_key: string
  category: string
  description?: string | null
  template_config: Record<string, unknown>
  is_system: boolean
  usage_count: number
  created_at: string
}

export interface PDFUploadResponse {
  file_hash: string
  original_filename: string
  file_size_bytes: number
  page_count: number
  extracted_text: string
  structure_analysis: {
    headings: Array<{ text: string; line: number; level: number }>
    sections: Array<{ title: string; start_line: number; headings: unknown[] }>
    key_topics: Array<{ topic: string; count: number }>
    word_count: number
    paragraph_count: number
    estimated_reading_time_min: number
  }
  metadata: Record<string, string>
  summary: string
  recommendations: {
    suggested_chapters: number
    suggested_lessons_per_chapter: number
    complexity_level: string
    suitable_methods: number[]
    notes: string[]
  }
  word_count: number
  estimated_reading_time: number
  from_cache: boolean
}

export interface AIEditorStats {
  total_sessions: number
  active_sessions: number
  completed_sessions: number
  total_chapters_created: number
  total_tokens_used: number
  avg_generation_time_ms: number
}

export interface CreateSessionRequest {
  course_id: string
  session_name?: string
  source_type?: SourceType
  template_key?: string
  chapter_id?: string
}

export interface UpdateSessionRequest {
  session_name?: string
  status?: SessionStatus
  current_step?: SessionStep
  ai_config?: Record<string, unknown>
}

export interface SetSourceDataRequest {
  source_type: SourceType
  source_data: Record<string, unknown>
}

export interface GenerateContentRequest {
  content_type: VariantType
  prompt?: string
  generate_variants?: number
  ai_config_override?: Record<string, unknown>
}

export interface FinalizeSessionRequest {
  create_chapter?: boolean
  create_lessons?: boolean
  create_methods?: boolean
  chapter_title?: string
  publish_immediately?: boolean
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * List user's AI authoring sessions
 */
export async function listSessions(status?: SessionStatus, limit: number = 20): Promise<AIEditorSessionListItem[]> {
  const params = new URLSearchParams()
  if (status) params.append('status', status)
  if (limit) params.append('limit', limit.toString())

  const response = await http.get(`/admin/ai-editor/sessions?${params.toString()}`)
  return response.data.sessions
}

/**
 * Create new AI authoring session
 */
export async function createSession(data: CreateSessionRequest): Promise<AIEditorSession> {
  const response = await http.post('/admin/ai-editor/sessions', data)
  return response.data.session
}

/**
 * Get session details
 */
export async function getSession(sessionId: string): Promise<AIEditorSession> {
  const response = await http.get(`/admin/ai-editor/sessions/${sessionId}`)
  return response.data.session
}

/**
 * Update session
 */
export async function updateSession(sessionId: string, data: UpdateSessionRequest): Promise<AIEditorSession> {
  const response = await http.patch(`/admin/ai-editor/sessions/${sessionId}`, data)
  return response.data.session
}

/**
 * Delete session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await http.delete(`/admin/ai-editor/sessions/${sessionId}`)
}

/**
 * Set source data for session
 */
export async function setSourceData(sessionId: string, data: SetSourceDataRequest): Promise<AIEditorSession> {
  const response = await http.post(`/admin/ai-editor/sessions/${sessionId}/source`, data)
  return response.data.session
}

export interface GenerateContentResponse {
  success: boolean
  message: string
  step?: string
  variant_id?: string
  prompt_code?: string
  tokens_used?: number
  cost_eur?: number
  data?: Record<string, unknown>
  job_id?: string  // For async generation (future)
}

/**
 * Start AI content generation
 */
export async function generateContent(sessionId: string, data: GenerateContentRequest): Promise<GenerateContentResponse> {
  const response = await http.post(`/admin/ai-editor/sessions/${sessionId}/generate`, data)
  return response.data
}

/**
 * Finalize session and create chapter
 */
export async function finalizeSession(sessionId: string, data: FinalizeSessionRequest): Promise<{ chapter_id?: string; message: string }> {
  const response = await http.post(`/admin/ai-editor/sessions/${sessionId}/finalize`, data)
  return response.data
}

/**
 * Get variants for session
 */
export async function getVariants(sessionId: string, type?: VariantType): Promise<AIEditorVariant[]> {
  const params = type ? `?type=${type}` : ''
  const response = await http.get(`/admin/ai-editor/sessions/${sessionId}/variants${params}`)
  return response.data.variants
}

/**
 * Select a variant
 */
export async function selectVariant(sessionId: string, variantId: string): Promise<AIEditorVariant> {
  const response = await http.post(`/admin/ai-editor/sessions/${sessionId}/variants/select`, { variant_id: variantId })
  return response.data.variant
}

/**
 * Rate a variant
 */
export async function rateVariant(sessionId: string, variantId: string, rating: number, feedback?: string): Promise<AIEditorVariant> {
  const response = await http.post(`/admin/ai-editor/sessions/${sessionId}/variants/rate`, {
    variant_id: variantId,
    rating,
    feedback
  })
  return response.data.variant
}

/**
 * Get snapshots for session
 */
export async function getSnapshots(sessionId: string): Promise<AIEditorSnapshot[]> {
  const response = await http.get(`/admin/ai-editor/sessions/${sessionId}/snapshots`)
  return response.data.snapshots
}

/**
 * Create session snapshot
 */
export async function createSnapshot(sessionId: string, description?: string): Promise<AIEditorSnapshot> {
  const response = await http.post(`/admin/ai-editor/sessions/${sessionId}/snapshots`, { description })
  return response.data.snapshot
}

/**
 * Restore snapshot
 */
export async function restoreSnapshot(sessionId: string, snapshotId: string): Promise<AIEditorSession> {
  const response = await http.post(`/admin/ai-editor/sessions/${sessionId}/snapshots/${snapshotId}/restore`)
  return response.data.session
}

/**
 * Upload and analyze PDF
 */
export async function uploadPDF(file: File): Promise<PDFUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await http.post('/admin/ai-editor/upload-pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

/**
 * Get available templates
 */
export async function getTemplates(category?: string): Promise<AIEditorTemplate[]> {
  const params = category ? `?category=${category}` : ''
  const response = await http.get(`/admin/ai-editor/templates${params}`)
  return response.data.templates
}

/**
 * Get user stats
 */
export async function getStats(): Promise<AIEditorStats> {
  const response = await http.get('/admin/ai-editor/stats')
  return response.data.stats
}

// Export all functions as default
export default {
  listSessions,
  createSession,
  getSession,
  updateSession,
  deleteSession,
  setSourceData,
  generateContent,
  finalizeSession,
  getVariants,
  selectVariant,
  rateVariant,
  getSnapshots,
  createSnapshot,
  restoreSnapshot,
  uploadPDF,
  getTemplates,
  getStats
}
