/**
 * Drag-and-drop composable for the Exam Archive File Explorer.
 *
 * Tracks the currently dragged item (folder or file) and the
 * drop-target folder, then invokes a callback on successful drop.
 */

import { ref, computed } from 'vue'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface DragItem {
  type: 'folder' | 'file'
  id: string
}

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

export function useDragDrop(
  onDrop: (item: DragItem, targetFolderId: string) => void,
) {
  const dragItem = ref<DragItem | null>(null)
  const dropTargetId = ref<string | null>(null)
  const isDragging = computed(() => dragItem.value !== null)

  function onDragStart(event: DragEvent, type: 'folder' | 'file', id: string) {
    dragItem.value = { type, id }
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move'
      event.dataTransfer.setData('text/plain', JSON.stringify({ type, id }))
    }
  }

  function onDragOver(event: DragEvent, targetFolderId: string) {
    event.preventDefault()
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'move'
    }
    // Prevent dropping a folder onto itself
    if (dragItem.value?.type === 'folder' && dragItem.value.id === targetFolderId) {
      return
    }
    dropTargetId.value = targetFolderId
  }

  function onDragLeave() {
    dropTargetId.value = null
  }

  function handleDrop(event: DragEvent, targetFolderId: string) {
    event.preventDefault()
    dropTargetId.value = null
    const item = dragItem.value
    if (item && item.id !== targetFolderId) {
      onDrop(item, targetFolderId)
    }
    dragItem.value = null
  }

  function onDragEnd() {
    dragItem.value = null
    dropTargetId.value = null
  }

  return {
    dragItem,
    dropTargetId,
    isDragging,
    onDragStart,
    onDragOver,
    onDragLeave,
    handleDrop,
    onDragEnd,
  }
}
