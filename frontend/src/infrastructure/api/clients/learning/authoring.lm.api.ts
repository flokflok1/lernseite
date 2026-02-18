/**
 * LernsystemX - Learning Method Suggestions API
 *
 * API endpoints for AI-powered learning method suggestions and
 * database-driven LM group metadata:
 * - Get AI suggestions for lessons
 * - Get all learning methods grouped by category
 * - Get LM groups from database (replaces hardcoded helpers)
 * - Display helpers for LM groups and KI usage
 *
 * Phase: DB-Zentriertes KI-Authoring (2025-12)
 */

import http from '@/infrastructure/api/http'
import type {
  KIUsage,
  LMGroupAPIInfo,
  LMGroupsResponse,
  LMSuggestionsRequest,
  LMSuggestionsResponse
} from './types'

// ============================================================================
// Re-export types for backwards compatibility
// ============================================================================

export type {
  LMGroup,
  LMMethodType,
  KIUsage,
  LMSuggestion,
  LMSuggestionsRequest,
  LMSuggestionsResponse,
  LMMethod,
  LMGroupInfo,
  LMGroupsResponse,
  LMGroupAPIInfo,
  LMGroupsAPIResponse
} from './types'

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
  const response = await http.post('/course-editor/ai/lm-suggestions', request)
  return response.data.data
}

/**
 * Get AI-powered learning method suggestions (async version).
 * Uses the AI to analyze context - may take longer but provides intelligent suggestions.
 */
export async function getLMSuggestionsAI(request: LMSuggestionsRequest): Promise<LMSuggestionsResponse> {
  const response = await http.post('/course-editor/ai/lm-suggestions/async', request)
  return response.data.data
}

/**
 * Get all 31 learning methods grouped by category.
 * For manual selection when user wants to choose themselves.
 */
export async function getAllLearningMethods(): Promise<LMGroupsResponse> {
  const response = await http.get('/course-editor/ai/learning-methods')
  return response.data.data
}

/**
 * Get all learning method groups with tier information from database.
 *
 * This is the database-driven endpoint that returns:
 * - group_code (A, B, C, ...)
 * - name (Erklaerend, Praxis, Pruefung, ...)
 * - description
 * - icon/emoji
 * - tier (basic, premium, enterprise)
 * - sort_order
 * - is_active
 *
 * REPLACES hardcoded getLMGroupName() and getLMGroupIcon() helper functions.
 * This endpoint serves as the single source of truth for group metadata.
 *
 * @returns LMGroupInfo[] - Array of all active learning method groups with tier info
 */
export async function getLMGroups(): Promise<LMGroupAPIInfo[]> {
  const response = await http.get('/learning-methods/groups')
  return response.data.data
}

// ============================================================================
// Display Helper Functions
// ============================================================================

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

// Export all functions as default
export default {
  getLMSuggestions,
  getLMSuggestionsAI,
  getAllLearningMethods,
  getLMGroups,
  getLMGroupName,
  getLMGroupIcon,
  getKIUsageColor,
  getKIUsageLabel
}
