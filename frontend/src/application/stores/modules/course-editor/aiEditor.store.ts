/**
 * aiEditor.store.ts
 *
 * AI Editor state management.
 * Handles AI generation state, settings, and AI-specific editor features.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface AIEditorState {
  isGenerating: boolean
  generationProgress: number
  generatedContent: string | null
  aiSettings: Record<string, unknown>
  error: string | null
}

export const useAIEditorStore = defineStore('courseEditor/aiEditor', () => {
  const isGenerating = ref(false)
  const generationProgress = ref(0)
  const generatedContent = ref<string | null>(null)
  const aiSettings = ref<Record<string, unknown>>({
    temperature: 0.7,
    maxTokens: 2000,
    model: 'default'
  })
  const error = ref<string | null>(null)

  const startGeneration = () => {
    isGenerating.value = true
    generationProgress.value = 0
  }

  const updateProgress = (progress: number) => {
    generationProgress.value = Math.min(100, progress)
  }

  const finishGeneration = (content: string) => {
    generatedContent.value = content
    isGenerating.value = false
    generationProgress.value = 100
  }

  const updateSettings = (settings: Partial<typeof aiSettings.value>) => {
    aiSettings.value = { ...aiSettings.value, ...settings }
  }

  return {
    isGenerating,
    generationProgress,
    generatedContent,
    aiSettings,
    error,
    startGeneration,
    updateProgress,
    finishGeneration,
    updateSettings
  }
})
