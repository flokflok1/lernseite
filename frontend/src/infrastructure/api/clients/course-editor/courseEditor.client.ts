/**
 * Course Editor API Client
 *
 * API client for AI-powered course editor functionality:
 * - Chat interface for AI assistance
 * - Content generation with templates
 * - Variant selection and management
 * - Project and session management
 * - Generation history
 *
 * All endpoints under /api/v1/ai/ namespace
 */

import http from '../http'

// ============================================================================
// Request/Response Types
// ============================================================================

/**
 * Chat Message Type
 */
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

/**
 * AI Chat Request
 */
export interface AIChartRequest {
  sessionId: string
  message: string
  context?: {
    projectId?: string
    chapterId?: string
    lessonId?: string
  }
  systemPrompt?: string
}

/**
 * AI Chat Response
 */
export interface AIChatResponse {
  message: ChatMessage
  tokensUsed: number
  isStreaming?: boolean
}

/**
 * Content Generation Request
 */
export interface GenerateContentRequest {
  projectId: string
  contentType: 'explanation' | 'example' | 'exercise' | 'quiz'
  templateId?: string
  customPrompt?: string
  temperature?: number
  maxTokens?: number
}

/**
 * Generated Content Response
 */
export interface GeneratedContentResponse {
  id: string
  content: string
  variants: Variant[]
  metadata: {
    model: string
    temperature: number
    promptId: string
    generatedAt: Date
  }
}

/**
 * Variant for generated content
 */
export interface Variant {
  id: string
  content: string
  style: 'formal' | 'casual' | 'academic' | 'simplified'
  score: number
  isSelected: boolean
}

/**
 * Variant Selection Request
 */
export interface SelectVariantRequest {
  generatedContentId: string
  variantId: string
}

/**
 * Template Type
 */
export interface Template {
  id: string
  name: string
  description: string
  category: string
  prompt: string
  contentType: 'explanation' | 'example' | 'exercise' | 'quiz'
  isPublic: boolean
  createdAt: Date
}

/**
 * Project Type
 */
export interface Project {
  id: string
  title: string
  description: string
  status: 'draft' | 'published' | 'archived'
  chapters: string[]
  metadata: {
    createdAt: Date
    updatedAt: Date
    createdBy: string
    version: number
  }
}

/**
 * Generation History Entry
 */
export interface HistoryEntry {
  id: string
  projectId: string
  contentId: string
  contentType: 'explanation' | 'example' | 'exercise' | 'quiz'
  generatedContent: string
  variants: Variant[]
  selectedVariantId?: string
  createdAt: Date
  model: string
  tokensUsed: number
}

/**
 * Chat Session Type
 */
export interface ChatSession {
  id: string
  projectId: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Send chat message to AI assistant
 *
 * POST /api/v1/ai/chat
 *
 * @param request - Chat request with message and context
 * @returns AI response message
 */
export const sendChatMessage = async (
  request: AIChartRequest
): Promise<AIChatResponse> => {
  const response = await http.post<{
    success: boolean
    data: AIChatResponse
  }>('/ai/chat', request, {
    timeout: 60000 // 60 seconds for AI response
  })
  return response.data.data
}

/**
 * Generate content using AI
 *
 * POST /api/v1/ai/generate
 *
 * @param request - Generation request with template and parameters
 * @returns Generated content with variants
 */
export const generateContent = async (
  request: GenerateContentRequest
): Promise<GeneratedContentResponse> => {
  const response = await http.post<{
    success: boolean
    data: GeneratedContentResponse
  }>('/ai/generate', request, {
    timeout: 120000 // 2 minutes for generation
  })
  return response.data.data
}

/**
 * Generate multiple variants for content
 *
 * POST /api/v1/ai/variants
 *
 * @param contentId - ID of previously generated content
 * @param count - Number of variants to generate (default 3)
 * @returns Array of new variants
 */
export const generateVariants = async (
  contentId: string,
  count: number = 3
): Promise<Variant[]> => {
  const response = await http.post<{
    success: boolean
    data: { variants: Variant[] }
  }>('/ai/variants', {
    contentId,
    count
  }, {
    timeout: 90000 // 90 seconds for variant generation
  })
  return response.data.data.variants
}

/**
 * Get all available templates
 *
 * GET /api/v1/ai/templates
 *
 * @param category - Optional filter by category
 * @returns Array of templates
 */
export const getTemplates = async (
  category?: string
): Promise<Template[]> => {
  const response = await http.get<{
    success: boolean
    data: { templates: Template[] }
  }>('/ai/templates', {
    params: category ? { category } : undefined
  })
  return response.data.data.templates
}

/**
 * Get all projects for current user
 *
 * GET /api/v1/ai/projects
 *
 * @param limit - Max results (default 20, max 100)
 * @param offset - Pagination offset (default 0)
 * @returns Array of projects
 */
export const getProjects = async (
  limit: number = 20,
  offset: number = 0
): Promise<{ projects: Project[]; total: number }> => {
  const response = await http.get<{
    success: boolean
    data: { projects: Project[]; total: number }
  }>('/ai/projects', {
    params: { limit, offset }
  })
  return response.data.data
}

/**
 * Get single project by ID
 *
 * GET /api/v1/ai/projects/:id
 *
 * @param projectId - ID of project to fetch
 * @returns Project details
 */
export const getProject = async (
  projectId: string
): Promise<Project> => {
  const response = await http.get<{
    success: boolean
    data: Project
  }>(`/ai/projects/${projectId}`)
  return response.data.data
}

/**
 * Get generation history for project
 *
 * GET /api/v1/ai/history
 *
 * @param projectId - Project ID to get history for
 * @param limit - Max results (default 50, max 200)
 * @param offset - Pagination offset (default 0)
 * @returns Array of history entries
 */
export const getGenerationHistory = async (
  projectId: string,
  limit: number = 50,
  offset: number = 0
): Promise<{ history: HistoryEntry[]; total: number }> => {
  const response = await http.get<{
    success: boolean
    data: { history: HistoryEntry[]; total: number }
  }>('/ai/history', {
    params: { projectId, limit, offset }
  })
  return response.data.data
}

/**
 * Get chat session by ID
 *
 * GET /api/v1/ai/sessions/:id
 *
 * @param sessionId - ID of chat session to fetch
 * @returns Chat session with message history
 */
export const getChatSession = async (
  sessionId: string
): Promise<ChatSession> => {
  const response = await http.get<{
    success: boolean
    data: ChatSession
  }>(`/ai/sessions/${sessionId}`)
  return response.data.data
}

// ============================================================================
// Batch Operations
// ============================================================================

/**
 * Select a variant (simplified wrapper)
 *
 * @param generatedContentId - ID of generated content
 * @param variantId - ID of variant to select
 */
export const selectVariant = async (
  generatedContentId: string,
  variantId: string
): Promise<void> => {
  await http.post('/ai/variants/select', {
    generatedContentId,
    variantId
  })
}

/**
 * Approve generated content
 *
 * @param contentId - ID of content to approve
 */
export const approveContent = async (
  contentId: string
): Promise<void> => {
  await http.post(`/ai/content/${contentId}/approve`, {})
}

/**
 * Delete generated content
 *
 * @param contentId - ID of content to delete
 */
export const deleteContent = async (
  contentId: string
): Promise<void> => {
  await http.delete(`/ai/content/${contentId}`)
}
