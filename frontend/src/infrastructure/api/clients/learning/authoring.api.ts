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

import http from '@/infrastructure/api/http'
import type {
  ActionCategory,
  ActionType,
  AuthoringAction,
  ActionContext,
  ActionVariables,
  EntityType,
  OutputFormat,
  ExecuteActionRequest,
  ExecuteActionResponse,
  CreateActionRequest,
  UpdateActionRequest,
  ActionUsageStats,
  PopularAction,
  LMGroupAPIInfo,
  LMGroupsAPIResponse
} from './types'

// ============================================================================
// Re-export types for backwards compatibility
// ============================================================================

export type {
  ActionCategory,
  ActionType,
  OutputFormat,
  EntityType,
  AuthoringAction,
  ActionContext,
  ActionVariables,
  ExecuteActionRequest,
  ExecuteActionResponse,
  CreateActionRequest,
  UpdateActionRequest,
  ActionUsageStats,
  PopularAction,
  LMGroupAPIInfo,
  LMGroupsAPIResponse
}

// Re-export ActionCategory interface under a distinct name to avoid collision
// with the ActionCategory type alias
export type { ActionCategoryInfo as ActionCategory_Info } from './types'

// ============================================================================
// Actions API Functions
// ============================================================================

/**
 * Get all active authoring actions
 */
export async function getActions(category?: ActionCategory): Promise<{
  actions: AuthoringAction[]
  categories: ActionCategory[]
}> {
  const params = category ? `?category=${category}` : ''
  const response = await http.get(`/course-editor/ai/actions${params}`)
  return response.data.data
}

/**
 * Get actions for a specific category
 */
export async function getActionsByCategory(category: ActionCategory): Promise<AuthoringAction[]> {
  const response = await http.get(`/course-editor/ai/actions/${category}`)
  return response.data.data.actions
}

/**
 * Get actions that apply to a specific entity type
 */
export async function getActionsForEntity(entityType: EntityType): Promise<AuthoringAction[]> {
  const response = await http.get(`/course-editor/ai/actions/entity/${entityType}`)
  return response.data.data.actions
}

/**
 * Get a single action by ID
 */
export async function getAction(actionId: string): Promise<AuthoringAction> {
  const response = await http.get(`/course-editor/ai/actions/${actionId}`)
  return response.data.data
}

/**
 * Execute an authoring action
 */
export async function executeAction(request: ExecuteActionRequest): Promise<ExecuteActionResponse> {
  const response = await http.post('/course-editor/ai/actions/execute', request)
  return response.data.data
}

/**
 * Create a new authoring action (admin only)
 */
export async function createAction(data: CreateActionRequest): Promise<AuthoringAction> {
  const response = await http.post('/course-editor/ai/actions', data)
  return response.data.data
}

/**
 * Update an existing action (admin only)
 */
export async function updateAction(actionId: string, data: UpdateActionRequest): Promise<AuthoringAction> {
  const response = await http.put(`/course-editor/ai/actions/${actionId}`, data)
  return response.data.data
}

/**
 * Delete an action (admin only, soft delete)
 */
export async function deleteAction(actionId: string): Promise<void> {
  await http.delete(`/course-editor/ai/actions/${actionId}`)
}

/**
 * Get usage statistics for actions
 */
export async function getActionStats(actionId?: string, days: number = 30): Promise<ActionUsageStats> {
  const params = new URLSearchParams()
  if (actionId) params.append('action_id', actionId)
  if (days) params.append('days', days.toString())

  const response = await http.get(`/course-editor/ai/actions/stats?${params.toString()}`)
  return response.data.data
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
  // Helper functions
  groupActionsByCategory,
  filterActionsByLmType,
  getCategoryIcon,
  getActionTypeColor
}
