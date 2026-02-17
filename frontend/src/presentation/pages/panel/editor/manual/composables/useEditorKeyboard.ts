/**
 * useEditorKeyboard - Keyboard shortcuts for the editor
 *
 * Registers Ctrl+S (save) and Ctrl+Shift+P (toggle preview)
 * on mount, removes listeners on unmount.
 */

import { onMounted, onUnmounted } from 'vue'

interface KeyboardCallbacks {
  onSave: () => void
  onTogglePreview?: () => void
}

export function useEditorKeyboard(callbacks: KeyboardCallbacks) {
  const handleKeyDown = (e: KeyboardEvent): void => {
    const isMod = e.ctrlKey || e.metaKey

    // Ctrl+S / Cmd+S → Save
    if (isMod && e.key === 's') {
      e.preventDefault()
      callbacks.onSave()
      return
    }

    // Ctrl+Shift+P → Toggle preview
    if (isMod && e.shiftKey && e.key === 'P') {
      e.preventDefault()
      callbacks.onTogglePreview?.()
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeyDown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyDown)
  })
}
