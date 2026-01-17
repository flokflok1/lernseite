/**
 * LernsystemX - Authoring Actions API
 *
 * API endpoints for DB-driven Quick-Actions in KI-Editor:
 * - Get actions by category (course_builder, chat, chapter, lesson, method, content)
 * - Execute actions with context
 * - Create, update, delete actions (admin only)
 * - Usage statistics
 *
 * Phase: DB-Zentriertes KI-Authoring (2025-12)
 */

import http from './http'

// ============================================================================
// Types & Interfaces
// ============================================================================

export type ActionCategory = 'course_builder' | 'chat' | 'chapter' | 'lesson' | 'method' | 'content'
export type ActionType = 'chat' | 'generate' | 'edit' | 'delete' | 'preview'
export type OutputFormat = 'text' | 'json' | 'markdown' | 'html'
export type EntityType = 'course' | 'chapter' | 'lesson' | 'method'

export interface AuthoringAction {
  action_id: string
  action_key: string
  category: ActionCategory
  label: string
  description?: string
  icon?: string
  color?: string
  prompt_template: string
  mode?: string
  context_entity?: EntityType
  requires_context?: Record<string, boolean>
  action_type: ActionType
  requires_confirmation: boolean
  confirmation_label?: string
  output_format?: OutputFormat
  output_entity?: string
  lm_types?: number[]
  is_premium: boolean
  order_index: number
  is_system: boolean
}

export interface ActionCategory {
  category: string
  action_count: number
  system_count?: number
}

export interface ActionContext {
  course_id?: string
  chapter_id?: string
  lesson_id?: string
  method_id?: string
  selected_content?: string
  chapter_title?: string
  lesson_title?: string
  method_title?: string
  [key: string]: unknown
}

export interface ActionVariables {
  topic?: string
  difficulty?: string
  target_audience?: string
  [key: string]: unknown
}

export interface ExecuteActionRequest {
  action_id?: string
  action_key?: string
  course_id?: string
  context?: ActionContext
  variables?: ActionVariables
  session_id?: string
}

export interface ExecuteActionResponse {
  session_id: string
  response: string
  generated_content?: Record<string, unknown>
  has_content: boolean
  requires_confirmation: boolean
  output_entity?: string
  action_id: string
  action_key: string
  tokens_used?: number
  cost_eur?: number
}

export interface CreateActionRequest {
  action_key: string
  category: ActionCategory
  label: string
  description?: string
  icon?: string
  color?: string
  prompt_template: string
  mode?: string
  context_entity?: EntityType
  requires_context?: Record<string, boolean>
  action_type?: ActionType
  requires_confirmation?: boolean
  confirmation_label?: string
  output_format?: OutputFormat
  output_entity?: string
  lm_types?: number[]
  roles_allowed?: string[]
  is_premium?: boolean
  order_index?: number
}

export interface UpdateActionRequest {
  category?: ActionCategory
  label?: string
  description?: string
  icon?: string
  color?: string
  prompt_template?: string
  mode?: string
  context_entity?: EntityType
  requires_context?: Record<string, boolean>
  action_type?: ActionType
  requires_confirmation?: boolean
  confirmation_label?: string
  output_format?: OutputFormat
  output_entity?: string
  lm_types?: number[]
  roles_allowed?: string[]
  is_premium?: boolean
  order_index?: number
  is_active?: boolean
}

export interface ActionUsageStats {
  total_uses: number
  successful_uses: number
  confirmed_uses?: number
  total_tokens?: number
  total_cost?: number
  avg_response_time?: number
  actions_used?: number
  unique_users?: number
  popular_actions?: PopularAction[]
}

export interface PopularAction {
  action_id: string
  action_key: string
  category: string
  label: string
  icon?: string
  usage_count: number
  success_count: number
}

// ============================================================================
// LM Suggestions Types
// ============================================================================

