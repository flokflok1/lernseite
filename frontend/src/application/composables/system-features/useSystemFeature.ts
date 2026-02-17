/**
 * useSystemFeature Composable
 *
 * Base composable for all 25 System-Features.
 * Provides feature availability checking, config loading,
 * and course/chapter-level feature status.
 *
 * Usage:
 *   const { isAvailable, isLoading, featureConfig, checkAvailability }
 *     = useSystemFeature('whiteboard_engine')
 */

import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { apiClient } from '@/infrastructure/api/clients/config/apiClient'
import type {
  SystemFeatureCode,
  SystemFeatureCategory,
  SystemFeature,
  FeatureStatus
} from '@/domain/models/system-features'

const BASE_URL = '/api/v1/system-features'

// Global feature cache (shared across all instances)
const featureCache = ref<Map<SystemFeatureCode, SystemFeature>>(new Map())
const cacheLoaded = ref(false)

/**
 * Category lookup for feature codes.
 * Maps each feature_code to its DB category for API routing.
 */
const FEATURE_CATEGORY_MAP: Record<SystemFeatureCode, SystemFeatureCategory> = {
  whiteboard_engine: 'interactive_tools',
  it_sandbox: 'it_environments',
  speech_to_text: 'audio',
  ihk_exam_system: 'exam_systems',
  practical_exam_engine: 'exam_systems',
  comprehension_checker: 'tutor',
  chapter_completion_system: 'exam_systems',
  adaptive_difficulty: 'gamification',
  daily_recall: 'gamification',
  xp_quest_system: 'gamification',
  npc_tutor: 'tutor',
  socratic_dialog: 'tutor',
  peer_instruction: 'collaboration',
  team_case: 'collaboration',
  peer_review: 'collaboration',
  learning_journal: 'collaboration',
  project_portfolio: 'collaboration',
  project_based_learning: 'collaboration',
  inverted_classroom: 'collaboration',
  code_sandbox: 'it_environments',
  network_simulation: 'it_environments',
  terminal_access: 'it_environments',
  timer_wrapper: 'meta_features',
  mindmap_generator: 'visualization',
  learning_path_generator: 'learning_paths'
}

export interface UseSystemFeatureReturn {
  isLoading: Ref<boolean>
  error: Ref<string | null>
  isAvailable: Ref<boolean>
  featureConfig: Ref<Record<string, unknown>>
  featureData: ComputedRef<SystemFeature | null>
  category: SystemFeatureCategory
  checkAvailability: () => Promise<void>
  loadConfig: (courseId?: string) => Promise<void>
}

export function useSystemFeature(featureCode: SystemFeatureCode): UseSystemFeatureReturn {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isAvailable = ref(false)
  const featureConfig = ref<Record<string, unknown>>({})

  const category = FEATURE_CATEGORY_MAP[featureCode]

  const featureData = computed(() => featureCache.value.get(featureCode) ?? null)

  async function checkAvailability(): Promise<void> {
    // Use cache if available
    if (featureCache.value.has(featureCode)) {
      const cached = featureCache.value.get(featureCode)!
      isAvailable.value = cached.active
      featureConfig.value = cached.config ?? {}
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get(`${BASE_URL}/registry/features`)
      const features: SystemFeature[] = response.data?.features ?? []

      // Populate cache with all features
      for (const feature of features) {
        featureCache.value.set(feature.featureCode as SystemFeatureCode, feature)
      }
      cacheLoaded.value = true

      const thisFeature = featureCache.value.get(featureCode)
      isAvailable.value = thisFeature?.active ?? false
      featureConfig.value = thisFeature?.config ?? {}
    } catch (e: any) {
      error.value = e.response?.data?.error || e.message || 'Failed to check feature availability'
      isAvailable.value = false
    } finally {
      isLoading.value = false
    }
  }

  async function loadConfig(courseId?: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      if (courseId) {
        // Load course-level config override
        const response = await apiClient.get(
          `${BASE_URL}/registry/courses/${courseId}/features`
        )
        const courseFeatures = response.data?.features ?? []
        const match = courseFeatures.find(
          (f: any) => f.feature_code === featureCode
        )
        if (match) {
          isAvailable.value = match.enabled ?? false
          featureConfig.value = {
            ...(featureCache.value.get(featureCode)?.config ?? {}),
            ...(match.config_override ?? {})
          }
        }
      } else {
        // Load system-level config
        await checkAvailability()
      }
    } catch (e: any) {
      error.value = e.response?.data?.error || e.message || 'Failed to load feature config'
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    error,
    isAvailable,
    featureConfig,
    featureData,
    category,
    checkAvailability,
    loadConfig
  }
}
