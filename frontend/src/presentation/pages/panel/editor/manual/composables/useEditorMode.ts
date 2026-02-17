/**
 * useEditorMode - Manages editor mode (beginner/advanced/expert)
 *
 * Persists mode selection in localStorage. Returns reactive mode state
 * and a computed feature config that controls which panels are visible.
 */

import { ref, computed, onMounted } from 'vue'
import type { EditorMode, EditorModeConfig } from '../types'
import { EDITOR_MODE_CONFIGS } from '../types'

const STORAGE_KEY = 'lsx-editor-mode'

export function useEditorMode() {
  const currentMode = ref<EditorMode>('beginner')

  const modeConfig = computed<EditorModeConfig>(() => {
    return EDITOR_MODE_CONFIGS[currentMode.value]
  })

  const setMode = (mode: EditorMode): void => {
    currentMode.value = mode
    try {
      localStorage.setItem(STORAGE_KEY, mode)
    } catch {
      // localStorage not available (SSR, private browsing)
    }
  }

  const isFeatureVisible = (feature: keyof EditorModeConfig): boolean => {
    return modeConfig.value[feature]
  }

  onMounted(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as EditorMode | null
      if (stored && stored in EDITOR_MODE_CONFIGS) {
        currentMode.value = stored
      }
    } catch {
      // localStorage not available
    }
  })

  return {
    currentMode,
    modeConfig,
    setMode,
    isFeatureVisible,
  }
}
