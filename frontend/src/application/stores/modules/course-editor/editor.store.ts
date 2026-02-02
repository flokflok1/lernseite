/**
 * editor.store.ts
 *
 * Main editor state management for course editing.
 * Handles overall editor state, mode switching, and project management.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface EditorState {
  currentProjectId: string | null
  currentMode: 'manual' | 'ai'
  isDirty: boolean
  isSaving: boolean
  error: string | null
}

export const useEditorStore = defineStore('courseEditor/editor', () => {
  // State
  const currentProjectId = ref<string | null>(null)
  const currentMode = ref<'manual' | 'ai'>('manual')
  const isDirty = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const hasChanges = computed(() => isDirty.value)
  const isLoading = computed(() => isSaving.value)

  // Actions
  const setProject = (projectId: string) => {
    currentProjectId.value = projectId
  }

  const switchMode = (mode: 'manual' | 'ai') => {
    currentMode.value = mode
  }

  const markDirty = () => {
    isDirty.value = true
  }

  const markClean = () => {
    isDirty.value = false
  }

  const setSaving = (saving: boolean) => {
    isSaving.value = saving
  }

  const setError = (err: string | null) => {
    error.value = err
  }

  const save = async () => {
    if (!currentProjectId.value) {
      setError('No project selected')
      return
    }

    isSaving.value = true
    error.value = null

    try {
      // TODO: Call API to save project
      console.log(`Saving project ${currentProjectId.value}`)
      isDirty.value = false
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Save failed'
    } finally {
      isSaving.value = false
    }
  }

  const reset = () => {
    currentProjectId.value = null
    currentMode.value = 'manual'
    isDirty.value = false
    isSaving.value = false
    error.value = null
  }

  return {
    currentProjectId,
    currentMode,
    isDirty,
    isSaving,
    error,
    hasChanges,
    isLoading,
    setProject,
    switchMode,
    markDirty,
    markClean,
    setSaving,
    setError,
    save,
    reset
  }
})
