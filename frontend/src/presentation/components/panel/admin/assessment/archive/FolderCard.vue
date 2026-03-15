<script setup lang="ts">
import type { ArchiveFolder } from '@/infrastructure/api/clients/panel/admin/exams/folders.api'

interface Props {
  folder: ArchiveFolder
  isDropTarget?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  open: [folderId: string]
  contextmenu: [event: MouseEvent, folder: ArchiveFolder]
  dragstart: [event: DragEvent, folder: ArchiveFolder]
  dragover: [event: DragEvent, folderId: string]
  dragleave: [event: DragEvent]
  drop: [event: DragEvent, folderId: string]
}>()
</script>

<template>
  <div
    class="bg-gray-800/80 border border-gray-700/50 rounded-xl p-4 text-center cursor-pointer
           transition-all hover:border-indigo-500/50 hover:bg-gray-800 hover:-translate-y-0.5 relative"
    :class="{ 'ring-2 ring-indigo-400 bg-indigo-500/10': isDropTarget }"
    draggable="true"
    @dblclick="emit('open', String(folder.folder_id))"
    @click="emit('open', String(folder.folder_id))"
    @contextmenu.prevent="emit('contextmenu', $event, folder)"
    @dragstart="emit('dragstart', $event, folder)"
    @dragover.prevent="emit('dragover', $event, String(folder.folder_id))"
    @dragleave="emit('dragleave', $event)"
    @drop="emit('drop', $event, String(folder.folder_id))"
  >
    <div class="text-4xl mb-2">{{ folder.icon || '📁' }}</div>
    <div class="text-sm font-medium truncate">{{ folder.name }}</div>
    <div class="text-[11px] text-gray-400 mt-0.5">
      {{ folder.child_count || 0 }} {{ folder.child_count === 1 ? 'Ordner' : 'Ordner' }}
      · {{ folder.file_count || 0 }} PDFs
    </div>
  </div>
</template>
