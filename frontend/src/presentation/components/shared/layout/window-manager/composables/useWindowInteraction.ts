/**
 * useWindowInteraction - Composable for window drag and resize behavior
 *
 * Extracted from WindowComponent.vue for Quality Gate G01 compliance.
 * Handles mouse-based drag and resize interactions for desktop-style windows.
 */

import { ref } from 'vue'
import type { Ref } from 'vue'

type ResizeDirection = 'n' | 'e' | 's' | 'w' | 'ne' | 'se' | 'sw' | 'nw'

interface WindowPosition {
  x: number
  y: number
}

interface WindowSize {
  width: number
  height: number
}

interface UseWindowInteractionOptions {
  windowRef: Ref<HTMLElement | null>
  windowId: Ref<string>
  windowPosition: Ref<WindowPosition>
  isMaximized: Ref<boolean>
  onFocus: (id: string) => void
  onDrag: (id: string, position: WindowPosition) => void
  onResize: (id: string, size: WindowSize) => void
}

interface DragState {
  startX: number
  startY: number
  offsetX: number
  offsetY: number
}

interface ResizeState {
  direction: ResizeDirection
  startX: number
  startY: number
  startWidth: number
  startHeight: number
  startPosX: number
  startPosY: number
}

export function useWindowInteraction(options: UseWindowInteractionOptions) {
  const { windowRef, windowId, windowPosition, isMaximized, onFocus, onDrag, onResize } = options

  const isDragging = ref(false)
  const isResizing = ref(false)
  const dragState = ref<DragState | null>(null)
  const resizeState = ref<ResizeState | null>(null)

  // ===========================================================================
  // Drag Handling
  // ===========================================================================

  /**
   * Start dragging window
   */
  function handleDragStart(e: MouseEvent): void {
    if (e.button !== 0) return
    if (isMaximized.value) return

    onFocus(windowId.value)

    const offsetX = e.clientX - windowPosition.value.x
    const offsetY = e.clientY - windowPosition.value.y

    dragState.value = {
      startX: e.clientX,
      startY: e.clientY,
      offsetX,
      offsetY
    }

    isDragging.value = true

    document.addEventListener('mousemove', handleDragMove)
    document.addEventListener('mouseup', handleDragEnd)

    e.preventDefault()
  }

  /**
   * Handle drag move
   */
  function handleDragMove(e: MouseEvent): void {
    if (!dragState.value) return

    let newX = e.clientX - dragState.value.offsetX
    let newY = e.clientY - dragState.value.offsetY

    // Constrain to viewport
    const maxX = window.innerWidth - 200
    const maxY = window.innerHeight - 50

    newX = Math.max(0, Math.min(newX, maxX))
    newY = Math.max(0, Math.min(newY, maxY))

    onDrag(windowId.value, { x: newX, y: newY })
  }

  /**
   * End dragging
   */
  function handleDragEnd(): void {
    isDragging.value = false
    dragState.value = null

    document.removeEventListener('mousemove', handleDragMove)
    document.removeEventListener('mouseup', handleDragEnd)
  }

  // ===========================================================================
  // Resize Handling
  // ===========================================================================

  /**
   * Start resizing window
   */
  function handleResizeStart(e: MouseEvent, direction: ResizeDirection): void {
    if (e.button !== 0) return
    if (isMaximized.value) return

    onFocus(windowId.value)

    const rect = windowRef.value?.getBoundingClientRect()
    if (!rect) return

    resizeState.value = {
      direction,
      startX: e.clientX,
      startY: e.clientY,
      startWidth: rect.width,
      startHeight: rect.height,
      startPosX: windowPosition.value.x,
      startPosY: windowPosition.value.y
    }

    isResizing.value = true

    document.addEventListener('mousemove', handleResizeMove)
    document.addEventListener('mouseup', handleResizeEnd)

    e.preventDefault()
    e.stopPropagation()
  }

  /**
   * Handle resize move
   */
  function handleResizeMove(e: MouseEvent): void {
    if (!resizeState.value) return

    const { direction, startX, startY, startWidth, startHeight, startPosX, startPosY } = resizeState.value
    const deltaX = e.clientX - startX
    const deltaY = e.clientY - startY

    let newWidth = startWidth
    let newHeight = startHeight
    let newX = startPosX
    let newY = startPosY

    // Handle horizontal resizing
    if (direction.includes('e')) {
      newWidth = startWidth + deltaX
    }
    if (direction.includes('w')) {
      newWidth = startWidth - deltaX
      newX = startPosX + deltaX
    }

    // Handle vertical resizing
    if (direction.includes('s')) {
      newHeight = startHeight + deltaY
    }
    if (direction.includes('n')) {
      newHeight = startHeight - deltaY
      newY = startPosY + deltaY
    }

    // Apply minimum size
    const minWidth = 400
    const minHeight = 300

    if (newWidth < minWidth) {
      if (direction.includes('w')) {
        newX = startPosX + startWidth - minWidth
      }
      newWidth = minWidth
    }

    if (newHeight < minHeight) {
      if (direction.includes('n')) {
        newY = startPosY + startHeight - minHeight
      }
      newHeight = minHeight
    }

    // Update position if needed (for n/w/nw/ne/sw resizing)
    if (direction.includes('n') || direction.includes('w')) {
      onDrag(windowId.value, { x: newX, y: newY })
    }

    onResize(windowId.value, { width: newWidth, height: newHeight })
  }

  /**
   * End resizing
   */
  function handleResizeEnd(): void {
    isResizing.value = false
    resizeState.value = null

    document.removeEventListener('mousemove', handleResizeMove)
    document.removeEventListener('mouseup', handleResizeEnd)
  }

  return {
    isDragging,
    isResizing,
    handleDragStart,
    handleResizeStart
  }
}
