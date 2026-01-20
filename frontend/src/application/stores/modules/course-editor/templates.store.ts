/**
 * templates.store.ts
 *
 * Templates state management.
 * Manages AI content generation templates.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Template {
  id: string
  name: string
  description: string
  category: string
  prompt: string
}

export const useTemplatesStore = defineStore('courseEditor/templates', () => {
  const templates = ref<Template[]>([])
  const isLoading = ref(false)

  const loadTemplates = async () => {
    isLoading.value = true
    try {
      // TODO: Load from API
    } finally {
      isLoading.value = false
    }
  }

  const getTemplatesByCategory = (category: string) => {
    return templates.value.filter(t => t.category === category)
  }

  return {
    templates,
    isLoading,
    loadTemplates,
    getTemplatesByCategory
  }
})
