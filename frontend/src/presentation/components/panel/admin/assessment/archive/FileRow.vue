<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ArchiveFile } from '@/infrastructure/api/clients/panel/admin/exams/folders.api'

interface Props {
  file: ArchiveFile
}

const props = defineProps<Props>()

const emit = defineEmits<{
  open: [examId: string]
  contextmenu: [event: MouseEvent, file: ArchiveFile]
  dragstart: [event: DragEvent, file: ArchiveFile]
}>()

const { t } = useI18n()

const statusClass = computed(() => {
  switch (props.file.analysis_status) {
    case 'ready': return 'bg-green-500/15 text-green-400'
    case 'analyzing': return 'bg-yellow-500/15 text-yellow-400'
    case 'failed': return 'bg-red-500/15 text-red-400'
    default: return 'bg-indigo-500/15 text-indigo-300'
  }
})

const statusLabel = computed(() => {
  const key = `panel.examArchive.status.${props.file.analysis_status}`
  return t(key)
})

const detail = computed(() => {
  const parts: string[] = []
  if (props.file.year) parts.push(`${props.file.season || ''} ${props.file.year}`.trim())
  if (props.file.question_count > 0) parts.push(`${props.file.question_count} Fragen`)
  return parts.join(' · ')
})
</script>

<template>
  <div
    class="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors
           hover:bg-gray-800/80 group"
    draggable="true"
    @click="emit('open', String(file.exam_id))"
    @contextmenu.prevent="emit('contextmenu', $event, file)"
    @dragstart="emit('dragstart', $event, file)"
  >
    <span class="text-xl shrink-0">📄</span>
    <div class="flex-1 min-w-0">
      <div class="text-sm font-medium truncate">{{ file.title || file.pdf_path || 'Untitled' }}</div>
      <div class="text-[11px] text-gray-400">{{ detail }}</div>
    </div>
    <span
      class="text-[11px] px-2 py-0.5 rounded-full shrink-0"
      :class="statusClass"
    >
      {{ statusLabel }}
    </span>
    <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
      <button
        class="w-7 h-7 flex items-center justify-center rounded-md bg-gray-700/50 text-gray-300
               hover:text-white hover:bg-gray-600 text-xs"
        title="Download"
        @click.stop
      >⬇</button>
      <button
        class="w-7 h-7 flex items-center justify-center rounded-md bg-gray-700/50 text-gray-300
               hover:text-white hover:bg-gray-600 text-xs"
        title="More"
        @click.stop="emit('contextmenu', $event as MouseEvent, file)"
      >⋯</button>
    </div>
  </div>
</template>