export type LMGroup = 'A' | 'B' | 'C' | 'D' | 'E' | 'F'
export type LMMethodType = 'explanatory' | 'practice' | 'exam' | 'pro' | 'it' | 'collaborative'
export type KIUsage = 'intensive' | 'medium' | 'optional'

export interface LMSuggestion {
  lm_id: number
  name: string
  group: LMGroup
  method_type: LMMethodType
  description: string
  reason: string  // KI-generierte Begründung
  priority: number
  icon: string
  ki_usage: KIUsage
}

export interface LMSuggestionsRequest {
  lesson_title: string
  lesson_content?: string
  chapter_title?: string
  course_title?: string
  existing_lm_ids?: number[]
  max_suggestions?: number
}

export interface LMSuggestionsResponse {
  suggestions: LMSuggestion[]
  lesson_title: string
  existing_count: number
  ai_generated?: boolean
}

export interface LMMethod {
  lm_id: number
  name: string
  description: string
  icon: string
  ki_usage: KIUsage
}

export interface LMGroup {
  name: string
  icon: string
  methods: LMMethod[]
}

export type LMGroupsResponse = Record<string, LMGroup>

// ============================================================================
// API Functions
// ============================================================================

/**
 * Get all active authoring actions
 */
export async function getActions(category?: ActionCategory): Promise<{
  actions: AuthoringAction[]
  categories: ActionCategory[]
}> {
  const params = category ? `?category=${category}` : ''
  const response = await http.get(`/admin/ai-editor/actions${params}`)
  return response.data.data
}

/**
 * Get actions for a specific category
 */
export async function getActionsByCategory(category: ActionCategory): Promise<AuthoringAction[]> {
  const response = await http.get(`/admin/ai-editor/actions/${category}`)
  return response.data.data.actions
}

/**
 * Get actions that apply to a specific entity type
 */
export async function getActionsForEntity(entityType: EntityType): Promise<AuthoringAction[]> {
  const response = await http.get(`/admin/ai-editor/actions/entity/${entityType}`)
  return response.data.data.actions
}

/**
 * Get a single action by ID
 */
export async function getAction(actionId: string): Promise<AuthoringAction> {
  const response = await http.get(`/admin/ai-editor/actions/${actionId}`)
  return response.data.data
}

/**
 * Execute an authoring action
 */
export async function executeAction(request: ExecuteActionRequest): Promise<ExecuteActionResponse> {
  const response = await http.post('/admin/ai-editor/actions/execute', request)
  return response.data.data
}

/**
 * Create a new authoring action (admin only)
 */
export async function createAction(data: CreateActionRequest): Promise<AuthoringAction> {
  const response = await http.post('/admin/ai-editor/actions', data)
  return response.data.data
}

/**
 * Update an existing action (admin only)
 */
export async function updateAction(actionId: string, data: UpdateActionRequest): Promise<AuthoringAction> {
  const response = await http.put(`/admin/ai-editor/actions/${actionId}`, data)
  return response.data.data
}

/**
 * Delete an action (admin only, soft delete)
 */
export async function deleteAction(actionId: string): Promise<void> {
  await http.delete(`/admin/ai-editor/actions/${actionId}`)
}

/**
 * Get usage statistics for actions
 */
export async function getActionStats(actionId?: string, days: number = 30): Promise<ActionUsageStats> {
  const params = new URLSearchParams()
  if (actionId) params.append('action_id', actionId)
  if (days) params.append('days', days.toString())

  const response = await http.get(`/admin/ai-editor/actions/stats?${params.toString()}`)
  return response.data.data
}

// ============================================================================
// LM Suggestions API Functions
// ============================================================================

/**
 * Get AI-powered learning method suggestions for a lesson.
 *
 * The AI analyzes the lesson context and suggests appropriate
 * learning methods from the 31 available types.
 */
