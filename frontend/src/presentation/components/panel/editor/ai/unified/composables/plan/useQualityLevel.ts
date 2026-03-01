import { ref, computed } from 'vue'
import http from '@/infrastructure/api/http'

export interface QualityLevel {
  level: string
  label: string
  description: string
  icon: string
  estimated_time: string
  token_ratio: number
  pipeline: boolean
  methods_per_lesson: number
  retries: number
}

/**
 * Composable for quality level selection in the AI Editor.
 * Controls token budget, validation strictness, retry behavior, and pipeline mode.
 */
export function useQualityLevel() {
  const levels = ref<QualityLevel[]>([])
  const selectedLevel = ref('standard')
  const isLoading = ref(false)

  const currentLevel = computed<QualityLevel | undefined>(() =>
    levels.value.find((l) => l.level === selectedLevel.value)
  )

  const selectionLabel = computed(() => currentLevel.value?.label ?? 'Standard')

  async function loadQualityLevels(): Promise<void> {
    isLoading.value = true
    try {
      const response = await http.get('/course-editor/ai/quality-levels')
      levels.value = response.data?.data?.levels ?? []
    } catch (err) {
      console.warn('[QualityLevel] Failed to load levels:', err)
      // Fallback defaults so the UI still works
      levels.value = [
        { level: 'schnell', label: 'Schnell', description: 'Schnelle Generierung', icon: 'zap', estimated_time: '~15-30s', token_ratio: 0.5, pipeline: false, methods_per_lesson: 1, retries: 0 },
        { level: 'standard', label: 'Standard', description: 'Ausgewogene Qualitaet', icon: 'star', estimated_time: '~30-60s', token_ratio: 0.75, pipeline: false, methods_per_lesson: 2, retries: 1 },
        { level: 'hoch', label: 'Hoch', description: 'Hochwertige Inhalte', icon: 'target', estimated_time: '~1-2min', token_ratio: 0.9, pipeline: true, methods_per_lesson: 2, retries: 1 },
        { level: 'maximum', label: 'Maximum', description: 'Maximale Qualitaet', icon: 'diamond', estimated_time: '~2-5min', token_ratio: 1.0, pipeline: true, methods_per_lesson: 3, retries: 2 },
      ]
    } finally {
      isLoading.value = false
    }
  }

  function setLevel(level: string): void {
    selectedLevel.value = level
  }

  return {
    levels,
    selectedLevel,
    currentLevel,
    selectionLabel,
    isLoading,
    loadQualityLevels,
    setLevel,
  }
}
