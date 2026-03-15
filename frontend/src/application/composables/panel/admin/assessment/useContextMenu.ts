/**
 * Context menu composable for the Exam Archive File Explorer.
 *
 * Manages visibility, positioning (viewport-clamped), and target tracking
 * for right-click context menus on folders, files, and background areas.
 */

import { ref, onMounted, onUnmounted } from 'vue'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ContextMenuTarget {
  type: 'folder' | 'file' | 'background'
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

  function show(event: MouseEvent, menuTarget: ContextMenuTarget) {
    event.preventDefault()
    const x = Math.min(event.clientX, window.innerWidth - MENU_WIDTH - CLAMP_MARGIN)
    const y = Math.min(event.clientY, window.innerHeight - MENU_HEIGHT - CLAMP_MARGIN)
    position.value = { x: Math.max(0, x), y: Math.max(0, y) }
    target.value = menuTarget
    visible.value = true
  }

  function hide() {
    visible.value = false
    target.value = null
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') hide()
  }

  onMounted(() => {
    document.addEventListener('click', hide)
    document.addEventListener('keydown', onKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('click', hide)
    document.removeEventListener('keydown', onKeydown)
  })

  return { visible, position, target, show, hide }
}