export async function getLMSuggestions(request: LMSuggestionsRequest): Promise<LMSuggestionsResponse> {
  const response = await http.post('/admin/ai-editor/lm-suggestions', request)
  return response.data.data
}

/**
 * Get AI-powered learning method suggestions (async version).
 * Uses the AI to analyze context - may take longer but provides intelligent suggestions.
 */
export async function getLMSuggestionsAI(request: LMSuggestionsRequest): Promise<LMSuggestionsResponse> {
  const response = await http.post('/admin/ai-editor/lm-suggestions/async', request)
  return response.data.data
}

/**
 * Get all 31 learning methods grouped by category.
 * For manual selection when user wants to choose themselves.
 */
export async function getAllLearningMethods(): Promise<LMGroupsResponse> {
  const response = await http.get('/admin/ai-editor/learning-methods')
  return response.data.data
}

/**
 * Get display name for LM group
 */
export function getLMGroupName(group: string): string {
  const names: Record<string, string> = {
    'A': 'Erklärend',
    'B': 'Praxis',
    'C': 'Prüfung',
    'D': 'Pro',
    'E': 'IT',
    'F': 'Kollaborativ'
  }
  return names[group] || group
}

/**
 * Get icon for LM group
 */
export function getLMGroupIcon(group: string): string {
  const icons: Record<string, string> = {
    'A': '📖',
    'B': '✏️',
    'C': '📝',
    'D': '🎓',
    'E': '💻',
    'F': '👥'
  }
  return icons[group] || '📋'
}

/**
 * Get color class for KI usage intensity
 */
export function getKIUsageColor(usage: KIUsage): string {
  const colors: Record<KIUsage, string> = {
    'intensive': 'text-purple-600',
    'medium': 'text-blue-600',
    'optional': 'text-gray-600'
  }
  return colors[usage] || 'text-gray-600'
}

/**
 * Get label for KI usage intensity
 */
export function getKIUsageLabel(usage: KIUsage): string {
  const labels: Record<KIUsage, string> = {
    'intensive': 'KI-intensiv',
    'medium': 'Mittlere KI',
    'optional': 'KI optional'
  }
  return labels[usage] || usage
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Group actions by category
 */
export function groupActionsByCategory(actions: AuthoringAction[]): Record<string, AuthoringAction[]> {
  return actions.reduce((groups, action) => {
    const category = action.category
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(action)
    return groups
  }, {} as Record<string, AuthoringAction[]>)
}

/**
 * Filter actions by learning method type
 */
export function filterActionsByLmType(actions: AuthoringAction[], lmType: number): AuthoringAction[] {
  return actions.filter(action => {
    if (!action.lm_types || action.lm_types.length === 0) {
      return true // Action applies to all LM types
    }
    return action.lm_types.includes(lmType)
  })
}

/**
 * Get icon for action category
 */
export function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    'course_builder': '🏗️',
    'chat': '💬',
    'chapter': '📑',
    'lesson': '📝',
    'method': '🎯',
    'content': '✨'
  }
  return icons[category] || '📋'
}

/**
 * Get color class for action type
 */
export function getActionTypeColor(actionType: ActionType): string {
  const colors: Record<ActionType, string> = {
    'chat': 'blue',
    'generate': 'green',
    'edit': 'yellow',
    'delete': 'red',
    'preview': 'gray'
  }
  return colors[actionType] || 'gray'
}

// Export all functions as default
export default {
  // Actions API
  getActions,
  getActionsByCategory,
  getActionsForEntity,
  getAction,
  executeAction,
  createAction,
  updateAction,
  deleteAction,
  getActionStats,
  // LM Suggestions API
  getLMSuggestions,
  getLMSuggestionsAI,
  getAllLearningMethods,
  // Helper functions
  groupActionsByCategory,
  filterActionsByLmType,
  getCategoryIcon,
  getActionTypeColor,
  getLMGroupName,
  getLMGroupIcon,
  getKIUsageColor,
  getKIUsageLabel
}
