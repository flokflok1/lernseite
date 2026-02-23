/**
 * useGenerationHistory — Generation history tracking with rollback
 */
import { ref, computed } from 'vue'
import type { GenerationHistoryEntry } from '../types'
import { getGenerationHistory } from '@/infrastructure/api/clients/panel/editor/unified/unified.api'

export function useGenerationHistory() {
  const entries = ref<GenerationHistoryEntry[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const filterSkill = ref<string | null>(null)

  const filteredEntries = computed(() => {
    if (!filterSkill.value) return entries.value
    return entries.value.filter(e => e.skill_code === filterSkill.value)
  })

  const totalTokens = computed(() =>
    entries.value.reduce((sum, e) => sum + (e.tokens_input || 0) + (e.tokens_output || 0), 0),
  )

  const uniqueSkills = computed(() =>
    [...new Set(entries.value.map(e => e.skill_code))],
  )

  async function loadHistory(courseId: string, limit = 50, offset = 0) {
    isLoading.value = true
    error.value = null
    try {
      entries.value = await getGenerationHistory(courseId, limit, offset)
    } catch (e: any) {
      error.value = e.response?.data?.error?.message || e.message
    } finally {
      isLoading.value = false
    }
  }

  function setFilter(skillCode: string | null) {
    filterSkill.value = skillCode
  }

  function addEntry(entry: GenerationHistoryEntry) {
    entries.value.unshift(entry)
  }

  function clearHistory() {
    entries.value = []
    filterSkill.value = null
  }

  return {
    entries,
    isLoading,
    error,
    filterSkill,
    filteredEntries,
    totalTokens,
    uniqueSkills,
    loadHistory,
    setFilter,
    addEntry,
    clearHistory,
  }
}
