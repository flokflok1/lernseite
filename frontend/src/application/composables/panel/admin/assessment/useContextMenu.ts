/**
 * Context menu composable for the Exam Archive File Explorer.
 *
 * Manages visibility, positioning (viewport-clamped), and target tracking
 * for right-click context menus on folders, files, and background areas.
 */

import { ref, onMounted, onUnmounted, nextTick } from 'vue'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ContextMenuTarget {
  type: 'folder' | 'file' | 'background' | 'program'
  id: string | null
  data: unknown
}

// ---------------------------------------------------------------------------
// Constants (approximate context menu dimensions for clamping)
// ---------------------------------------------------------------------------

const MENU_WIDTH = 220
const MENU_HEIGHT = 350
const CLAMP_MARGIN = 10

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

export function useContextMenu() {
  const visible = ref(false)
  const position = ref({ x: 0, y: 0 })
  const target = ref<ContextMenuTarget | null>(null)

  let justOpened = false

  function show(event: MouseEvent, menuTarget: ContextMenuTarget) {
    event.preventDefault()
    event.stopPropagation()
    const x = Math.min(event.clientX, window.innerWidth - MENU_WIDTH - CLAMP_MARGIN)
    const y = Math.min(event.clientY, window.innerHeight - MENU_HEIGHT - CLAMP_MARGIN)
    position.value = { x: Math.max(0, x), y: Math.max(0, y) }
    target.value = menuTarget
    visible.value = true
    // Prevent the click-outside handler from immediately closing
    justOpened = true
    nextTick(() => { justOpened = false })
  }

  function hide() {
    if (justOpened) return
    visible.value = false
    target.value = null
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      visible.value = false
      target.value = null
    }
  }

  function onClickOutside(e: MouseEvent) {
    if (justOpened) return
    // Don't hide if clicking inside the context menu itself
    const el = e.target as HTMLElement
    if (el.closest('[data-context-menu]')) return
    hide()
  }

  onMounted(() => {
    document.addEventListener('mousedown', onClickOutside)
    document.addEventListener('keydown', onKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('mousedown', onClickOutside)
    document.removeEventListener('keydown', onKeydown)
  })

  return { visible, position, target, show, hide }
}
